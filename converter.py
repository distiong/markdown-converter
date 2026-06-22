import os
import tempfile
import shutil
from html_generator import md_file_to_html, md_to_html
from pdf_writer import html_to_pdf, check_wkhtmltopdf
from docx_writer import html_to_docx


def convert_file(md_path, output_dir, formats=('pdf', 'docx'), callback=None):
    md_path = os.path.abspath(md_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(md_path))[0]
    md_file_dir = os.path.dirname(md_path)

    if callback:
        callback(f'Reading {os.path.basename(md_path)}...')

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    cache_dir = os.path.join(tempfile.gettempdir(), 'md_converter_cache')
    os.makedirs(cache_dir, exist_ok=True)

    results = []

    if 'pdf' in formats:
        try:
            if callback:
                callback(f'Generating PDF for {base_name}...')
            html = md_to_html(md_text, md_file_dir, cache_dir)
            pdf_path = os.path.join(output_dir, f'{base_name}.pdf')
            html_to_pdf(html, pdf_path)
            results.append(('pdf', True, pdf_path))
            if callback:
                callback(f'PDF saved: {pdf_path}')
        except Exception as e:
            results.append(('pdf', False, str(e)))
            if callback:
                callback(f'PDF error: {e}')

    if 'docx' in formats:
        try:
            if callback:
                callback(f'Generating Word for {base_name}...')
            docx_path = os.path.join(output_dir, f'{base_name}.docx')
            html_to_docx(md_text, docx_path, md_file_dir)
            results.append(('docx', True, docx_path))
            if callback:
                callback(f'Word saved: {docx_path}')
        except Exception as e:
            results.append(('docx', False, str(e)))
            if callback:
                callback(f'Word error: {e}')

    return results


def convert_directory(dir_path, output_dir, formats=('pdf', 'docx'), callback=None):
    dir_path = os.path.abspath(dir_path)
    md_files = []
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith('.md'):
                md_files.append(os.path.join(root, f))

    if callback:
        callback(f'Found {len(md_files)} Markdown files')

    all_results = []
    for i, md_file in enumerate(md_files):
        if callback:
            callback(f'[{i+1}/{len(md_files)}] Converting {os.path.relpath(md_file, dir_path)}...')
        results = convert_file(md_file, output_dir, formats)
        all_results.append((md_file, results))

    return all_results
