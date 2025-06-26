from typing import Any, Dict
import requests
from .base import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(model)
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def generate_response(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract response from OpenAI format
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "No response generated"
                
        except requests.exceptions.Timeout:
            return "Request timed out - OpenAI API might be slow"
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return "Authentication failed - please check your API key"
            elif response.status_code == 429:
                return "Rate limit exceeded - please try again later"
            elif response.status_code == 400:
                return f"Bad request - check your model name and parameters. Error: {e}"
            else:
                return f"HTTP Error {response.status_code}: {e}"
        except requests.exceptions.JSONDecodeError:
            return f"Invalid JSON response from OpenAI. Raw response: {response.text[:200]}..."
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def configure(self, **kwargs: Any) -> None:
        if "api_key" in kwargs:
            self.api_key = kwargs["api_key"]
        if "model" in kwargs:
            self.model_name = kwargs["model"]
        if "base_url" in kwargs:
            self.base_url = kwargs["base_url"]

    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to list models: {str(e)}"}

    def validate_api_key(self) -> bool:
        """Validate the API key"""
        try:
            models = self.list_models()
            return "error" not in models
        except Exception:
            return False

def interactive_chat():
    """Interactive chat interface for OpenAI client"""
    print("=== OpenAI Interactive Chat ===")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'config' to change settings")
    print("Type 'models' to list available models")
    print("Type 'validate' to check API key")
    print("-" * 40)
    
    # Get API key
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ API key is required for OpenAI")
        return
    
    # Get model
    model = input("Enter model name (default: gpt-3.5-turbo): ").strip()
    if not model:
        model = "gpt-3.5-turbo"
    
    # Initialize client
    try:
        client = OpenAIClient(api_key=api_key, model=model)
        print(f"\n✅ OpenAI client initialized!")
        print(f"Model: {model}")
        
        # Validate API key
        print("🔑 Validating API key...")
        if client.validate_api_key():
            print("✅ API key is valid!")
        else:
            print("⚠️ API key validation failed - you may encounter issues")
        
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
                new_key = input(f"API Key (current: {'*' * len(client.api_key)}): ").strip()
                new_model = input(f"Model (current: {client.model_name}): ").strip()
                new_url = input(f"Base URL (current: {client.base_url}): ").strip()
                
                config_kwargs = {}
                if new_key:
                    config_kwargs["api_key"] = new_key
                if new_model:
                    config_kwargs["model"] = new_model
                if new_url:
                    config_kwargs["base_url"] = new_url
                
                if config_kwargs:
                    client.configure(**config_kwargs)
                    print("✅ Configuration updated!")
                continue
            
            elif user_input.lower() == 'models':
                try:
                    models = client.list_models()
                    if "data" in models:
                        model_names = [model["id"] for model in models["data"][:10]]  # Show first 10
                        print(f"📋 Available Models (first 10): {', '.join(model_names)}")
                    else:
                        print(f"📋 Models response: {models}")
                except Exception as e:
                    print(f"🔴 Failed to list models: {e}")
                continue
            
            elif user_input.lower() == 'validate':
                try:
                    if client.validate_api_key():
                        print("✅ API key is valid!")
                    else:
                        print("❌ API key is invalid!")
                except Exception as e:
                    print(f"🔴 Validation failed: {e}")
                continue
            
            elif not user_input:
                print("Please enter a message or command.")
                continue
            
            # Generate AI response
            print("🤔 AI is thinking...")
            response = client.generate_response(user_input)
            print(f"🤖 AI: {response}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    interactive_chat()