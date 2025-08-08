import streamlit as st
import sys
import os

# 為了避免導入app_chat.py時執行底部的聊天循環，我們直接複製需要的代碼
import transformers
import torch
import re
import os

# 導入CVE分析器和模型配置
from cve_analyzer import CVEAnalyzer
from datetime import datetime
from model_config import get_model_config
from data_persistence import DataPersistence

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 獲取模型配置
MODEL_PATH, NEED_TOKEN, HF_TOKEN = get_model_config()

from transformers import AutoModelForCausalLM, AutoTokenizer

# 只有在還沒有載入模型時才載入（避免重複載入）
if 'tokenizer' not in st.session_state:
    with st.spinner("🔄 正在載入模型..."):
        if NEED_TOKEN:
            st.session_state.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, token=HF_TOKEN)
            st.session_state.model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=MODEL_PATH,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                token=HF_TOKEN,
            )
        else:
            st.write("📂 使用本地模型，不需要HF_TOKEN")
            st.session_state.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            st.session_state.model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=MODEL_PATH,
                device_map="auto",
                torch_dtype=torch.bfloat16,
            )

generation_args = {
    "max_new_tokens": 1024,
    "temperature": None,
    "repetition_penalty": 1.2,
    "do_sample": False,
    "use_cache": True,
    "eos_token_id": st.session_state.tokenizer.eos_token_id,
    "pad_token_id": st.session_state.tokenizer.pad_token_id,
}

DEFAULT_SYSTEM_PROMPT = "你是一位專業的網路安全專家。請務必使用繁體中文回答所有問題，提供專業、詳細且實用的網路安全建議和解決方案。"

def inference(request, system_prompt=DEFAULT_SYSTEM_PROMPT):
    if isinstance(request, str):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request},
        ]
    elif isinstance(request, list):
        if request[0].get("role") != "system":
            messages = [{"role": "system", "content": system_prompt}] + request
        else:
            messages = request
    else:
        raise ValueError(
            "Request is not well formed. It must be a string or list of dict with correct format."
        )

    inputs = st.session_state.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    inputs = st.session_state.tokenizer(inputs, return_tensors="pt")
    input_ids = inputs["input_ids"].to(DEVICE)
    with torch.no_grad():
        outputs = st.session_state.model.generate(
            input_ids=input_ids,
            **generation_args,
        )
    response = st.session_state.tokenizer.decode(
        outputs[0][input_ids.shape[1]:],  # Only get new tokens
        skip_special_tokens=False
    )
    
    if response.endswith(st.session_state.tokenizer.eos_token):
        response = response[:-len(st.session_state.tokenizer.eos_token)]
    
    return response

# 設定頁面配置
st.set_page_config(
    page_title="🤖 Cybersecurity Expert Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化資料持久化管理器
if "data_persistence" not in st.session_state:
    st.session_state.data_persistence = DataPersistence()

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# 初始化會話管理
if "current_session_id" not in st.session_state:
    # 嘗試載入最近的對話歷史
    session_id, loaded_messages = st.session_state.data_persistence.load_chat_messages()
    if session_id and loaded_messages:
        # 載入成功，使用歷史會話
        st.session_state.current_session_id = session_id
        # 添加系統提示詞到載入的訊息前面
        st.session_state.messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}] + loaded_messages
        st.success(f"✅ 已載入歷史對話 ({len(loaded_messages)} 則訊息)")
    else:
        # 建立新會話
        st.session_state.current_session_id = st.session_state.data_persistence.create_new_session()
        st.session_state.messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]

# 初始化CVE分析器
if "cve_analyzer" not in st.session_state:
    st.session_state.cve_analyzer = CVEAnalyzer(inference_function=inference)

# CVE查詢結果
if "cve_report" not in st.session_state:
    st.session_state.cve_report = None

# 追踪當前活動的標籤頁
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "chat"  # 預設為聊天標籤

# 自動保存標記
if "auto_save_enabled" not in st.session_state:
    st.session_state.auto_save_enabled = True

