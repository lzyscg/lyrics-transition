#!/bin/bash
set -e

cd "$(dirname "$0")/../.."

export PYTHONUTF8=1
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo "正在启动歌词转换工具..."
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 python3。请先安装 Python 3.12 或更新版本。"
  echo "可以从 https://www.python.org/downloads/macos/ 下载。"
  read -n 1 -s -r -p "按任意键关闭窗口。"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "首次启动：正在创建本地 Python 环境..."
  python3 -m venv .venv
fi

source ".venv/bin/activate"

echo "正在检查依赖..."
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt

echo
echo "浏览器会自动打开 http://localhost:8501"
echo "使用期间请不要关闭这个窗口。关闭窗口后，工具也会停止。"
echo

(sleep 3 && open "http://localhost:8501") &
python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --server.port 8501 --browser.gatherUsageStats false

echo
read -n 1 -s -r -p "工具已停止。按任意键关闭窗口。"
