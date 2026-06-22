import os
import sys
import webbrowser
import threading
from app import app, create_templates


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    create_templates()
    print("=" * 60)
    print("  Markdown Converter - Web Interface")
    print("  ")
    print("  Open http://localhost:5000 in your browser")
    print("  ")
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
