@echo off
:: 1. 强制切换到脚本所在的目录，防止双击运行路径错误
cd /d "%~dp0"

:: 2. 设置 UTF-8 编码，防止中文乱码
CHCP 65001 > nul

echo ==================================================
echo   AI-OCR 助手 Windows 环境初始化
echo ==================================================

:: 3. 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 并勾选 "Add Python to PATH"！
    echo 官网下载: https://www.python.org/
    pause
    exit /b
)

:: 4. 创建虚拟环境
if not exist venv (
    echo [1/3] 正在创建独立虚拟环境 (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败，请检查 Python 安装是否完整。
        pause
        exit /b
    )
) else (
    echo [信息] 虚拟环境已存在，跳过创建。
)

:: 5. 激活并升级组件
echo [2/3] 正在准备 Pip 环境...
:: 使用 call 确保激活脚本后能继续执行本脚本
call venv\Scripts\activate
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 6. 安装依赖
echo [3/3] 正在从清华源安装依赖库...
if not exist requirements.txt (
    echo [错误] 找不到 requirements.txt 文件！请确保文件在脚本同级目录下。
    pause
    exit /b
)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ==================================================
echo ✅ 配置完成！
echo 💡 提示：Poppler 组件将在首次运行程序并上传 PDF 时自动下载。
echo 现在可以双击 run_windows.bat 启动程序。
echo ==================================================
pause