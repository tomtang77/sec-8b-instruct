import transformers
import torch
import re
import os

# 導入模型配置
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

SYSTEM_PROMPT = "你是一位專業的網路安全專家。請務必使用繁體中文回答所有問題，提供專業、詳細且實用的網路安全建議和解決方案。"

def inference(prompt):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    inputs = tokenizer(inputs, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            **generation_args,
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens = False)
    
    # extract the assistant response part only
    match = re.search(r"<\|assistant\|>(.*?)<\|end_of_text\|>", response, re.DOTALL)
    
    return match.group(1).strip()

#print(inference("What is MITRE ATT&CK? Give a very brief answer"))
print(inference("What is MITRE ATT&CK? Give a detailed answer"))