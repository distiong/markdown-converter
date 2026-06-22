# Markdown Converter

将 Markdown 文件转换为 PDF 和 Word 格式的图形界面工具。

## 功能特性

- 支持 Markdown 转 PDF 和 Word (.docx)
- Web 图形界面，操作简单
- 支持批量转换
- 完整支持表格、代码块、多级标题
- 支持图片嵌入
- 中文友好

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

浏览器自动打开 `http://localhost:5000`，然后：

1. 拖拽或点击上传 `.md` 文件
2. 选择输出格式（PDF / Word）
3. 点击 "Convert" 转换
4. 下载生成的文件

## PDF 生成说明

- 默认使用 reportlab 直接生成 PDF（无需额外安装）
- 如需更高质量，可安装 [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)，工具会自动切换

## 项目结构

```
md_converter/
├── main.py              # 启动入口
├── app.py               # Flask Web 服务器
├── converter.py         # 转换调度核心
├── html_generator.py    # Markdown → HTML
├── pdf_writer.py        # HTML → PDF
├── docx_writer.py       # Markdown → Word
├── image_handler.py     # 图片处理
├── math_handler.py      # 数学公式处理
├── diagram_handler.py   # Mermaid 图表处理
├── styles/              # CSS 样式
├── templates/           # Web 页面模板
└── requirements.txt     # 依赖列表
```

## License

MIT
