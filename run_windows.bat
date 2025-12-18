@echo off
CHCP 65001 > nul
echo 🚀 正在启动 AI-OCR 管道...
call venv\Scripts\activate
streamlit run app.py
pause