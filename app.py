import os
import sys
import json
import uuid
import shutil
import tempfile
import threading
import urllib.parse
import ctypes
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from converter import convert_file, convert_directory
from pdf_writer import check_wkhtmltopdf
from html_generator import md_file_to_html


def _resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


app = Flask(
    __name__,
    template_folder=_resource_path('templates'),
    static_folder=_resource_path('static'),
)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), 'md_converter_uploads')
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'md_converter_output')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

conversion_tasks = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/check-deps')
def check_deps():
    return jsonify({
        'wkhtmltopdf': check_wkhtmltopdf()
    })


@app.route('/api/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    uploaded = []
    task_id = str(uuid.uuid4())[:8]
    task_dir = os.path.join(UPLOAD_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    for f in files:
        if f.filename and f.filename.lower().endswith('.md'):
            filepath = os.path.join(task_dir, f.filename)
            f.save(filepath)
            uploaded.append({
                'name': f.filename,
                'path': filepath,
                'size': os.path.getsize(filepath)
            })

    conversion_tasks[task_id] = {
        'files': uploaded,
        'task_dir': task_dir,
        'status': 'uploaded'
    }

    return jsonify({
        'task_id': task_id,
        'files': [{'name': u['name'], 'size': u['size'], 'path': u['path']} for u in uploaded]
    })


@app.route('/api/preview', methods=['POST'])
def preview():
    data = request.json
    task_id = data.get('task_id')
    file_index = data.get('file_index', 0)

    if not task_id or task_id not in conversion_tasks:
        return jsonify({'error': 'Invalid task'}), 400

    task = conversion_tasks[task_id]
    if file_index >= len(task['files']):
        return jsonify({'error': 'File index out of range'}), 400

    filepath = task['files'][file_index]['path']
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        html = md_file_to_html(filepath)
        return jsonify({
            'markdown': content,
            'html': html
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.json
    task_id = data.get('task_id')
    formats = data.get('formats', ['pdf', 'docx'])

    if not task_id or task_id not in conversion_tasks:
        return jsonify({'error': 'Invalid task'}), 400

    task = conversion_tasks[task_id]
    output_dir = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(output_dir, exist_ok=True)

    results = []
    errors = []
    total = len(task['files'])

    for i, file_info in enumerate(task['files']):
        filepath = file_info['path']
        try:
            conv_results = convert_file(filepath, output_dir, formats)
            for fmt, ok, msg in conv_results:
                if ok:
                    results.append({
                        'file': file_info['name'],
                        'format': fmt,
                        'path': msg,
                        'download': f'/api/download/{task_id}/{os.path.basename(msg)}'
                    })
                else:
                    errors.append(f"{file_info['name']} ({fmt}): {msg}")
        except Exception as e:
            errors.append(f"{file_info['name']}: {str(e)}")

    return jsonify({
        'results': results,
        'errors': errors,
        'total': total,
        'success': len(results)
    })


@app.route('/api/download/<task_id>/<filename>')
def download(task_id, filename):
    output_dir = os.path.join(OUTPUT_DIR, task_id)
    filepath = os.path.join(output_dir, filename)
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)


@app.route('/api/download-all/<task_id>')
def download_all(task_id):
    output_dir = os.path.join(OUTPUT_DIR, task_id)
    if not os.path.isdir(output_dir):
        return jsonify({'error': 'No output found'}), 404

    zip_path = os.path.join(tempfile.gettempdir(), f'md_converter_{task_id}.zip')
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
    return send_file(zip_path, as_attachment=True, download_name=f'converted_{task_id}.zip')


@app.route('/api/download-file/<path:filepath>')
def download_file_by_path(filepath):
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)


@app.route('/api/convert-folder', methods=['POST'])
def convert_folder():
    data = request.json
    folder_path = data.get('folder_path')
    formats = data.get('formats', ['pdf', 'docx'])
    output_dir_name = data.get('output_dir')

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': 'Invalid folder path'}), 400

    task_id = str(uuid.uuid4())[:8]
    if output_dir_name:
        output_dir = os.path.join(folder_path, output_dir_name)
    else:
        output_dir = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(output_dir, exist_ok=True)

    results = []
    errors = []
    md_files = []

    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith('.md'):
                md_files.append(os.path.join(root, f))

    total = len(md_files)
    for md_path in md_files:
        try:
            conv_results = convert_file(md_path, output_dir, formats)
            for fmt, ok, msg in conv_results:
                if ok:
                    results.append({
                        'file': os.path.basename(md_path),
                        'format': fmt,
                        'path': msg,
                        'download': f'/api/download-file/{urllib.parse.quote(msg, safe="")}'
                    })
                else:
                    errors.append(f"{os.path.basename(md_path)} ({fmt}): {msg}")
        except Exception as e:
            errors.append(f"{os.path.basename(md_path)}: {str(e)}")

    return jsonify({
        'results': results,
        'errors': errors,
        'total': total,
        'success': len(results),
        'output_dir': output_dir
    })


@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    import signal
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    else:
        threading.Thread(target=lambda: (os._exit(0))).start()
    return jsonify({'status': 'shutting down'})


def create_templates():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    return templates_dir


if __name__ == '__main__':
    templates_dir = create_templates()
    print(f"Templates dir: {templates_dir}")
    print("Starting Markdown Converter on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
