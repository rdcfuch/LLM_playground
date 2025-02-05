import requests
import json
from typing import List, Dict, Optional, Union

class QwenAgent:
    def __init__(self, api_key: str = None):
        self.url = "https://chat.qwenlm.ai/api/chat/completions"
        # Use provided API key or default to the one from the original code
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImM5MzAwOGE5LTQwZGMtNDNjNS1hNTQ3LTFhYTBlMDFiNDMwMSIsImV4cCI6MTc0MDY5NTI5OH0.kkmIk234bKBDdGwm_9Y8cdA3jEISpCsFggdCuJjUmuA"
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {self.api_key}",
            "bx-v": "2.5.0",
            "Content-Type": "application/json",
            "Origin": "https://chat.qwenlm.ai",
            "Referer": "https://chat.qwenlm.ai/?spm=5aebb161.2ef5001f.0.0.8f5cc921CFI3do",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
        }
        self.session_id = "eb66e038-2033-42e3-a4a6-2f3eaf8c65e1"
        self.chat_id = "659690b7-7ae7-4d52-8203-4cf2015c89e0"
        self.model = "qwen-max-latest"
        self.messages: List[Dict] = []

    def chat_stream(self, messages: List[Dict]) -> Optional[str]:
        """Send a chat request to Qwen API with streaming response"""
        payload = {
            "stream": True,
            "chat_type": "t2t",
            "model": self.model,
            "messages": messages,
            "session_id": self.session_id,
            "chat_id": self.chat_id,
            "id": "3a264886-69cc-4044-b40e-072e48a6f85a",
            "chat_type": "search"
        }

        try:
            with requests.post(self.url, headers=self.headers, json=payload, stream=True) as response:
                if response.status_code == 200:
                    content_buffer = ""
                    for line in response.iter_lines(decode_unicode=True):
                        if line:
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    json_data = json.loads(data_str)
                                    if "content" in json_data["choices"][0]["delta"]:
                                        content = json_data["choices"][0]["delta"]["content"]
                                        content_buffer += content + "|"
                                except json.JSONDecodeError:
                                    pass
                    last_msg = content_buffer.split("|")[-2]  # Get final message only
                    return last_msg
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return None

    def chat(self, message: str) -> Optional[str]:
        """Send a single message and get response"""
        self.messages.append({"role": "user", "content": message, "extra": {}})
        response = self.chat_stream(self.messages)
        if response:
            self.messages.append({"role": "assistant", "content": response, "extra": {}})
        return response

    def reset_conversation(self):
        """Clear the conversation history"""
        self.messages = []

    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history"""
        return self.messages

def main():
    # Example usage
    agent = QwenAgent()
    print("Welcome to Qwen Chat! Type 'quit' to exit.\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() == 'quit':
            print("\nGoodbye!")
            break

        response = agent.chat(user_input)
        if response:
            print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
