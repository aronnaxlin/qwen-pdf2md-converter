<div align = "center">
<h1> 🤖 基于 Qwen 模型的 PDF 转 Markdown 格式转换器 </h1>
</div>

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-ff4b4b.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-success.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**无需手动排版，基于阿里通义千问大模型（Qwen-VL + Qwen-Plus）的三阶段 PDF 转 Markdown 工具。**

本项目通过**视觉识别、单页清洗、全局重组**三层流水线，解决了传统 OCR 无法处理复杂表格、公式及跨页断裂的问题，完美还原文档结构。

---

## 🌟 核心特性 (Core Features)

智能ORC过程包括三个阶段

-  **阶段一：视觉感知**
    * 调用 **Qwen-VL-OCR** 多模态大模型。
    * 精准提取文字、识别复杂表格结构，保留原始排版信息。
-  **阶段二：语义清洗**
    * 调用 **Qwen-Plus** 纯文本模型对每一页进行“微整形”。
    * 修复 OCR 导致的 Markdown 语法闭合错误，去除水印、页眉页脚等噪音。
-  **阶段三：全局重构**
    * 将所有页面拼接后进行全文逻辑梳理。
    * 自动合并跨页断裂的段落。
    * 统一全文的标题层级（如 `一、` -> `1.` -> `(1)`）。
    * 统一中英文标点规范与 LaTeX 公式格式。

---

## 🚀 快速开始 (Quick Start)

本项目已实现**跨平台环境自动适配**，提供一键启动脚本。

### 📦 准备工作
1.  确保已安装 **Python 3.9+**。
2.  获取 [阿里云百炼 API Key](https://bailian.console.aliyun.com/)。

### 💻 Windows 用户
本项目已内置便携版 `Poppler` 组件，**解压即用**。

1.  **首次运行**（初始化环境）：
    双击运行 `setup_windows.bat`
2.  **启动程序**：
    双击运行 `run_windows.bat`

### 💻 macOS / Linux 用户
需要使用脚本自动配置系统依赖。

1.  打开终端，进入项目目录。
2.  赋予脚本执行权限：
    ```bash
    chmod +x setup_unix.sh run_unix.sh
    ```
3.  **首次运行**（自动安装 Homebrew 依赖）：
    ```bash
    ./setup_unix.sh
    ```
4.  **启动程序**：
    ```bash
    ./run_unix.sh
    ```

---

## 🛠️ 项目结构 (Project Structure)

```text
Qwen-OCR-Pipeline/
├── app.py                  # 主程序
├── requirements.txt        # Python 依赖清单
├── setup_windows.bat       # Windows 一键安装脚本
├── run_windows.bat         # Windows 一键运行脚本
├── setup_unix.sh           # macOS/Linux 环境配置脚本
├── run_unix.sh             # macOS/Linux 启动脚本
├── poppler/                # [Windows专用] 内置 PDF 处理引擎
│   └── Library/bin/        
└── README.md               

```

---

## ⚙️ 配置与使用

1. **输入 API Key**：在侧边栏输入你的阿里云 API Key（程序仅在内存中使用，不会保存）。
2. **模型选择**：
* **OCR 模型**：推荐使用 `qwen-vl-ocr-latest`（专为文档优化）。
* **重组模型**：普通文档选 `qwen-plus`；长文本选 `qwen-long`；省钱选`qwen-flash`；如果你拥有贯朽粟腐的家庭条件，选`qwen-max`。


1. **上传文件**：将 PDF 拖入上传区，点击“开始全流程处理”。
2. **导出结果**：处理完成后，点击下载按钮获取清洗好的 `.md` 文件。

---

## ❓ 常见问题 (FAQ)

**Q: 为什么 Windows 上提示找不到 Poppler?**
A: 请确保解压后的文件夹结构未被修改，`app.py` 必须和 `poppler` 文件夹在同一级目录下。

**Q: macOS 上运行报错 "command not found: brew"?**
A: `setup_unix.sh` 脚本依赖 Homebrew 来安装系统库。如果您没有安装 Homebrew，请访问 <https://brew.sh> 安装，或手动安装 `poppler`。

**Q: 全局重组阶段报错 "ContextLimitExceeded"?**
A: 文档字数超过了所选模型的上下文限制。请在侧边栏将“重组模型”切换为 **`qwen-long`**，它支持超长文本窗口。

---

## 📜 免责声明

* 本项目调用的阿里云 Qwen 系列模型属于付费服务，使用过程中会消耗您的 Token 额度。
* 建议在阿里云控制台设置费用预警。

---

## 👨‍💻 Author & Community

**Aronnax**

* Software Engineering Student
* Email: lilinhan917@gmail.com
* Join our QQ group: 871868825

![群号](./README-SRC/qrcode_1766036352190.jpg)

---

*Use Streamlit & Qwen-VL*
*Code with Google Gemini 3 Pro & Qwen Coder*
