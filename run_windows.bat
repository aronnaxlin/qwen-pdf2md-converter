@echo off
cd /d "%~dp0"
CHCP 65001 > nul

echo ==================================================
echo   AI-OCR Assistant Launching...
echo ==================================================

if not exist venv (
    echo [Error] Virtual environment 'venv' not found.
    echo Please run setup_windows.bat first.
    pause
    exit /b
)

:: 激活虚拟环境 (注意：这里不要在括号里写中文提示)
call venv\Scripts\activate

:: 启动程序
echo [Info] Starting Streamlit app...
python -m streamlit run app.py

pause