# 側邊欄設定
with st.sidebar:
    st.title("⚙️ 設定")
    
    # 資料持久化控制
    st.subheader("💾 資料管理")
    
    # 自動保存開關
    auto_save = st.checkbox(
        "自動保存對話", 
        value=st.session_state.auto_save_enabled,
        help="自動保存對話歷史和CVE報告到本地JSON檔案"
    )
    if auto_save != st.session_state.auto_save_enabled:
        st.session_state.auto_save_enabled = auto_save
        st.rerun()
    
    # 手動保存按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 立即保存", use_container_width=True):
            if st.session_state.auto_save_enabled:
                st.session_state.data_persistence.save_chat_messages(
                    st.session_state.current_session_id, 
                    st.session_state.messages
                )
                st.success("✅ 手動保存完成")
            else:
                st.warning("請先啟用自動保存功能")
    
    with col2:
        if st.button("🗂️ 新會話", use_container_width=True):
            # 保存當前會話（如果啟用自動保存）
            if st.session_state.auto_save_enabled:
                st.session_state.data_persistence.save_chat_messages(
                    st.session_state.current_session_id, 
                    st.session_state.messages
                )
            
            # 建立新會話
            st.session_state.current_session_id = st.session_state.data_persistence.create_new_session()
            st.session_state.messages = [{"role": "system", "content": st.session_state.system_prompt}]
            st.session_state.cve_report = None
            st.success("✅ 已建立新會話")
            st.rerun()
    
    st.divider()
    
    # 對話管理按鈕
    st.subheader("🧹 清除功能")
    
    if st.button("🗑️ 清除當前對話", type="secondary", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": st.session_state.system_prompt}]
        st.success("當前對話已清除！")
        st.rerun()
    
    if st.button("🗑️ 清除CVE結果", type="secondary", use_container_width=True):
        st.session_state.cve_report = None
        st.success("CVE查詢結果已清除！")
        st.rerun()
    
    st.divider()
    
    # 顯示統計資訊
    st.subheader("📊 會話統計")
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 用戶訊息", len(user_messages))
        st.metric("📊 CVE報告", "已就緒" if st.session_state.cve_report else "無")
    with col2:
        st.metric("🤖 助手回應", len(assistant_messages))
        st.metric("🗂️ 會話ID", st.session_state.current_session_id[:8] + "..." if st.session_state.current_session_id else "無")
    
    st.divider()
    
    # 歷史會話瀏覽
    st.subheader("📚 歷史會話")
    
    # 獲取會話列表
    try:
        session_list = st.session_state.data_persistence.get_session_list()
        if session_list:
            # 選擇會話
            session_options = []
            session_map = {}
            
            for session in session_list[:10]:  # 只顯示最近10個會話
                preview = session['preview']
                created_time = session['created_at'][:16].replace('T', ' ')
                option_text = f"{created_time} - {preview}"
                session_options.append(option_text)
                session_map[option_text] = session['session_id']
            
            if session_options:
                selected_session = st.selectbox(
                    "選擇歷史會話",
                    options=["當前會話"] + session_options,
                    help="選擇要載入的歷史會話"
                )
                
                if selected_session != "當前會話" and selected_session in session_map:
                    if st.button("📂 載入選中會話", use_container_width=True):
                        # 保存當前會話
                        if st.session_state.auto_save_enabled:
                            st.session_state.data_persistence.save_chat_messages(
                                st.session_state.current_session_id, 
                                st.session_state.messages
                            )
                        
                        # 載入選中的會話
                        selected_id = session_map[selected_session]
                        session_id, loaded_messages = st.session_state.data_persistence.load_chat_messages(selected_id)
                        
                        if loaded_messages:
                            st.session_state.current_session_id = selected_id
                            st.session_state.messages = [{"role": "system", "content": st.session_state.system_prompt}] + loaded_messages
                            st.session_state.cve_report = None  # 清除當前CVE報告
                            st.success(f"✅ 已載入會話 ({len(loaded_messages)} 則訊息)")
                            st.rerun()
        else:
            st.info("尚無歷史會話")
            
    except Exception as e:
        st.error(f"載入歷史會話時發生錯誤: {e}")
    
    st.divider()
    
    # CVE報告歷史
    st.subheader("🔍 CVE報告歷史")
    
    try:
        cve_reports = st.session_state.data_persistence.get_cve_report_list()
        if cve_reports:
            # 顯示最近的CVE報告
            recent_reports = cve_reports[:5]  # 最近5個報告
            
            for report in recent_reports:
                with st.expander(f"📋 {report['cve_id']} - {report['query_time'][:16].replace('T', ' ')}"):
                    st.text(f"會話: {report['session_id'][:8]}...")
                    st.text(f"內容長度: {report['content_length']} 字元")
                    
                    if st.button(f"📂 載入 {report['cve_id']}", key=f"load_cve_{report['id']}"):
                        # 載入這個CVE報告
                        loaded_report = st.session_state.data_persistence.load_cve_report(
                            report['cve_id'], 
                            report['session_id']
                        )
                        if loaded_report:
                            st.session_state.cve_report = loaded_report
                            st.session_state.active_tab = "cve"  # 切換到CVE標籤
                            st.success(f"✅ 已載入 {report['cve_id']} 報告")
                            st.rerun()
        else:
            st.info("尚無CVE報告歷史")
            
    except Exception as e:
        st.error(f"載入CVE報告歷史時發生錯誤: {e}")
    
    st.divider()
    
    # 系統資訊
    st.subheader("🔧 系統資訊")
    st.text("Model: Foundation-Sec-8B")
    st.text("Language: 繁體中文")
    st.text("Mode: Security Expert")
    st.text(f"Auto-save: {'啟用' if st.session_state.auto_save_enabled else '停用'}")
    
    # 資料清理功能
    with st.expander("🗑️ 資料清理"):
        st.warning("⚠️ 危險操作：此操作無法復原")
        
        days = st.slider("清除幾天前的資料", min_value=1, max_value=90, value=30)
        
        if st.button("🗑️ 執行清理", type="secondary"):
            try:
                st.session_state.data_persistence.clear_old_data(days)
                st.success(f"✅ 已清除 {days} 天前的資料")
            except Exception as e:
                st.error(f"清理資料時發生錯誤: {e}")

# 主要內容區域
st.title("🛡️ 網路安全專家AI助手")
st.markdown("**專業的網路安全諮詢與CVE弱點分析平台**")

# 功能選擇區域
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 AI聊天助手", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == "chat" else "secondary"):
        st.session_state.active_tab = "chat"
        st.rerun()

with col2:
    if st.button("🔍 CVE弱點分析", use_container_width=True,
                 type="primary" if st.session_state.active_tab == "cve" else "secondary"):
        st.session_state.active_tab = "cve"
        st.rerun()

st.divider()

# 根據選中的標籤顯示相應內容
if st.session_state.active_tab == "chat":
    st.subheader("🤖 與網路安全專家對話")
    st.markdown("向AI專家詢問任何網路安全相關問題，獲得專業建議和解決方案。")
    
    # 顯示對話歷史（排除系統訊息）
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] != "system":  # 不顯示系統訊息
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # 用戶輸入
    if prompt := st.chat_input("請輸入您的問題..."):
        # 添加用戶訊息到對話歷史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 顯示用戶訊息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成並顯示助手回應
        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                try:
                    # 使用現有的inference函數
                    response = inference(st.session_state.messages)
                    st.markdown(response)
                    
                    # 添加助手回應到對話歷史
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # 自動保存對話歷史
                    if st.session_state.auto_save_enabled:
                        st.session_state.data_persistence.save_chat_messages(
                            st.session_state.current_session_id, 
                            st.session_state.messages
                        )
                    
                except Exception as e:
                    st.error(f"❌ 發生錯誤: {str(e)}")
                    st.info("請檢查模型是否正確載入，或者網路連接是否正常。")

