# 🛡️ Foundation-Sec-8B-Instruct 網路安全專家AI助手

一個功能強大的網路安全專家AI助手，支援智能對話和即時CVE弱點查詢功能。

## 🚀 功能特色

### 🤖 核心功能
- **智能對話**：基於Foundation-Sec-8B-Instruct模型的專業網路安全諮詢
- **繁體中文回覆**：AI助手使用專業繁體中文提供詳細解答
- **即時CVE查詢**：從NVD資料庫查詢CVE弱點並提供AI智能分析
- **資料持久化**：對話歷史和CVE報告自動保存到本地JSON檔案
- **會話管理**：多會話支援，隨時切換和載入歷史對話
- **雙重介面**：支援終端聊天模式和Web網頁模式
- **本地模型支援**：支援本地模型運行，完全無需HF_TOKEN

### 🔍 CVE查詢功能
- ✅ 即時查詢任何CVE ID
- ✅ 從NVD（國家弱點資料庫）獲取官方資料
- ✅ AI智能分析：弱點概要、攻擊方式、影響範圍、修補建議
- ✅ 完整報告：CVSS分數、危險等級、參考連結
- ✅ 支援下載和進一步討論
- ✅ 自動保存分析報告到本地

### 💾 資料持久化功能
- ✅ **自動保存對話**：每次AI回應後自動保存到JSON檔案
- ✅ **CVE報告保存**：所有分析報告永久保存，支援歷史回顧
- ✅ **多會話管理**：支援建立、切換和管理多個對話會話
- ✅ **歷史資料瀏覽**：側邊欄提供歷史會話和CVE報告瀏覽
- ✅ **重啟後自動恢復**：應用重啟後自動載入最近的對話會話
- ✅ **可控制保存**：提供自動保存開關和手動保存選項
- ✅ **資料清理**：支援清除指定天數前的舊資料

### 💻 雙重介面
- **終端模式**：`app_chat.py` - 命令列互動式聊天
- **Web模式**：`streamlit_app.py` - 現代化標籤頁網頁界面

### 🏠 靈活部署
- **本地模型**：完全離線運行，無需網路和Token
- **遠端模型**：使用Hugging Face Hub上的最新模型
- **智能配置**：自動檢測配置並提供清楚的狀態資訊

## 📋 系統要求

### 基本要求
- Python 3.8+
- RAM: 16GB+（CPU模式）
- VRAM: 16GB+（GPU模式，推薦）

### 推薦配置
- NVIDIA GPU（支援CUDA）
- 高速SSD硬碟
- 穩定的網路連接（用於CVE查詢）

## ⚙️ 安裝與配置

### 1. 環境準備

```bash
# 克隆專案
git clone <repository-url>
cd sec-8b-instruct

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 模型配置

#### 選項A：使用本地模型（推薦）

1. **下載模型到本地**：
```bash
# 使用huggingface-cli（需要先設定HF_TOKEN）
huggingface-cli download fdtn-ai/Foundation-Sec-8B-Instruct --local-dir /path/to/your/model
```

2. **配置本地模型**：
```python
# 編輯 model_config.py
USE_LOCAL_MODEL = True
LOCAL_MODEL_PATH = "/path/to/your/model"  # 修改為實際路徑
```

3. **驗證配置**：
```bash
python model_config.py
```

#### 選項B：使用遠端模型

```bash
# 設定Hugging Face Token
export HF_TOKEN="your_hugging_face_token"

# model_config.py 設定
USE_LOCAL_MODEL = False
```

### 3. 驗證安裝

```bash
# 檢查模型配置
python model_config.py

# 測試基本功能
python app.py
```

## 🎯 使用方法

### 🖥️ 終端聊天模式

```bash
source venv/bin/activate
python app_chat.py
```

**可用命令：**
- 直接輸入問題開始對話
- `cve CVE-2023-44487` - 查詢並分析指定CVE
- `help` - 顯示所有命令
- `history` - 查看對話歷史
- `clear` - 清除對話歷史
- `quit` / `exit` / `q` - 結束程式

### 🌐 Web網頁模式

```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

