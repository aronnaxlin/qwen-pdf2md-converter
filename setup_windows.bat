@echo off
:: 锁定目录
cd /d "%~dp0"
:: 设置编码
CHCP 65001 > nul

echo ==================================================
echo   AI-OCR Assistant Windows Setup
echo ==================================================

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first!
    pause
    exit /b
)

:: 创建虚拟环境
if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b
    )
) else (
    echo [INFO] venv already exists.
)

:: 激活并升级
echo [2/3] Preparing pip environment...
call venv\Scripts\activate
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 安装依赖
echo [3/3] Installing requirements...
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b
)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ==================================================
echo   SUCCESS: Environment is ready.
echo   Tip: Poppler will be downloaded on first run.
echo ==================================================
pause