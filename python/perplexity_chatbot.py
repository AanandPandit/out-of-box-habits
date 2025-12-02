import requests
import json
import os
import re

# Updated API Key and Model
API_KEY = os.environ.get("PERPLEXITY_API_KEY", "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")
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL_NAME = "sonar" # User example used sonar-deep-research, but sonar is faster for chat. 
                     # I will use 'sonar' as it is the standard chat model, but keep the payload simple.

def ask_perplexity(prompt: str, history: list = None) -> str:
    """
    Sends a prompt to the Perplexity API and returns the response.
    """
    if not history:
        history = []

    messages = [
        {"role": "system", "content": "You are a helpful, hacker-themed AI assistant. Be precise and concise."}
    ]
    
    # Add history context
    for msg in history:
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            messages.append({"role": msg['role'], "content": msg['content']})
        
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        # Post-processing: Remove citation markers like [1], [2], etc.
        clean_content = re.sub(r'\[\d+\]', '', content)
        return clean_content.strip()
        
    except requests.exceptions.HTTPError as e:
        return f"Error: API Request Failed. {e}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test
    print(ask_perplexity("How many stars are there in our galaxy?"))
