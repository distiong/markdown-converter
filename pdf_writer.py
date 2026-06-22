import os
import re
import markdown
from html.parser import HTMLParser


def check_wkhtmltopdf():
    try:
        import subprocess
        result = subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


def html_to_pdf(html_content_or_path, output_path, options=None):
    if check_wkhtmltopdf():
        return _html_to_pdf_wkhtmltopdf(html_content_or_path, output_path, options)
    else:
        return _html_to_pdf_reportlab(html_content_or_path, output_path)


def _html_to_pdf_wkhtmltopdf(html_content_or_path, output_path, options=None):
    import pdfkit
    default_options = {
        'encoding': 'UTF-8',
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'enable-local-file-access': '',
        'no-stop-slow-scripts': '',
        'quiet': '',
    }
    if options:
        default_options.update(options)

    if os.path.isfile(html_content_or_path):
        pdfkit.from_file(html_content_or_path, output_path, options=default_options)
    else:
        pdfkit.from_string(html_content_or_path, output_path, options=default_options)


def _html_to_pdf_reportlab(html_content_or_path, output_path):
    if os.path.isfile(html_content_or_path):
        with open(html_content_or_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        html_content = html_content_or_path

    parser = _HTMLToReportLab()
    parser.feed(html_content)
    flowables = parser.get_flowables()

    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, KeepInFrame
    from reportlab.lib.units import cm

    page_width, page_height = A4
    content_width = page_width - 4 * cm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    processed = _post_process_flowables(flowables, content_width)
    doc.build(processed)


def _post_process_flowables(flowables, content_width):
    from reportlab.platypus import KeepTogether, Spacer, Table, Image, Paragraph, Preformatted, Flowable

    result = []
    group = []

    for f in flowables:
        f_type = type(f).__name__

        if f_type == 'Table':
            if group:
                result.append(KeepTogether(group))
                group = []
            _resize_table(f, content_width)
            result.append(KeepTogether([f]))

        elif f_type == 'Image':
            if group:
                result.append(KeepTogether(group))
                group = []
            _resize_image(f, content_width)
            result.append(f)

        elif f_type in ('Paragraph', 'Preformatted'):
            style = getattr(f, 'style', None)
            style_name = getattr(style, 'name', '') if style else ''

            if 'Heading' in style_name:
                if group:
                    result.append(KeepTogether(group))
                    group = []
                result.append(f)
                result.append(Spacer(1, 2))
            else:
                group.append(f)

        elif f_type == 'HRFlowable':
            if group:
                result.append(KeepTogether(group))
                group = []
            result.append(f)

        else:
            group.append(f)

    if group:
        result.append(KeepTogether(group))

    return result


def _resize_image(img, content_width):
    if hasattr(img, 'imageWidth') and img.imageWidth:
        if img.imageWidth > content_width:
            ratio = content_width / img.imageWidth
            img.imageWidth = content_width
            img.imageHeight = img.imageHeight * ratio


def _resize_table(table, content_width):
    if hasattr(table, '_colWidths') and table._colWidths:
        total = sum(table._colWidths)
        if total > content_width:
            ratio = content_width / total
            table._colWidths = [w * ratio for w in table._colWidths]


def _get_font_name(bold=False, italic=False):
    if bold and italic:
        return 'CJK-BoldItalic'
    elif bold:
        return 'CJK-Bold'
    elif italic:
        return 'CJK-Italic'
    return 'CJK'


def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont

    try:
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    except Exception:
        pass

    font_candidates = [
        (r'C:\Windows\Fonts\msyh.ttc', 'msyh'),
        (r'C:\Windows\Fonts\simsun.ttc', 'simsun'),
        (r'C:\Windows\Fonts\simhei.ttf', 'simhei'),
    ]
    for path, name in font_candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('CJK', path))
                try:
                    pdfmetrics.registerFont(TTFont('CJK-Bold', path, subfontIndex=1))
                except Exception:
                    pdfmetrics.registerFont(TTFont('CJK-Bold', path))
                return
            except Exception:
                continue

    try:
        pdfmetrics.registerFont(TTFont('CJK', r'C:\Windows\Fonts\simsun.ttc'))
    except Exception:
        pass


