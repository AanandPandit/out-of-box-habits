import requests
import json
import os
import re

# Updated API Key and Model
# Using the key provided by user in history as default if env not set
DEFAULT_KEY = "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"

def ask_perplexity(prompt: str, history: list = None) -> str:
    """
    Sends a prompt to the Perplexity API and returns the response.
    """
    # Get API key at runtime
    api_key = os.getenv("PERPLEXITY_API_KEY", DEFAULT_KEY)
    
    if not api_key:
        return "Error: Perplexity API Key not configured."

    url = "https://api.perplexity.ai/chat/completions"
    
    # Prepare messages
    messages = []
    if history:
        for msg in history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({"role": msg['role'], "content": msg['content']})
    
    # If no history or just starting, add system prompt if not present
    if not messages or messages[0]['role'] != 'system':
        messages.insert(0, {"role": "system", "content": "You are a helpful, hacker-themed AI assistant. Be precise and concise."})
        
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "sonar",
        "messages": messages
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            error_detail = response.text
            return f"Error: API Request Failed {response.status_code} - {error_detail}"
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            # Post-processing: Remove citation markers like [1], [2]
            clean_content = re.sub(r'\[\d+\]', '', content)
            return clean_content.strip()
        else:
            return "Error: No response content from AI."
            
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test
    print(ask_perplexity("How many stars are there in our galaxy?"))
