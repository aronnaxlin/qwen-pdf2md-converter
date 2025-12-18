@echo off
CHCP 65001 > nul
echo ==================================================
echo   AI-OCR 助手 Windows 环境配置 (首次运行)
echo ==================================================

:: 1. 创建虚拟环境
echo [1/3] 正在创建独立虚拟环境 (venv)...
python -m venv venv

:: 2. 激活并升级
echo [2/3] 正在升级工具并设置镜像源...
call venv\Scripts\activate
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 3. 安装依赖
echo [3/3] 正在安装 Python 依赖库...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ✅ 配置完成！请确认目录下存在 poppler 文件夹。
echo 现在可以双击 run_windows.bat 启动程序。
pause