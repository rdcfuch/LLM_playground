#!/usr/bin/env python3
import requests
import json

try:
    # Test the Ollama API
    url = 'http://localhost:11434/api/generate'
    data = {
        'model': 'qwen3:8b',
        'prompt': 'Hello, how are you?',
        'stream': False
    }
    
    print("Testing Ollama API connection...")
    print(f"URL: {url}")
    print(f"Model: {data['model']}")
    
    response = requests.post(url, json=data, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success! Ollama is working correctly.")
        print(f"Response: {result.get('response', 'No response field')[:100]}...")
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Cannot connect to Ollama server")
    print("Make sure Ollama is running with: ollama serve")
except requests.exceptions.Timeout:
    print("❌ Timeout Error: Request took too long")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")