_register_fonts()


class _HTMLToReportLab(HTMLParser):
    def __init__(self):
        super().__init__()
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Preformatted
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        self.flowables = []
        self.current_text = ''
        self.tag_stack = []
        self.in_pre = False
        self.pre_text = ''
        self.in_table = False
        self.table_data = []
        self.current_row = []
        self.current_cell_text = ''
        self.in_style = False
        self.style_content = ''
        self.list_stack = []

        self.styles = getSampleStyleSheet()

        base_font = 'CJK'
        bold_font = 'CJK-Bold'

        self.styles.add(ParagraphStyle(
            'CJKNormal', parent=self.styles['Normal'],
            fontName=base_font, fontSize=10.5, leading=18,
            spaceAfter=6, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKHeading1', parent=self.styles['Normal'],
            fontName=bold_font, fontSize=22, leading=30,
            spaceBefore=16, spaceAfter=10, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKHeading2', parent=self.styles['Normal'],
            fontName=bold_font, fontSize=18, leading=26,
            spaceBefore=14, spaceAfter=8, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKHeading3', parent=self.styles['Normal'],
            fontName=bold_font, fontSize=15, leading=22,
            spaceBefore=12, spaceAfter=6, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKHeading4', parent=self.styles['Normal'],
            fontName=bold_font, fontSize=13, leading=20,
            spaceBefore=10, spaceAfter=4, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKHeading5', parent=self.styles['Normal'],
            fontName=bold_font, fontSize=11, leading=18,
            spaceBefore=8, spaceAfter=4, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKHeading6', parent=self.styles['Normal'],
            fontName=bold_font, fontSize=10, leading=16,
            spaceBefore=6, spaceAfter=3, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKCode', parent=self.styles['Normal'],
            fontName=base_font, fontSize=9, leading=14,
            spaceBefore=6, spaceAfter=6,
            backColor=colors.Color(0.95, 0.95, 0.95),
            leftIndent=12, rightIndent=12,
            borderPadding=6, wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKQuote', parent=self.styles['Normal'],
            fontName=base_font, fontSize=10, leading=16,
            leftIndent=20, rightIndent=12, spaceAfter=6,
            textColor=colors.Color(0.4, 0.4, 0.4),
            wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKBullet', parent=self.styles['Normal'],
            fontName=base_font, fontSize=10.5, leading=18,
            leftIndent=24, bulletIndent=12, spaceAfter=3,
            wordWrap='CJK',
        ))
        self.styles.add(ParagraphStyle(
            'CJKNumber', parent=self.styles['Normal'],
            fontName=base_font, fontSize=10.5, leading=18,
            leftIndent=24, bulletIndent=12, spaceAfter=3,
            wordWrap='CJK',
        ))

    def get_flowables(self):
        return self.flowables

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        attrs_dict = dict(attrs)

        if tag == 'style':
            self.in_style = True
            self.style_content = ''
            return

        if self.in_style:
            return

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._flush_text()
        elif tag == 'p':
            self._flush_text()
        elif tag == 'pre':
            self._flush_text()
            self.in_pre = True
            self.pre_text = ''
        elif tag == 'code':
            if not self.in_pre:
                self.current_text += '<font face="Courier">'
        elif tag == 'br':
            self.current_text += '<br/>'
        elif tag == 'hr':
            self._flush_text()
            from reportlab.platypus import HRFlowable
            self.flowables.append(HRFlowable(width="100%", thickness=1, color='#cccccc', spaceAfter=6, spaceBefore=6))
        elif tag == 'table':
            self._flush_text()
            self.in_table = True
            self.table_data = []
        elif tag == 'tr':
            if self.in_table:
                self.current_row = []
        elif tag in ('td', 'th'):
            if self.in_table:
                self.current_cell_text = ''
        elif tag == 'ul':
            self._flush_text()
            self.list_stack.append('bullet')
        elif tag == 'ol':
            self._flush_text()
            self.list_stack.append('number')
        elif tag == 'li':
            self.current_text = ''
        elif tag == 'blockquote':
            self._flush_text()
            self.tag_stack.append('blockquote')
        elif tag == 'strong' or tag == 'b':
            self.current_text += '<b>'
        elif tag == 'em' or tag == 'i':
            self.current_text += '<i>'
        elif tag == 'del' or tag == 's':
            self.current_text += '<strike>'
        elif tag == 'a':
            href = attrs_dict.get('href', '#')
            if href and not href.startswith('#'):
                self.current_text += f'<a href="{href}" color="#0366d6">'
            else:
                self.current_text += '<font color="#0366d6">'
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', 'image')
            if src.startswith('data:image'):
                self._embed_base64_image(src, alt)
            else:
                self.current_text += f'[{alt}]'

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
            return

        if self.in_style:
            return

        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._flush_heading(tag)
        elif tag == 'p':
            self._flush_paragraph()
        elif tag == 'pre':
            self._flush_pre()
            self.in_pre = False
        elif tag == 'code':
            if not self.in_pre:
                self.current_text += '</font>'
        elif tag in ('td', 'th'):
            if self.in_table:
                self.current_row.append(self.current_cell_text)
        elif tag == 'tr':
            if self.in_table and self.current_row:
                self.table_data.append(self.current_row)
        elif tag == 'table':
            self._flush_table()
            self.in_table = False
        elif tag == 'ul':
            if self.list_stack:
                self.list_stack.pop()
        elif tag == 'ol':
            if self.list_stack:
                self.list_stack.pop()
        elif tag == 'li':
            self._flush_list_item()
        elif tag == 'blockquote':
            self._flush_blockquote()
        elif tag == 'strong' or tag == 'b':
            self.current_text += '</b>'
        elif tag == 'em' or tag == 'i':
            self.current_text += '</i>'
        elif tag == 'del' or tag == 's':
            self.current_text += '</strike>'
        elif tag == 'a':
            if '<a href=' in self.current_text:
                self.current_text += '</a>'
            else:
                self.current_text += '</font>'

    def handle_data(self, data):
        if self.in_style:
            return

        escaped = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        if self.in_pre:
            self.pre_text += data
        elif self.in_table and self.tag_stack and self.tag_stack[-1] in ('td', 'th'):
            self.current_cell_text += escaped
        else:
            self.current_text += escaped

    def _flush_text(self):
        self.current_text = ''

    def _flush_paragraph(self):
        text = self.current_text.strip()
        if text:
            from reportlab.platypus import Paragraph
            try:
                p = Paragraph(text, self.styles['CJKNormal'])
                self.flowables.append(p)
            except Exception:
                clean = re.sub(r'<[^>]+>', '', text)
                if clean.strip():
                    p = Paragraph(clean, self.styles['CJKNormal'])
                    self.flowables.append(p)
        self.current_text = ''

    def _flush_heading(self, tag):
        text = self.current_text.strip()
        if text:
            from reportlab.platypus import Paragraph
            style_name = f'CJK{tag.capitalize()}'
            if style_name not in self.styles.byName:
                style_name = 'CJKHeading1'
            try:
                p = Paragraph(text, self.styles[style_name])
                self.flowables.append(p)
            except Exception:
                clean = re.sub(r'<[^>]+>', '', text)
                if clean.strip():
                    p = Paragraph(clean, self.styles[style_name])
                    self.flowables.append(p)
        self.current_text = ''

    def _flush_pre(self):
        text = self.pre_text.strip()
        if text:
            from reportlab.platypus import Preformatted
            p = Preformatted(text, self.styles['CJKCode'])
            self.flowables.append(p)
        self.pre_text = ''

    def _flush_list_item(self):
        text = self.current_text.strip()
        if text:
            from reportlab.platypus import Paragraph
            if self.list_stack and self.list_stack[-1] == 'bullet':
                p = Paragraph(f'• {text}', self.styles['CJKBullet'])
            else:
                p = Paragraph(f'{text}', self.styles['CJKNumber'])
            self.flowables.append(p)
        self.current_text = ''

    def _flush_blockquote(self):
        text = self.current_text.strip()
        if text:
            from reportlab.platypus import Paragraph
            clean = re.sub(r'<[^>]+>', '', text)
            if clean.strip():
                p = Paragraph(clean, self.styles['CJKQuote'])
                self.flowables.append(p)
        self.current_text = ''

    def _flush_table(self):
        if not self.table_data:
            return

        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        base_font = 'CJK'
        cell_style = ParagraphStyle(
            'CJKTableCell',
            fontName=base_font,
            fontSize=9,
            leading=14,
            wordWrap='CJK',
        )
        header_style = ParagraphStyle(
            'CJKTableHeader',
            fontName='CJK-Bold',
            fontSize=9,
            leading=14,
            wordWrap='CJK',
        )

        processed_data = []
        for i, row in enumerate(self.table_data):
            processed_row = []
            for cell in row:
                style = header_style if i == 0 else cell_style
                try:
                    p = Paragraph(str(cell), style)
                    processed_row.append(p)
                except Exception:
                    clean = re.sub(r'<[^>]+>', '', str(cell))
                    p = Paragraph(clean, style)
                    processed_row.append(p)
            processed_data.append(processed_row)

        if not processed_data:
            return

        num_cols = max(len(row) for row in processed_data)
        col_width = (16 * cm) / num_cols
        col_widths = [col_width] * num_cols

        for row in processed_data:
            while len(row) < num_cols:
                row.append('')

        table = Table(processed_data, colWidths=col_widths)

        style_commands = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
        ]

        for i in range(2, len(processed_data), 2):
            style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.Color(0.98, 0.98, 0.98)))

        table.setStyle(TableStyle(style_commands))
        self.flowables.append(table)
        self.table_data = []

    def _embed_base64_image(self, src, alt):
        import base64
        import tempfile
        import re as _re

        match = _re.match(r'data:image/([^;]+);base64,(.*)', src, _re.DOTALL)
        if not match:
            self.current_text += f'[{alt}]'
            return

        ext = match.group(1).replace('+xml', '')
        if ext == 'svg+xml':
            ext = 'svg'
        if ext == 'svg':
            self.current_text += f'[{alt}]'
            return

        b64_data = match.group(2)
        try:
            img_data = base64.b64decode(b64_data)
            suffix = '.png' if ext == 'png' else '.jpg' if ext in ('jpeg', 'jpg') else '.gif'
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(img_data)
            tmp.close()

            from reportlab.platypus import Image
            from reportlab.lib.units import cm
            try:
                from PIL import Image as PILImage
                with PILImage.open(tmp.name) as pil_img:
                    orig_w, orig_h = pil_img.size
                    max_w = 15 * cm
                    max_h = 20 * cm
                    w = orig_w * 0.026458
                    h = orig_h * 0.026458
                    if w > max_w:
                        ratio = max_w / w
                        w = max_w
                        h = h * ratio
                    if h > max_h:
                        ratio = max_h / h
                        h = max_h
                        w = w * ratio
                    img = Image(tmp.name, width=w, height=h)
            except Exception:
                img = Image(tmp.name, width=10 * cm, height=7.5 * cm)

            img.hAlign = 'CENTER'
            self._flush_text()
            self.flowables.append(img)
        except Exception:
            self.current_text += f'[{alt}]'
