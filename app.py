import transformers
import torch
import re
import os

# export Huggfing Face token to HF_TOKEN
HF_TOKEN = os.getenv("HF_TOKEN")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", DEVICE)

MODEL_ID = "fdtn-ai/Foundation-Sec-8B-Instruct" # To be relaced with the final model name

from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=MODEL_ID,
    device_map="auto",
    torch_dtype=torch.bfloat16, # this model's tensor_type is BF16
    token=HF_TOKEN,
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

SYSTEM_PROMPT = "You are a cybersecurity expert."

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