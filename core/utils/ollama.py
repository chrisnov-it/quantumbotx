import requests

def ask_ollama(prompt, model="qwen2.5-coder:1.5b"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception during AI call: {e}"
