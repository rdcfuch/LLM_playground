from typing import Any, Dict
import requests
from .base import BaseLLMClient

class OllamaClient(BaseLLMClient):
    def __init__(self, base_url: str, model: str = "llama2"):
        super().__init__(model)
        self.base_url = base_url

    def generate_response(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use Ollama's correct API format
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=data, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Extract response from Ollama format
            if "response" in result:
                return result["response"].strip()
            else:
                return "No response generated"
                
        except requests.exceptions.Timeout:
            return "Request timed out - the model might be taking too long to respond"
        except requests.exceptions.JSONDecodeError:
            return f"Invalid JSON response from server. Raw response: {response.text[:200]}..."
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def configure(self, **kwargs: Any) -> None:
        if "base_url" in kwargs:
            self.base_url = kwargs["base_url"]
        if "model" in kwargs:
            self.model_name = kwargs["model"]

    def get_model_info(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to get model info: {str(e)}"}

    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to list models: {str(e)}"}

def interactive_chat():
    """Interactive chat interface for Ollama client"""
    print("=== Ollama Interactive Chat ===")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'config' to change settings")
    print("Type 'models' to list available models")
    print("Type 'info' to get model information")
    print("-" * 40)
    
    # Default configuration
    base_url = input("Enter Ollama server URL (default: http://localhost:11434): ").strip()
    if not base_url:
        base_url = "http://localhost:11434"
    
    model = input("Enter model name (default: llama2): ").strip()
    if not model:
        model = "llama2"
    
    # Initialize client
    try:
        client = OllamaClient(base_url=base_url, model=model)
        print(f"\n✅ Ollama client initialized!")
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
                new_model = input(f"Model (current: {client.model_name}): ").strip()
                
                config_kwargs = {}
                if new_url:
                    config_kwargs["base_url"] = new_url
                if new_model:
                    config_kwargs["model"] = new_model
                
                if config_kwargs:
                    client.configure(**config_kwargs)
                    print("✅ Configuration updated!")
                continue
            
            elif user_input.lower() == 'models':
                try:
                    models = client.list_models()
                    print(f"📋 Available Models: {models}")
                except Exception as e:
                    print(f"🔴 Failed to list models: {e}")
                continue
            
            elif user_input.lower() == 'info':
                try:
                    info = client.get_model_info()
                    print(f"ℹ️ Model Info: {info}")
                except Exception as e:
                    print(f"🔴 Failed to get model info: {e}")
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
                print("❌ Connection Error: Unable to connect to Ollama server.")
                print("Please make sure Ollama is running and the server URL is correct.")
            except requests.exceptions.HTTPError as e:
                print(f"❌ HTTP Error: {e}")
                print("Please check your server configuration and model name.")
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