import PyInstaller.__main__
import os

work_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=MarkdownConverter',
    '--onefile',
    '--noconsole',
    '--add-data=templates;templates',
    '--add-data=styles;styles',
    '--hidden-import=flask',
    '--hidden-import=markdown',
    '--hidden-import=reportlab',
    '--hidden-import=docx',
    '--hidden-import=PIL',
    '--hidden-import=xhtml2pdf',
    '--hidden-import=pdfkit',
    '--hidden-import=pygments',
    f'--distpath={os.path.join(work_dir, "dist")}',
    f'--workpath={os.path.join(work_dir, "build")}',
    f'--specpath={work_dir}',
])
