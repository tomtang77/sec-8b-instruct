# Foundation-Sec-8B-Instruct 聊天應用

這是一個基於 Foundation-Sec-8B-Instruct 模型的網絡安全專家聊天應用程式。

## 功能特色

- 🤖 **智能對話**：使用專業的網絡安全AI模型
- 💬 **交互式聊天**：支持多輪對話和歷史記錄
- 🔒 **網絡安全專家**：專門針對網絡安全領域優化
- 🚀 **簡單易用**：命令行界面，快速啟動

## 文件說明

- `app_chat.py` - 交互式聊天應用程式
- `app.py` - 簡單的單次推理腳本

## 環境要求

- Python 3.8+
- PyTorch
- Transformers
- CUDA (可選，用於GPU加速)

## 安裝步驟

1. **克隆倉庫**
   ```bash
   git clone git@github.com:tomtang77/sec-8b-instruct.git
   cd sec-8b-instruct
   ```

2. **創建虛擬環境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   # venv\Scripts\activate  # Windows
   ```

3. **安裝依賴**
   ```bash
   pip install torch transformers
   ```

4. **設置Hugging Face Token**
   ```bash
   export HF_TOKEN=your_hugging_face_token
   ```

## 使用方法

### 交互式聊天

```bash
python3 app_chat.py
```

聊天命令：
- 輸入任何問題開始對話
- `quit`、`exit` 或 `q` - 退出程式
- `clear` - 清除對話歷史
- `history` - 查看對話歷史

### 單次推理

```bash
python3 app.py
```

## 模型資訊

- **模型名稱**: fdtn-ai/Foundation-Sec-8B-Instruct
- **參數規模**: 8B
- **專業領域**: 網絡安全
- **張量類型**: BFloat16

## 系統要求

- **CPU**: 支持所有現代CPU
- **GPU**: 推薦使用CUDA兼容的GPU以提升性能
- **RAM**: 建議16GB+（CPU模式）
- **VRAM**: 建議16GB+（GPU模式）

## 範例對話

```
💬 You: What is SQL injection?

🤖 Assistant: SQL injection is a code injection technique where malicious SQL 
statements are inserted into application entry points, allowing attackers to 
interfere with database queries and potentially access, modify, or delete data.
```

## 貢獻指南

歡迎提交Issue和Pull Request來改進這個項目！

## 授權

此項目遵循開源授權條款。

## 聯絡方式

如有問題或建議，請通過GitHub Issues聯絡。