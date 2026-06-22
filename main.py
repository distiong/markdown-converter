import sys
import os


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, create_templates
import webbrowser
import threading


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    templates_dir = get_resource_path('templates')
    os.makedirs(templates_dir, exist_ok=True)

    print("=" * 60)
    print("  Markdown Converter")
    print("  Open http://localhost:5000 in your browser")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