**功能特色：**
- 🎯 **標籤頁設計**：AI聊天與CVE分析功能清楚分離
- 💬 **AI聊天標籤**：純粹的專業對話體驗
- 🔍 **CVE分析標籤**：專用的CVE查詢與分析空間
- 📊 **智能狀態管理**：操作後正確保持當前標籤頁
- 🎨 **直覺界面**：現代化設計，易於操作
- 💾 **資料持久化**：對話和CVE報告自動保存，重啟不遺失
- 📚 **歷史管理**：完整的會話和CVE報告歷史瀏覽功能

訪問 `http://localhost:8501` 開始使用

**完整的Web界面體驗：**
1. **💬 AI聊天助手標籤**：專注於與AI專家對話
2. **🔍 CVE弱點分析標籤**：專用CVE查詢和完整報告展示
3. **⚙️ 強化側邊欄**：
   - 💾 資料管理：自動保存控制、手動保存、新會話建立
   - 📚 歷史會話：瀏覽和載入之前的對話記錄
   - 🔍 CVE報告歷史：查看和載入歷史分析報告
   - 📊 會話統計：當前會話資訊和系統狀態
   - 🗑️ 資料清理：管理和清理舊資料

### 🔍 CVE查詢功能詳解

#### 支援的CVE格式
- ✅ `CVE-2023-44487`
- ✅ `CVE-2021-44228`
- ❌ `2023-44487`（缺少CVE-前綴）
- ❌ `CVE-23-1234`（年份格式錯誤）

#### 分析報告包含
1. **基本資訊**：CVE ID、危險等級、發布日期、狀態
2. **CVSS分數**：v3.1/v3.0/v2.0分數和嚴重程度
3. **分類標籤**：CWE（常見弱點列表）分類
4. **弱點描述**：官方詳細描述
5. **AI智能分析**：
   - 弱點概要
   - 攻擊方式
   - 影響範圍
   - 修補建議
   - 預防策略
6. **參考連結**：相關技術文件和修補資訊

#### 使用範例

**終端模式：**
```bash
💬 You: cve CVE-2021-44228
🤖 系統會自動查詢Log4Shell弱點並提供完整分析報告
```

**Web模式：**
1. 點擊「🔍 CVE弱點分析」標籤頁
2. 在輸入框中輸入 `CVE-2023-44487`
3. 點擊「🔍 查詢分析」按鈕
4. 系統自動查詢並生成完整AI分析報告
5. 可使用「💬 轉到聊天討論」進一步詢問
6. 可使用「📥 下載報告」保存分析結果

## 🔧 技術架構

### 檔案結構
```
sec-8b-instruct/
├── app.py                  # 基礎推理腳本
├── app_chat.py             # 終端聊天應用
├── streamlit_app.py        # Web應用
├── cve_analyzer.py         # CVE查詢分析核心
├── model_config.py         # 智能模型配置系統
├── data_persistence.py     # 資料持久化管理器
├── data/                   # 資料存儲目錄
│   ├── chat_history.json   # 對話歷史記錄
│   └── cve_reports.json    # CVE分析報告
├── requirements.txt        # Python依賴
├── run_web_app.sh         # Web應用啟動腳本
└── README.md              # 本說明文件
```

### 核心模組
- **model_config.py**：智能模型配置，支援本地/遠端切換
- **cve_analyzer.py**：CVE查詢引擎，整合NVD API和LLM分析
- **data_persistence.py**：資料持久化管理，處理對話歷史和CVE報告的JSON存儲
- **inference系統**：基於transformers的AI推理引擎
- **雙重界面**：終端CLI和Streamlit Web界面

### 依賴套件
```
streamlit>=1.28.0          # Web框架
transformers>=4.30.0       # AI模型框架
torch>=2.0.0              # 深度學習框架
accelerate>=0.20.0        # 模型加速
requests>=2.31.0          # HTTP請求（CVE查詢）
python-dateutil>=2.8.0    # 日期處理
beautifulsoup4>=4.12.0    # HTML解析
```

