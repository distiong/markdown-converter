import re
import os
import subprocess
import tempfile
import hashlib

MERMAID_PATTERN = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL)


def extract_and_render_diagrams(html_content, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    counter = [0]

    def replace_diagram(match):
        code = match.group(1).strip()
        img_path = _render_mermaid(code, cache_dir, counter)
        if img_path:
            return f'<div class="diagram-img"><img src="file:///{img_path}" alt="Mermaid Diagram"></div>'
        return f'<pre><code>{_escape_html(code)}</code></pre>'

    html_content = MERMAID_PATTERN.sub(replace_diagram, html_content)
    return html_content


def _render_mermaid(code, cache_dir, counter):
    key = hashlib.md5(code.encode()).hexdigest()
    img_path = os.path.join(cache_dir, f"diagram_{key}.png")
    if os.path.exists(img_path):
        return img_path

    mmd_path = os.path.join(cache_dir, f"diagram_{counter[0]}.mmd")
    counter[0] += 1
    with open(mmd_path, 'w', encoding='utf-8') as f:
        f.write(code)

    try:
        subprocess.run(
            ['mmdc', '-i', mmd_path, '-o', img_path, '-b', 'white', '-w', '1200'],
            capture_output=True, timeout=30, check=True
        )
        if os.path.exists(img_path):
            return img_path
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        subprocess.run(
            ['npx', '-y', '@mermaid-js/mermaid-cli', '-i', mmd_path, '-o', img_path, '-b', 'white'],
            capture_output=True, timeout=60, check=True
        )
        if os.path.exists(img_path):
            return img_path
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def diagrams_to_code_block(html_content):
    return MERMAID_PATTERN.sub(
        lambda m: f'<pre><code class="language-mermaid">{_escape_html(m.group(1).strip())}</code></pre>',
        html_content
    )


def extract_diagrams_from_markdown(md_text):
    return MERMAID_PATTERN.findall(md_text)


def _escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
