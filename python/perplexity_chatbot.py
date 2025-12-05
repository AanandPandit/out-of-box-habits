import requests
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def ask_perplexity(prompt: str, history: list = None) -> str:
    """
    Sends a prompt to the Perplexity API and returns the response.
    """
    # Get API key at runtime
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        return "Error: Perplexity API Key not configured."

    url = "https://api.perplexity.ai/chat/completions"
    
    # Prepare messages
    raw_messages = []
    
    # Add system prompt first
    raw_messages.append({"role": "system", "content": "You are a helpful, hacker-themed AI assistant. Be precise and concise."})
    
    # Add history
    if history:
        for msg in history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                raw_messages.append({"role": msg['role'], "content": msg['content']})
    
    # Add current prompt if not already the last message
    if not raw_messages or raw_messages[-1]['role'] != 'user' or raw_messages[-1]['content'] != prompt:
        raw_messages.append({"role": "user", "content": prompt})
        
    # Sanitize messages to enforce alternation (System -> User -> Assistant -> User ...)
    sanitized_messages = []
    if raw_messages and raw_messages[0]['role'] == 'system':
        sanitized_messages.append(raw_messages.pop(0))
        
    for msg in raw_messages:
        if not sanitized_messages:
            if msg['role'] == 'user':
                sanitized_messages.append(msg)
            continue
            
        last_role = sanitized_messages[-1]['role']
        if msg['role'] == last_role:
            # Merge content if same role (to avoid 400 error)
            sanitized_messages[-1]['content'] += f"\n\n{msg['content']}"
        else:
            sanitized_messages.append(msg)
            
    # Ensure the last message is from user (to trigger a response)
    if sanitized_messages and sanitized_messages[-1]['role'] == 'assistant':
        # This shouldn't happen if we added prompt, but just in case history was weird
        sanitized_messages.append({"role": "user", "content": "Continue."})

    payload = {
        "model": "sonar",
        "messages": sanitized_messages
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
            
    except requests.exceptions.ConnectionError:
        return "⚠ OFFLINE: Please connect to the internet to establish uplink."
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test
    print(ask_perplexity("How many stars are there in our galaxy?"))
