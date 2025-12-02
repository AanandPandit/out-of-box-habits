import requests
import json
import os

# Updated API Key and Model
API_KEY = os.environ.get("PERPLEXITY_API_KEY", "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")
API_URL = "https://api.perplexity.ai/chat/completions"
# Using 'sonar-pro' as 'llama-3.1-sonar-small-128k-online' is deprecated by Dec 2025
MODEL_NAME = "sonar-pro" 

def ask_perplexity(prompt: str, history: list = None) -> str:
    """
    Sends a prompt to the Perplexity API and returns the response.
    """
    if not history:
        history = []

    messages = [
        {"role": "system", "content": "You are a helpful, hacker-themed AI assistant. Keep answers concise and technical."}
    ]
    
    # Add history context
    for msg in history:
        messages.append(msg)
        
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        return f"Error: API Request Failed. {e}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test
    print(ask_perplexity("Hello, system check."))
