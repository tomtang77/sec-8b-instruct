#!/bin/bash

echo "🚀 啟動 Streamlit Web 應用..."
echo "請確保您已經設定了 HF_TOKEN 環境變數"
echo "=================================="

# 檢查是否安裝了streamlit
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit 未安裝。正在安裝所需依賴..."
    pip install -r requirements.txt
fi

# 啟動應用
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

echo "🎉 應用已啟動！請在瀏覽器中訪問 http://localhost:8501"