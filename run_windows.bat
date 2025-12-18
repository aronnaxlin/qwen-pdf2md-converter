@echo off
:: 锁定脚本所在目录
cd /d "%~dp0"
:: 设置 UTF-8 编码
CHCP 65001 > nul

echo ==================================================
echo   AI-OCR 助手 正在启动...
echo ==================================================

:: 1. 检查虚拟环境是否存在
if not exist venv (
    echo [错误] 找不到虚拟环境 venv！
    echo 请先运行 setup_windows.bat 完成环境初始化。
    pause
    exit /b
)

:: 2. 激活虚拟环境
echo [信息] 正在激活虚拟环境...
call venv\Scripts\activate

:: 3. 启动程序 (改用 python -m streamlit，避开环境变量路径问题)
echo [信息] 正在通过 Python 模块启动 Streamlit...
python -m streamlit run app.py

:: 4. 错误捕获
if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序异常退出。
    echo 提示：如果提示 'No module named streamlit'，说明依赖未安装成功。
    echo 请重新运行 setup_windows.bat 并观察是否有红色报错。
)

pause