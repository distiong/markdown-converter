import re
import os
import hashlib
import subprocess
import tempfile
from pathlib import Path

MATH_PATTERN_BLOCK = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
MATH_PATTERN_INLINE = re.compile(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)')


def extract_and_render_math(html_content, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    counter = [0]

    def render_block(match):
        latex = match.group(1).strip()
        img_path = _render_latex(latex, cache_dir, counter, display=True)
        if img_path:
            return f'<div class="math-block"><img src="file:///{img_path}" alt="{_escape_html(latex)}"></div>'
        return f'<div class="math-block"><i>{_escape_html(latex)}</i></div>'

    def render_inline(match):
        latex = match.group(1).strip()
        img_path = _render_latex(latex, cache_dir, counter, display=False)
        if img_path:
            return f'<img src="file:///{img_path}" alt="{_escape_html(latex)}" style="vertical-align:middle; height:1.2em;">'
        return f'<i>{_escape_html(latex)}</i>'

    html_content = MATH_PATTERN_BLOCK.sub(render_block, html_content)
    html_content = MATH_PATTERN_INLINE.sub(render_inline, html_content)
    return html_content


def _render_latex(latex, cache_dir, counter, display=False):
    key = hashlib.md5((latex + str(display)).encode()).hexdigest()
    img_path = os.path.join(cache_dir, f"math_{key}.png")
    if os.path.exists(img_path):
        return img_path

    tex = r"""
\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage[utf8]{inputenc}
\usepackage{ctex}
\begin{document}
"""
    if display:
        tex += f"$${latex}$$"
    else:
        tex += f"${latex}$"
    tex += r"""
\end{document}
"""
    tex_path = os.path.join(cache_dir, f"math_{counter[0]}.tex")
    counter[0] += 1
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex)

    try:
        subprocess.run(
            ['pdflatex', '-output-directory', cache_dir, tex_path],
            capture_output=True, timeout=10, check=True
        )
        pdf_path = tex_path.replace('.tex', '.pdf')
        if os.path.exists(pdf_path):
            try:
                import fitz
                doc = fitz.open(pdf_path)
                page = doc[0]
                pix = page.get_pixmap(dpi=200)
                pix.save(img_path)
                doc.close()
                return img_path
            except ImportError:
                pass
        return None
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def math_to_text(html_content):
    html_content = MATH_PATTERN_BLOCK.sub(
        lambda m: f'<div class="math-block"><i>[Math: {_escape_html(m.group(1).strip())}]</i></div>',
        html_content
    )
    html_content = MATH_PATTERN_INLINE.sub(
        lambda m: f'<i>[{_escape_html(m.group(1).strip())}]</i>',
        html_content
    )
    return html_content


def math_to_docx_paragraph(doc, paragraph, text):
    parts = re.split(r'(\$\$.*?\$\$|\$(?!\$).*?\$(?!\$))', text)
    for part in parts:
        if part.startswith('$$') and part.endswith('$$'):
            latex = part[2:-2].strip()
            run = paragraph.add_run(f'[Math: {latex}]')
            run.italic = True
            run.font.size = doc.styles['Normal'].font.size
        elif part.startswith('$') and part.endswith('$') and len(part) > 2:
            latex = part[1:-1].strip()
            run = paragraph.add_run(f'[{latex}]')
            run.italic = True
            run.font.size = doc.styles['Normal'].font.size
        else:
            paragraph.add_run(part)
