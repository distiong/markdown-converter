# 告别格式错乱！这个 Python 小工具让 Markdown 一键变 PDF/Word

---

## 你有没有遇到过这些烦恼？

写了一篇漂亮的 Markdown 文档，领导说「发个 PDF 给我」；

团队协作文档，对方说「能不能转成 Word？」；

导出 PDF 一看——中文全是方块、表格错位、代码乱飞……

**别慌，今天给大家分享一个我刚写的小工具，一键解决这些问题。**

---

## 先看效果

**Web 界面，拖拽上传，点击即转：**

<!-- 插入截图：Web 主界面 -->
![主界面](./screenshots/main.png)

**PDF 输出，中文完美，排版整齐：**

<!-- 插入截图：PDF 效果 -->
![PDF效果](./screenshots/pdf.png)

**Word 输出，格式完整，直接编辑：**

<!-- 插入截图：Word 效果 -->
![Word效果](./screenshots/word.png)

---

## 它能做什么？

**✅ 支持 PDF + Word 双格式输出**

不用纠结选哪个，两个都要。

**✅ 中文完美支持**

标题、正文、表格里的中文，一个方块都不会出现。

**✅ 表格、代码块全覆盖**

Markdown 里的表格、代码块原样保留，代码还有语法高亮。

**✅ 批量转换**

一次上传多个文件，一键全部转换，不用一个个来。

**✅ 拖拽上传**

文件直接拖进浏览器，零学习成本。

**✅ 右上角 Exit 按钮**

用完点一下退出，干干净净。

---

## 怎么用？

### 方式一：下载 EXE（推荐）

**不需要装 Python，双击就能用。**

1. 打开 GitHub Release 页面：

> https://github.com/distiong/markdown-converter/releases/tag/v1.0.0

2. 下载 `MarkdownConverter.exe`
3. 双击运行
4. 浏览器自动打开，开始转换

<!-- 插入截图：Release 下载页面 -->
![下载页面](./screenshots/release.png)

### 方式二：源码运行

如果你是 Python 开发者：

```bash
git clone https://github.com/distiong/markdown-converter.git
cd markdown-converter
pip install -r requirements.txt
python main.py
```

---

## 技术实现（给开发者看的）

整个工具的技术栈：

```
Python 3.x
├── Flask          # Web 界面
├── python-markdown # Markdown 解析
├── reportlab      # PDF 生成
├── python-docx    # Word 生成
└── Pygments       # 代码高亮
```

**PDF 生成踩过的坑：**

一开始用 xhtml2pdf，结果中文全是黑方块，换了各种字体都不行。最后放弃 HTML 中间层，直接用 reportlab Platypus 逐行构建 PDF，注册 STSong-Light CID 字体 + 微软雅黑系统字体，才彻底解决。

**中文换行问题：**

reportlab 默认不处理 CJK 换行，需要在每个 Paragraph 设置 `wordWrap='CJK'`，表格单元格同理。

**代码块 Unicode 字符：**

代码块里如果有 `├│└─` 这类制表符，Courier 字体不支持，改成中文字体才行。

---

## 项目结构

```
md_converter/
├── main.py              # 启动入口
├── app.py               # Flask Web 服务器
├── converter.py         # 转换调度
├── html_generator.py    # Markdown → HTML
├── pdf_writer.py        # PDF 生成
├── docx_writer.py       # Word 生成
├── image_handler.py     # 图片处理
├── build.py             # EXE 打包脚本
└── requirements.txt
```

---

## 后续计划

- [ ] 数学公式渲染（LaTeX）
- [ ] Mermaid 图表支持
- [ ] 自定义主题样式
- [ ] 暗色模式

---

## 开源地址

**GitHub：** https://github.com/distiong/markdown-converter

欢迎 Star ⭐、Fork 🍴、提 Issue 💬

---

## 最后

这个工具是为了解决日常 Markdown 转文档的痛点写的，特别是中文环境下各种格式错乱的问题。

如果你也有类似需求，欢迎试用。觉得有用的话，**点个「在看」再走吧～**

---

> **作者：** TangJC
> 
> **GitHub：** https://github.com/distiong
