# Removed IPython imports as they are not needed for terminal display
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

DEFAULT_SYSTEM_PROMPT = "You are a cybersecurity expert."

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

    def chat(self):
        print("-" * 40)
        print("Type 'quit', 'exit', or 'q' to end the conversation")
        print("Type 'clear' to clear conversation history")
        print("Type 'history' to see conversation history")
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

chatapp = ChatApp()
chatapp.chat()