from typing import Any, Dict
import requests
from .base import BaseLLMClient

class LMStudioClient(BaseLLMClient):
    def __init__(self, base_url: str, api_key: str, model: str = "qwen/qwen2.5-coder-32b"):
        super().__init__(model)
        self.base_url = base_url
        self.api_key = api_key

    def generate_response(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        # Only add authorization header if api_key is meaningful
        if self.api_key and self.api_key != "not-needed":
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        # Use OpenAI-compatible chat completions format
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.base_url}/v1/chat/completions", json=data, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract response from OpenAI-compatible format
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "No response generated"
                
        except requests.exceptions.Timeout:
            return "Request timed out - the model might be taking too long to respond"
        except requests.exceptions.JSONDecodeError:
            return f"Invalid JSON response from server. Raw response: {response.text[:200]}..."
        except Exception as e:
            # More detailed error information
            return f"Error generating response: {str(e)}"

    def configure(self, **kwargs: Any) -> None:
        if "base_url" in kwargs:
            self.base_url = kwargs["base_url"]
        if "api_key" in kwargs:
            self.api_key = kwargs["api_key"]
        if "model" in kwargs:
            self.model_name = kwargs["model"]

    def health_check(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

def interactive_chat():
    """Interactive chat interface for LMStudio client"""
    print("=== LMStudio Interactive Chat ===")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'config' to change settings")
    print("Type 'health' to check server health")
    print("-" * 40)
    
    # Default configuration
    base_url = input("Enter LMStudio server URL (default: http://localhost:1234): ").strip()
    if not base_url:
        base_url = "http://localhost:1234"
    
    api_key = input("Enter API key (press Enter if none required): ").strip()
    if not api_key:
        api_key = "not-needed"
    
    model = input("Enter model name (default: qwen/qwen2.5-coder-32b): ").strip()
    if not model:
        model = "qwen/qwen2.5-coder-32b"
    
    # Initialize client
    try:
        client = LMStudioClient(base_url=base_url, api_key=api_key, model=model)
        print(f"\n✅ LMStudio client initialized!")
        print(f"Server: {base_url}")
        print(f"Model: {model}")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return
    
    while True:
        try:
            user_input = input("\n🤖 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'config':
                print("\n=== Configuration ===")
                new_url = input(f"Server URL (current: {client.base_url}): ").strip()
                new_key = input(f"API Key (current: {client.api_key}): ").strip()
                new_model = input(f"Model (current: {client.model_name}): ").strip()
                
                config_kwargs = {}
                if new_url:
                    config_kwargs["base_url"] = new_url
                if new_key:
                    config_kwargs["api_key"] = new_key
                if new_model:
                    config_kwargs["model"] = new_model
                
                if config_kwargs:
                    client.configure(**config_kwargs)
                    print("✅ Configuration updated!")
                continue
            
            elif user_input.lower() == 'health':
                try:
                    health = client.health_check()
                    print(f"🟢 Server Health: {health}")
                except Exception as e:
                    print(f"🔴 Health check failed: {e}")
                continue
            
            elif not user_input:
                print("Please enter a message or command.")
                continue
            
            # Generate AI response
            print("🤔 AI is thinking...")
            try:
                response = client.generate_response(user_input)
                print(f"🤖 AI: {response}")
            except requests.exceptions.ConnectionError:
                print("❌ Connection Error: Unable to connect to LMStudio server.")
                print("Please make sure LMStudio is running and the server URL is correct.")
            except requests.exceptions.HTTPError as e:
                print(f"❌ HTTP Error: {e}")
                print("Please check your API key and server configuration.")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    interactive_chat()