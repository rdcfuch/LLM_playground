#!/usr/bin/env python3
import requests
import json

def test_ollama_connection():
    base_url = "http://localhost:11434"
    
    print("Testing Ollama connection...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        print(f"Server status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Available models: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama server at localhost:11434")
        print("Make sure Ollama is running with: ollama serve")
        return False
    except requests.exceptions.Timeout:
        print("ERROR: Connection timeout")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Test 2: Try a simple generation request
    try:
        test_data = {
            "model": "qwen3:8b",
            "prompt": "Hello, how are you?",
            "stream": False
        }
        
        print("\nTesting generation endpoint...")
        response = requests.post(f"{base_url}/api/generate", 
                               json=test_data, 
                               timeout=30)
        
        print(f"Generation status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')}")
        else:
            print(f"Generation error: {response.text}")
            
    except Exception as e:
        print(f"Generation test failed: {e}")
    
    return True

if __name__ == "__main__":
    test_ollama_connection()