## 🚨 故障排解

### 模型相關問題

**Q: 模型載入失敗？**
```bash
# 檢查配置
python model_config.py

# 檢查GPU記憶體
nvidia-smi

# 嘗試CPU模式（在model_config.py中調整device_map）
```

**Q: 本地模型路徑錯誤？**
```bash
# 確認模型目錄結構
ls -la /path/to/your/model/
# 應包含：config.json, pytorch_model.bin, tokenizer.json等
```

### CVE查詢問題

**Q: CVE查詢失敗？**
- 檢查網路連接
- 驗證CVE ID格式
- 查看是否該CVE存在於NVD資料庫

**Q: 查詢速度慢？**
- NVD API有時回應較慢，系統已內建重試機制
- 較新的CVE通常查詢較快

### Web界面問題

**Q: Streamlit啟動失敗？**
```bash
# 檢查端口
netstat -an | grep 8501

# 清除瀏覽器快取
# 重新啟動應用
```

**Q: CVE查詢後跳轉到錯誤的標籤頁？**
- 這是已修復的已知問題
- 現在使用智能狀態管理，CVE查詢後會正確保持在CVE分析標籤頁
- 如仍有問題，請重新整理頁面

**Q: AI回覆不是繁體中文？**
- 系統已設定強制使用繁體中文回覆
- 如遇到簡體中文回覆，請重新啟動應用
- 檢查system prompt是否被修改

**Q: 標籤頁切換不正常？**
- 清除瀏覽器快取和Cookies
- 確保使用現代瀏覽器（Chrome、Firefox、Safari等）
- 避免同時開啟多個應用分頁

### 資料持久化問題

**Q: 對話或CVE報告沒有自動保存？**
- 檢查側邊欄的「自動保存對話」開關是否啟用
- 確認 `data/` 目錄是否存在且有寫入權限
- 查看是否有檔案權限或磁碟空間問題

**Q: 歷史對話載入失敗？**
- 檢查 `data/chat_history.json` 檔案是否存在
- 確認JSON檔案格式是否正確（可能被意外修改）
- 嘗試手動刪除損壞的JSON檔案，系統會自動重建

**Q: CVE報告歷史顯示異常？**
- 檢查 `data/cve_reports.json` 檔案完整性
- 確認檔案大小合理（過大可能影響載入速度）
- 可使用資料清理功能清除舊資料

**Q: 會話切換後資料混亂？**
- 每個會話都有唯一的UUID識別碼
- 如果出現資料關聯錯誤，建立新會話即可解決
- 檢查是否同時開啟多個應用實例造成衝突

**Q: JSON檔案過大影響效能？**
```bash
# 檢查檔案大小
ls -lh data/

# 手動清理30天前的資料
# 在側邊欄使用「資料清理」功能
```

## 📊 使用範例

### 網路安全諮詢
```
💬 You: 什麼是SQL注入攻擊？如何防護？

🤖 Assistant: SQL注入攻擊是一種程式碼注入技術，攻擊者透過在應用程式的輸入點
插入惡意SQL語句，來干擾資料庫查詢的執行...

防護措施包括：
1. 使用參數化查詢或預處理語句
2. 輸入驗證和過濾
3. 最小權限原則
4. 定期安全稽核...（專業繁體中文詳細回答）
```

### CVE弱點分析
```
💬 You: cve CVE-2021-44228

🤖 系統: 🔍 正在查詢 CVE-2021-44228...
📊 正在提取CVE資訊...
🤖 正在進行智能分析...
📝 正在生成報告...

（返回完整的Log4Shell弱點分析報告，包含AI智能分析）
```

### Web界面CVE分析體驗
```
1. 點擊「🔍 CVE弱點分析」標籤頁
2. 輸入 CVE-2021-44228
3. 點擊「🔍 查詢分析」
4. 獲得完整報告：
   - 基本資訊和CVSS分數
   - AI智能分析（繁體中文）
   - 修補建議和預防策略
5. 使用「💬 轉到聊天討論」進一步詢問
```

