import requests
import json

def chat_stream(messages):
    url = "https://chat.qwenlm.ai/api/chat/completions"
    
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImM5MzAwOGE5LTQwZGMtNDNjNS1hNTQ3LTFhYTBlMDFiNDMwMSIsImV4cCI6MTc0MDY5NTI5OH0.kkmIk234bKBDdGwm_9Y8cdA3jEISpCsFggdCuJjUmuA",
        "bx-v": "2.5.0",
        "Content-Type": "application/json",
        "Origin": "https://chat.qwenlm.ai",
        "Referer": "https://chat.qwenlm.ai/?spm=5aebb161.2ef5001f.0.0.8f5cc921CFI3do",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
        "x-request-id": "a902f00b-7df4-477b-bdc5-c6442b1b0e93"
    }

    payload = {
        "stream": True,
        "chat_type": "t2t",
        "model": "qwen-max-latest",
        "messages": messages,
        "session_id": "eb66e038-2033-42e3-a4a6-2f3eaf8c65e1",
        "chat_id": "659690b7-7ae7-4d52-8203-4cf2015c89e0",
        "id": "3a264886-69cc-4044-b40e-072e48a6f85a"
    }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
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
                # print("content: ",content_buffer)
                print(last_msg)
                return last_msg
            else:
                print(f"Request failed with status code: {response.status_code}")
                return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None

def main():
    messages = []
    print("Welcome to Qwen Chat! Type 'quit' to exit.\n")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() == 'quit':
            print("\nGoodbye!")
            break
            
        # Add user message to history
        messages.append({"role": "user", "content": user_input, "extra": {}})
        
        # Get AI response
        ai_response = chat_stream(messages)
        if ai_response:
            # Add AI response to history
            messages.append({"role": "assistant", "content": ai_response, "extra": {}})

if __name__ == "__main__":
    main()