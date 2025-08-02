import streamlit as st
import sys
import os

# 為了避免導入app_chat.py時執行底部的聊天循環，我們直接複製需要的代碼
import transformers
import torch
import re
import os

# export Huggfing Face token to HF_TOKEN
HF_TOKEN = os.getenv("HF_TOKEN")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_ID = "fdtn-ai/Foundation-Sec-8B-Instruct"

from transformers import AutoModelForCausalLM, AutoTokenizer

# 只有在還沒有載入模型時才載入（避免重複載入）
if 'tokenizer' not in st.session_state:
    with st.spinner("🔄 正在載入模型..."):
        st.session_state.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
        st.session_state.model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=MODEL_ID,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            token=HF_TOKEN,
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

DEFAULT_SYSTEM_PROMPT = "You are a cybersecurity expert."

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

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# 側邊欄設定
with st.sidebar:
    st.title("⚙️ 設定")
    
    # 系統提示詞設定
    # new_system_prompt = st.text_area(
    #     "系統提示詞", 
    #     value=st.session_state.system_prompt,
    #     height=100,
    #     help="設定AI助手的角色和行為"
    # )
    
    # if st.button("🔄 更新系統提示詞"):
    #     st.session_state.system_prompt = new_system_prompt
    #     st.session_state.messages[0] = {"role": "system", "content": new_system_prompt}
    #     st.success("系統提示詞已更新！")
    #     st.rerun()
    
    # st.divider()
    
    # 對話管理按鈕
    if st.button("🧹 清除對話歷史", type="secondary"):
        st.session_state.messages = [{"role": "system", "content": st.session_state.system_prompt}]
        st.success("對話歷史已清除！")
        st.rerun()
    
    # 顯示對話統計
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
    
    st.metric("用戶訊息數", len(user_messages))
    st.metric("助手回應數", len(assistant_messages))
    
    # 歷史記錄展開/收合
    with st.expander("📜 查看對話歷史"):
        for i, message in enumerate(st.session_state.messages):
            if message["role"] != "system":
                role_icon = "💬" if message["role"] == "user" else "🤖"
                st.text(f"{role_icon} {message['role'].title()}: {message['content'][:100]}{'...' if len(message['content']) > 100 else ''}")

# 主要內容區域
st.title("🤖 網路安全專家聊天助手")
st.markdown("歡迎使用網路安全專家AI助手！您可以詢問任何關於網路安全的問題。")

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
                
            except Exception as e:
                st.error(f"❌ 發生錯誤: {str(e)}")
                st.info("請檢查模型是否正確載入，或者網路連接是否正常。")

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