### 綜合安全評估
```
💬 You: 我的Web應用使用了Apache Struts 2.5.20，有什麼安全風險？

🤖 Assistant: Apache Struts 2.5.20確實存在多個已知的安全弱點...
建議您立即查詢相關CVE：CVE-2021-31805, CVE-2020-17530...
（提供專業的繁體中文安全建議）
```

### 資料持久化使用體驗
```
1. 啟動應用：
   streamlit run streamlit_app.py
   
2. 系統自動載入：
   ✅ 已載入歷史對話 (15 則訊息)
   
3. 繼續之前的對話：
   💬 You: 繼續我們剛才討論的SQL注入防護...
   
4. 查詢新的CVE：
   - 切換到CVE分析標籤
   - 輸入 CVE-2023-44487
   - 系統自動保存分析報告
   
5. 會話管理：
   - 側邊欄選擇「建立新會話」
   - 或從歷史會話中選擇載入
   
6. 歷史回顧：
   - 在「CVE報告歷史」中載入之前的分析
   - 在「歷史會話」中回看過去的對話
```

## 🤝 開發與貢獻

### 程式架構
- **模組化設計**：清楚分離模型管理、CVE查詢、界面展示、資料持久化
- **配置驅動**：透過`model_config.py`統一管理設定
- **資料持久化**：基於JSON的本地存儲系統，支援會話管理和CVE報告保存
- **錯誤處理**：完善的異常處理和用戶友善提示
- **擴展性**：易於添加新功能和資料源，支援資料庫遷移

### 自定義開發
```python
# 擴展CVE分析器
from cve_analyzer import CVEAnalyzer

analyzer = CVEAnalyzer(inference_function=your_custom_llm)
report = analyzer.query_and_analyze("CVE-2023-12345")

# 自定義模型配置
from model_config import setup_local_model
setup_local_model("/path/to/your/custom/model")

# 資料持久化擴展
from data_persistence import DataPersistence

# 自定義資料存儲路徑
dp = DataPersistence(data_dir="custom_data")

# 程式化管理會話
session_id = dp.create_new_session()
dp.save_chat_messages(session_id, messages)
loaded_session, messages = dp.load_chat_messages(session_id)

# 批次處理CVE報告
for cve_id in cve_list:
    report = analyzer.query_and_analyze(cve_id)
    dp.save_cve_report(session_id, cve_id, report)

# 資料清理和維護
dp.clear_old_data(days=7)  # 清除一週前的資料
session_list = dp.get_session_list()
cve_reports = dp.get_cve_report_list()
```

## 📄 授權與支援

- **授權**：請參考項目授權條款
- **問題回報**：透過GitHub Issues回報問題
- **功能建議**：歡迎提交Pull Request

---

## 🎉 快速開始

```bash
# 1. 安裝
git clone <repository>
cd sec-8b-instruct
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 配置（選擇其一）
# 選項A: 本地模型（推薦）
vim model_config.py  # 設定 USE_LOCAL_MODEL = True

# 選項B: 遠端模型
export HF_TOKEN="your_token"

# 3. 啟動
python app_chat.py              # 終端模式
# 或
streamlit run streamlit_app.py  # Web模式（推薦新體驗）

# 4. 體驗新功能
# 💬 AI聊天：專業繁體中文回覆
# 🔍 CVE查詢：cve CVE-2023-44487（終端）或切換到CVE標籤頁（Web）
# 📊 完整分析：AI智能分析報告
```

### 🌟 新版本亮點
- ✅ **繁體中文專業回覆**：AI助手現在使用專業繁體中文
- ✅ **標籤頁設計**：Web界面採用清楚的功能分離設計
- ✅ **智能狀態管理**：CVE查詢後正確保持在分析標籤頁
- ✅ **完整CVE體驗**：從查詢到分析到討論的一站式流程

🚀 **立即體驗升級後的專業網路安全AI助手！**