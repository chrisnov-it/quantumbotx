# core/ai/ollama_client.py

import ollama

def ask_ollama(prompt, model="qwen2.5-coder:1.5b"):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"
