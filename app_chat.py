# Removed IPython imports as they are not needed for terminal display
import transformers
import torch
import re
import os

# 導入CVE分析器和模型配置
from cve_analyzer import CVEAnalyzer
from model_config import get_model_config, print_model_info

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", DEVICE)

# 獲取模型配置
MODEL_PATH, NEED_TOKEN, HF_TOKEN = get_model_config()
print_model_info()

from transformers import AutoModelForCausalLM, AutoTokenizer

# 根據配置載入模型和tokenizer
if NEED_TOKEN:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=MODEL_PATH,
        device_map="auto",
        torch_dtype=torch.bfloat16, # this model's tensor_type is BF16
        token=HF_TOKEN,
    )
else:
    print("📂 使用本地模型，不需要HF_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=MODEL_PATH,
        device_map="auto",
        torch_dtype=torch.bfloat16, # this model's tensor_type is BF16
    )

generation_args = {
    "max_new_tokens": 1024,
    "temperature": None,
    "repetition_penalty": 1.2,
    "do_sample": False,
    "use_cache": True,
    "eos_token_id": tokenizer.eos_token_id,
    "pad_token_id": tokenizer.pad_token_id,
}

DEFAULT_SYSTEM_PROMPT = "你是一位專業的網路安全專家。請務必使用繁體中文回答所有問題，提供專業、詳細且實用的網路安全建議和解決方案。"

def inference(request, system_prompt = DEFAULT_SYSTEM_PROMPT):
    
    if isinstance(request, str):
        messages =  [
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

    inputs = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    inputs = tokenizer(inputs, return_tensors="pt")
    input_ids = inputs["input_ids"].to(DEVICE)
    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            **generation_args,
        )
    response = tokenizer.decode(
        outputs[0][input_ids.shape[1]:],  # Only get new tokens
        skip_special_tokens = False
    )
    
    if response.endswith(tokenizer.eos_token):
        response = response[:-len(tokenizer.eos_token)]
    
    return response

class ChatApp():
    
    def __init__(self, system_message = DEFAULT_SYSTEM_PROMPT):
        self.system_message = system_message
        self.messages = [{"role": "system", "content": self.system_message}]
        # 初始化CVE分析器
        self.cve_analyzer = CVEAnalyzer(inference_function=inference)

    def chat(self):
        print("-" * 40)
        print("Type 'quit', 'exit', or 'q' to end the conversation")
        print("Type 'clear' to clear conversation history")
        print("Type 'history' to see conversation history")
        print("Type 'cve <CVE-ID>' to query and analyze a specific CVE")
        print("Type 'help' to show all available commands")
        print("-" * 40)
        print("🤖 Chat begins")

        while True:
            try:
                user_input = input("\n💬 You: ").strip()
    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.messages = [{"role": "system", "content": self.system_message}]
                    print("🧹 Conversation history cleared!")
                    continue
                elif user_input.lower() == 'history':
                    if self.messages:
                        print("\n==========📜 Conversation History 📜==========")
                        for message in self.messages:
                            print(message.get("role", "Unknown").title(),":", message.get("content", "N/A"), "\n")
                        print("========== End of Conversation History ==========")
                    else:
                        print("📜 No conversation history yet.")
                    continue
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower().startswith('cve '):
                    cve_id = user_input[4:].strip()
                    if cve_id:
                        self._handle_cve_query(cve_id)
                    else:
                        print("⚠️  請提供CVE ID，例如: cve CVE-2023-44487")
                    continue                   
                elif not user_input:
                    print("❌ Please enter a message.")
                    continue
    
                print("\n🤔 Thinking...")
                self.messages.append({"role": "user", "content": user_input})
                response = inference(self.messages)
    
                print("\n🤖 Assistant: ")
                print(response)
                self.messages.append({"role": "assistant", "content": response})
            
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
    
    def _show_help(self):
        """顯示幫助資訊"""
        print("\n" + "="*50)
        print("📚 可用命令列表")
        print("="*50)
        print("• quit / exit / q     - 結束對話")
        print("• clear              - 清除對話歷史")
        print("• history            - 顯示對話歷史")
        print("• help               - 顯示此幫助資訊")
        print("• cve <CVE-ID>       - 查詢並分析指定的CVE")
        print("  例如: cve CVE-2023-44487")
        print("• <其他輸入>          - 正常對話")
        print("="*50)
    
    def _handle_cve_query(self, cve_id):
        """處理CVE查詢"""
        print(f"\n🔍 正在查詢 {cve_id}...")
        
        try:
            report = self.cve_analyzer.query_and_analyze(cve_id)
            
            if report:
                print(f"\n✅ 成功查詢 {cve_id}")
                print("\n" + "="*60)
                print("📊 CVE分析報告")
                print("="*60)
                
                # 將報告輸出到終端
                # 移除Markdown格式中的#符號用於更好的終端顯示
                terminal_report = report.replace('#', '').replace('**', '')
                print(terminal_report)
                
                print("="*60)
                
                # 詢問用戶是否要將此CVE加入對話中進行進一步討論
                while True:
                    follow_up = input(f"\n💬 是否要將{cve_id}加入對話中進行進一步討論？ (y/n): ").lower().strip()
                    if follow_up in ['y', 'yes', '是']:
                        question = f"我剛才查詢了{cve_id}的詳細資訊，請根據這個CVE的特性，提供更深入的分析和具體的防護建議。"
                        self.messages.append({"role": "user", "content": question})
                        print(f"\n✅ 已將{cve_id}相關問題加入對話中")
                        
                        # 立即生成回應
                        print("\n🤔 Thinking...")
                        response = inference(self.messages)
                        print("\n🤖 Assistant: ")
                        print(response)
                        self.messages.append({"role": "assistant", "content": response})
                        break
                    elif follow_up in ['n', 'no', '否']:
                        print("👍 好的，CVE查詢完成")
                        break
                    else:
                        print("⚠️  請輸入 y(是) 或 n(否)")
                        
            else:
                print(f"❌ 查詢失敗：找不到 {cve_id}，請檢查CVE ID是否正確")
                
        except Exception as e:
            print(f"❌ CVE查詢過程發生錯誤: {str(e)}")
            print("💡 請檢查網路連接是否正常，或稍後再試")

chatapp = ChatApp()
chatapp.chat()