@echo off
CHCP 65001 > nul
echo ==================================================
echo   AI-OCR 助手 Windows 环境初始化
echo ==================================================

:: 1. 创建虚拟环境
if not exist venv (
    echo [1/3] 正在创建独立虚拟环境 (venv)...
    python -m venv venv
) else (
    echo [信息] 虚拟环境已存在，跳过创建。
)

:: 2. 激活并升级
echo [2/3] 正在设置镜像源并准备环境...
call venv\Scripts\activate
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 3. 安装依赖 (重点：requests 会在这里被安装)
echo [3/3] 正在安装 Python 依赖库...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ✅ 配置完成！
echo 💡 提示：Poppler 组件将在您首次运行程序并上传 PDF 时自动下载。
echo 现在可以双击 run_windows.bat 启动程序。
pause