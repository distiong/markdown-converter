import PyInstaller.__main__
import os
import sys

work_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.dirname(sys.executable)
dlls_dir = os.path.join(python_dir, 'DLLs')

PyInstaller.__main__.run([
    'main.py',
    '--name=MarkdownConverter',
    '--onefile',
    '--noconsole',
    '--add-data=templates;templates',
    '--add-data=styles;styles',
    f'--add-binary={dlls_dir}{os.pathsep}.',
    '--hidden-import=flask',
    '--hidden-import=markdown',
    '--hidden-import=reportlab',
    '--hidden-import=docx',
    '--hidden-import=PIL',
    '--hidden-import=xhtml2pdf',
    '--hidden-import=pdfkit',
    '--hidden-import=pygments',
    '--hidden-import=ctypes',
    '--hidden-import=_ctypes',
    '--hidden-import=markupsafe',
    '--hidden-import=jinja2',
    '--hidden-import=werkzeug',
    '--collect-all=flask',
    '--collect-all=markdown',
    '--collect-all=reportlab',
    f'--distpath={os.path.join(work_dir, "dist")}',
    f'--workpath={os.path.join(work_dir, "build")}',
    f'--specpath={work_dir}',
])
