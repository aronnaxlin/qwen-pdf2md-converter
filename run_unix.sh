#!/bin/bash
if [ ! -d "venv" ]; then
    echo "❌ 找不到虚拟环境，请先运行 ./setup_unix.sh"
    exit 1
fi

echo "🚀 正在启动服务..."
source venv/bin/activate
streamlit run app.py