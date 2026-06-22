import os
import re
import base64
import urllib.request
import tempfile
from pathlib import Path


def resolve_images(html_content, md_file_dir):
    img_pattern = re.compile(r'<img\s+[^>]*src="([^"]+)"', re.IGNORECASE)

    def replace_img(match):
        src = match.group(1)
        if src.startswith('data:'):
            return match.group(0)
        if src.startswith('http://') or src.startswith('https://'):
            return _embed_remote_image(match.group(0), src)
        local_path = os.path.normpath(os.path.join(md_file_dir, src))
        if os.path.isfile(local_path):
            return _embed_local_image(match.group(0), local_path)
        return match.group(0)

    return img_pattern.sub(replace_img, html_content)


def _embed_local_image(img_tag, file_path):
    ext = Path(file_path).suffix.lower().lstrip('.')
    mime_map = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'gif': 'image/gif', 'svg': 'image/svg+xml', 'webp': 'image/webp',
                'bmp': 'image/bmp'}
    mime = mime_map.get(ext, 'image/png')
    with open(file_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    return img_tag.replace(f'"{os.path.basename(file_path)}"', f"data:{mime};base64,{b64}")


def _embed_remote_image(img_tag, url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            content_type = resp.headers.get('Content-Type', 'image/png').split(';')[0]
            b64 = base64.b64encode(data).decode('utf-8')
            original_src = re.search(r'src="([^"]+)"', img_tag).group(1)
            return img_tag.replace(f'"{original_src}"', f"data:{content_type};base64,{b64}")
    except Exception:
        return img_tag


def save_images_for_docx(images, output_dir):
    saved = []
    os.makedirs(output_dir, exist_ok=True)
    for i, (src, alt) in enumerate(images):
        if src.startswith('data:'):
            continue
        if src.startswith('http://') or src.startswith('https://'):
            try:
                req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                    ext = Path(src.split('?')[0]).suffix or '.png'
                    fname = f"img_{i}{ext}"
                    fpath = os.path.join(output_dir, fname)
                    with open(fpath, 'wb') as f:
                        f.write(data)
                    saved.append((fpath, alt))
            except Exception:
                pass
        else:
            full = os.path.normpath(os.path.join(output_dir, '..', src))
            if os.path.isfile(full):
                saved.append((full, alt))
    return saved