elif st.session_state.active_tab == "cve":
    st.subheader("🔍 CVE弱點查詢與分析")
    st.markdown("查詢任何CVE弱點，獲得詳細的AI智能分析報告。")
    
    # CVE查詢區域
    with st.container():
        st.markdown("### 📝 輸入CVE ID")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            cve_input = st.text_input(
                "CVE ID", 
                placeholder="例如: CVE-2023-44487, CVE-2021-44228",
                help="請輸入標準格式的CVE ID（例如：CVE-2023-1234）",
                label_visibility="collapsed"
            )
        
        with col2:
            search_button = st.button("🔍 查詢分析", type="primary", use_container_width=True)
    
    # 查詢處理
    if search_button:
        if cve_input.strip():
            with st.spinner("🔍 正在查詢CVE資訊並進行AI分析..."):
                try:
                    report = st.session_state.cve_analyzer.query_and_analyze(cve_input.strip())
                    if report:
                        st.session_state.cve_report = report
                        st.session_state.active_tab = "cve"  # 確保保持在CVE標籤頁
                        
                        # 自動保存CVE報告
                        if st.session_state.auto_save_enabled:
                            st.session_state.data_persistence.save_cve_report(
                                st.session_state.current_session_id,
                                cve_input.strip(),
                                report
                            )
                        
                        st.success(f"✅ 成功完成 {cve_input.strip()} 的查詢與分析")
                        st.rerun()
                    else:
                        st.error("❌ 查詢失敗，請檢查CVE ID是否正確或該CVE是否存在於NVD資料庫中")
                except Exception as e:
                    st.error(f"❌ 查詢過程發生錯誤: {str(e)}")
                    st.info("💡 請檢查網路連接是否正常，或稍後再試")
        else:
            st.warning("⚠️ 請輸入CVE ID")
    
    st.divider()
    
    # CVE分析結果顯示
    if st.session_state.cve_report:
        st.markdown("### 📊 CVE分析報告")
        
        # 提供操作按鈕
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("💬 轉到聊天討論", use_container_width=True):
                # 自動添加一個關於此CVE的問題到聊天中
                cve_id = st.session_state.cve_report.split('**CVE ID**: ')[1].split('\n')[0] if '**CVE ID**: ' in st.session_state.cve_report else 'CVE'
                question = f"我剛查詢了{cve_id}，請提供更深入的攻擊手法分析和具體的防護建議"
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.active_tab = "chat"  # 切換到聊天標籤
                st.success(f"✅ 已將{cve_id}相關問題加入聊天，正在切換到聊天標籤")
                st.rerun()
        
        with col2:
            # 生成下載鏈接
            if st.download_button(
                label="📥 下載報告", 
                data=st.session_state.cve_report,
                file_name=f"CVE_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            ):
                st.success("✅ 報告下載完成")
        
        with col3:
            if st.button("🔄 重新分析", use_container_width=True):
                st.session_state.cve_report = None
                st.session_state.active_tab = "cve"  # 保持在CVE標籤頁
                st.info("💡 請重新輸入CVE ID進行查詢")
                st.rerun()
        
        with col4:
            if st.button("🗑️ 清除報告", use_container_width=True):
                st.session_state.cve_report = None
                st.session_state.active_tab = "cve"  # 保持在CVE標籤頁
                st.success("🗑️ 報告已清除")
                st.rerun()
        
        st.markdown("---")
        
        # 顯示完整報告
        with st.container():
            st.markdown(st.session_state.cve_report)
            
    else:
        # 當沒有報告時的提示
        st.info("🔍 尚無CVE分析報告。請在上方輸入CVE ID開始查詢。")
        
        # 顯示一些常見的CVE範例
        with st.expander("💡 點擊查看常見CVE範例"):
            st.markdown("""
            **近期重要CVE弱點：**
            - `CVE-2023-44487` - HTTP/2 Rapid Reset 攻擊
            - `CVE-2021-44228` - Apache Log4j2 遠程代碼執行（Log4Shell）
            - `CVE-2021-34527` - Windows Print Spooler 權限提升（PrintNightmare）
            - `CVE-2020-1472` - Windows Netlogon 權限提升（Zerologon）
            - `CVE-2019-0708` - Windows RDP 遠程代碼執行（BlueKeep）
            
            **使用提示：**
            - 複製上述任一CVE ID到輸入框中
            - 點擊「🔍 查詢分析」按鈕
            - 等待AI完成完整的弱點分析
            """)

# 頁腳
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    💡 提示：您可以在側邊欄管理對話設定和查看歷史記錄<br>
    🚀 由 Foundation-Sec-8B-Instruct 模型驅動
    </div>
    """, 
    unsafe_allow_html=True
)

# 添加一些樣式
st.markdown("""
<style>
    .stChat > div {
        max-height: 600px;
        overflow-y: auto;
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    
    .stButton > button {
        border-radius: 20px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)