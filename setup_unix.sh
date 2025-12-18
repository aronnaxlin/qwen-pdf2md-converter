#!/bin/bash

echo "=================================================="
echo "   AI-OCR 助手 macOS/Linux 环境配置"
echo "=================================================="

# 1. 安装系统依赖 (Poppler)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 检测到 macOS..."
    if ! command -v brew &> /dev/null; then
        echo "❌ 错误: 未检测到 Homebrew。请先安装: https://brew.sh/"
        exit 1
    fi
    echo "📦 正在安装系统依赖 Poppler..."
    brew install poppler
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 检测到 Linux..."
    sudo apt-get update && sudo apt-get install -y poppler-utils
fi

# 2. 创建并激活虚拟环境
echo "🐍 正在创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 3. 安装 Python 依赖
echo "🚚 正在安装依赖库..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "\n✅ 环境配置成功！"
echo "执行 ./run_unix.sh 即可启动程序。"