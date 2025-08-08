import os

# 模型配置文件
# 您可以在這裡設定使用本地模型或遠端模型

# ========== 配置選項 ==========

# 選項1: 使用本地模型 (推薦，如果您已經下載模型)
USE_LOCAL_MODEL = False  # 設為True使用本地模型，False使用遠端模型

# 本地模型路徑 (如果USE_LOCAL_MODEL=True)
# 請修改為您的實際模型路徑，例如: "/home/user/models/Foundation-Sec-8B-Instruct"
LOCAL_MODEL_PATH = "/path/to/your/local/model"

# 遠端模型ID (如果USE_LOCAL_MODEL=False)
REMOTE_MODEL_ID = "fdtn-ai/Foundation-Sec-8B-Instruct"

# ========== 自動配置 ==========

def get_model_config():
    """
    根據配置返回模型相關設定
    
    Returns:
        tuple: (model_path_or_id, need_token, token)
    """
    
    if USE_LOCAL_MODEL:
        # 使用本地模型
        if not os.path.exists(LOCAL_MODEL_PATH):
            raise FileNotFoundError(f"本地模型路徑不存在: {LOCAL_MODEL_PATH}")
        
        return LOCAL_MODEL_PATH, False, None
    
    else:
        # 使用遠端模型
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("⚠️  警告: 使用遠端模型但未設定HF_TOKEN環境變數")
            print("    如果模型是私有的，可能會下載失敗")
        
        return REMOTE_MODEL_ID, True, hf_token

def print_model_info():
    """顯示當前模型配置資訊"""
    model_path, need_token, token = get_model_config()
    
    print("=" * 50)
    print("🤖 模型配置資訊")
    print("=" * 50)
    
    if USE_LOCAL_MODEL:
        print(f"📂 使用本地模型: {model_path}")
        print(f"🔑 需要HF_TOKEN: 否")
        print(f"✅ 模型路徑存在: {os.path.exists(model_path)}")
    else:
        print(f"🌐 使用遠端模型: {model_path}")
        print(f"🔑 需要HF_TOKEN: 是")
        print(f"✅ HF_TOKEN已設定: {'是' if token else '否'}")
    
    print("=" * 50)

# 快速配置函數
def setup_local_model(model_path: str):
    """
    快速設定本地模型
    
    Args:
        model_path (str): 本地模型路徑
    """
    global USE_LOCAL_MODEL, LOCAL_MODEL_PATH
    USE_LOCAL_MODEL = True
    LOCAL_MODEL_PATH = model_path
    print(f"✅ 已設定使用本地模型: {model_path}")

def setup_remote_model(model_id: str = None):
    """
    快速設定遠端模型
    
    Args:
        model_id (str, optional): 遠端模型ID，預設使用既有設定
    """
    global USE_LOCAL_MODEL, REMOTE_MODEL_ID
    USE_LOCAL_MODEL = False
    if model_id:
        REMOTE_MODEL_ID = model_id
    print(f"✅ 已設定使用遠端模型: {REMOTE_MODEL_ID}")

if __name__ == "__main__":
    # 顯示當前配置
    print_model_info()
