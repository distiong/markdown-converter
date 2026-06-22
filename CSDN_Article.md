# 告别格式错乱！Python 开发 Markdown 转 PDF/Word 图形化工具

> 中文完美支持，表格代码块全覆盖，一键导出 PDF 和 Word

---

## 前言

写 Markdown 的人不少，但一到要导出 PDF 或 Word 的时候就头疼——中文变方块、表格错位、代码乱飞……

于是用 Python 写了一个 **Markdown 转换工具**，带 Web 图形界面，支持 PDF 和 Word 双格式输出，中文完美支持，批量转换不是梦。

**先看效果：**

<!-- 在这里插入截图：Web 主界面 -->
![主界面](https://img-blog.csdnimg.cn/img_convert/placeholder_main.png)

<!-- 在这里插入截图：PDF 效果 -->
![PDF效果](https://img-blog.csdnimg.cn/img_convert/placeholder_pdf.png)

<!-- 在这里插入截图：Word 效果 -->
![Word效果](https://img-blog.csdnimg.cn/img_convert/placeholder_word.png)

---

## 功能亮点

| 功能 | 说明 |
|------|------|
| **双格式输出** | PDF + Word，一次转换全搞定 |
| **中文完美** | 注册 CID 字体 + 系统字体，告别方块字 |
| **表格支持** | 表头灰色背景、斑马纹、边框完整 |
| **代码高亮** | 代码块自动语法高亮，支持语言标识 |
| **批量转换** | 多文件一次上传，一键全部转换 |
| **拖拽上传** | 文件拖进浏览器，零学习成本 |
| **EXE 免装** | 下载双击即用，无需 Python 环境 |

---

## 快速开始

### 方式一：下载 EXE（推荐）

不需要装 Python，双击就能用。

1. 打开 GitHub Release 页面：

> https://github.com/distiong/markdown-converter/releases/tag/v1.0.0

2. 下载 `MarkdownConverter.exe`
3. 双击运行，浏览器自动打开
4. 上传 Markdown 文件，选择格式，点击 Convert

<!-- 在这里插入截图：Release 下载页面 -->
![下载页面](https://img-blog.csdnimg.cn/img_convert/placeholder_release.png)

### 方式二：源码运行

```bash
git clone https://github.com/distiong/markdown-converter.git
cd markdown-converter
pip install -r requirements.txt
python main.py
```

浏览器自动打开 `http://localhost:5000`，即可使用。

---

## 使用演示

### Step 1：上传文件

支持**拖拽上传**或**点击选择**，支持同时上传多个 `.md` 文件。

### Step 2：预览

上传后自动渲染预览，确认内容无误。

### Step 3：选择格式 & 转换

勾选 PDF 或 Word，点击 **Convert** 按钮。

### Step 4：下载

转换完成后直接下载文件，批量转换支持打包下载 ZIP。

---

## 支持的 Markdown 特性

- [x] 多级标题（H1-H6）
- [x] 表格（带表头背景、斑马纹）
- [x] 代码块（带语法高亮）
- [x] 行内代码
- [x] 粗体、斜体、删除线
- [x] 有序/无序列表
- [x] 引用块（带左侧竖线）
- [x] 图片嵌入
- [x] 链接
- [x] 分割线

---

## 技术栈

```
Python 3.x
├── Flask              # Web 界面
├── python-markdown    # Markdown 解析
├── reportlab          # PDF 生成（直接构建，非 HTML 转换）
├── python-docx        # Word 生成
├── Pygments           # 代码高亮
└── Pillow             # 图片处理
```

---

## 项目结构

```
md_converter/
├── main.py              # 启动入口
├── app.py               # Flask Web 服务器
├── converter.py         # 转换调度核心
├── html_generator.py    # Markdown → HTML
├── pdf_writer.py        # PDF 生成（reportlab Platypus）
├── docx_writer.py       # Word 生成
├── image_handler.py     # 图片处理（base64 嵌入）
├── build.py             # EXE 打包脚本
├── styles/              # CSS 样式
├── templates/           # Web 页面模板
└── requirements.txt     # 依赖列表
```

---

## 实现原理

### Markdown → HTML

使用 `python-markdown` 库，加载 `extra`、`codehilite`、`tables`、`fenced_code` 等扩展，将 Markdown 解析为带样式的 HTML。

### Markdown → Word

解析 Markdown 源文本，逐行识别标题、表格、代码块、列表等元素，使用 `python-docx` 直接构建 Word 文档。

**DOCX 样式细节：**
- 表格：表头灰色背景、斑马纹行、微软雅黑字体
- 代码块：灰色背景、逐行渲染、Consolas 等宽字体
- 引用块：蓝色左侧竖线、斜体灰色文字

### Markdown → PDF

采用 **reportlab Platypus** 直接构建 PDF（非 HTML 中间层），彻底绕过 xhtml2pdf 的中文渲染问题。

**PDF 分页优化：**
- 使用 `KeepTogether` 保护段落组，防止表格被截断
- 标题不会出现在页面底部
- 图片自动读取原始尺寸，按页面宽度自适应缩放

---

## 踩坑记录

### 1. xhtml2pdf 中文变方块

xhtml2pdf 对中文字体支持很差，即使注册了字体也可能出现黑方块。最终弃用，改用 reportlab Platypus 直接构建 PDF。

### 2. 中文文字重叠

reportlab 默认不处理 CJK 换行，需要在每个 `Paragraph` 中设置 `wordWrap='CJK'`，表格单元格同理。

### 3. 标题出现 ¶ 符号

Markdown 的 `toc` 扩展默认添加 permalink 锚点，设置 `'permalink': False` 关闭即可。

### 4. 代码块制表符变 n

`├│└─` 等 Unicode 制表符在 Courier 字体中不支持，改用中文字体（Microsoft YaHei）渲染代码块。

---

## EXE 打包

使用 PyInstaller 打包为单文件 EXE：

```bash
pip install pyinstaller
python build.py
```

生成的 EXE 在 `dist/MarkdownConverter.exe`，约 41MB，双击即用。

Web 界面右上角有 **Exit** 按钮，点击即可退出程序。

---

## 后续计划

- [ ] 数学公式渲染（LaTeX）
- [ ] Mermaid 图表支持
- [ ] 自定义主题样式
- [ ] 暗色模式

---

## 项目地址

**GitHub：** https://github.com/distiong/markdown-converter

**Release 下载：** https://github.com/distiong/markdown-converter/releases/tag/v1.0.0

```bash
git clone https://github.com/distiong/markdown-converter.git
```

欢迎 Star ⭐、Fork 🍴、提 Issue 💬

---

## 写在最后

这个工具是为了解决日常 Markdown 转文档的痛点写的，特别是中文环境下各种格式错乱的问题。

如果你也有类似需求，欢迎试用和反馈。

**如果觉得有用，点个赞再走吧~**

---

> **标签：** `Python` `Markdown` `PDF` `Word` `文档转换` `Flask` `reportlab` `python-docx` `PyInstaller`
