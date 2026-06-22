import os
import re
import markdown
from image_handler import resolve_images
from math_handler import extract_and_render_math, math_to_text
from diagram_handler import extract_and_render_diagrams, diagrams_to_code_block

DEFAULT_CSS_PATH = os.path.join(os.path.dirname(__file__), 'styles', 'default.css')


def md_to_html(md_text, md_file_dir=None, cache_dir=None, render_math=True, render_diagrams=True):
    if md_file_dir is None:
        md_file_dir = os.getcwd()
    if cache_dir is None:
        cache_dir = os.path.join(md_file_dir, '.md_converter_cache')

    md_text = _preprocess_md(md_text)

    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
    ]

    extension_configs = {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': False,
        },
        'markdown.extensions.toc': {
            'permalink': False,
        },
    }

    md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
    body_html = md.convert(md_text)

    body_html = re.sub(r'<a[^>]*class="headerlink"[^>]*>¶</a>', '', body_html)

    body_html = resolve_images(body_html, md_file_dir)

    if render_diagrams:
        body_html = extract_and_render_diagrams(body_html, cache_dir)
    else:
        body_html = diagrams_to_code_block(body_html)

    if render_math:
        body_html = extract_and_render_math(body_html, cache_dir)
    else:
        body_html = math_to_text(body_html)

    css = _load_css()

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
{css}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
    return html


def _preprocess_md(md_text):
    return md_text


def _load_css():
    if os.path.isfile(DEFAULT_CSS_PATH):
        with open(DEFAULT_CSS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def md_file_to_html(md_path, render_math=True, render_diagrams=True):
    md_file_dir = os.path.dirname(os.path.abspath(md_path))
    cache_dir = os.path.join(md_file_dir, '.md_converter_cache')
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    return md_to_html(md_text, md_file_dir, cache_dir, render_math, render_diagrams)
