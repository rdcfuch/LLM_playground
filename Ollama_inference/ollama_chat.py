import ollama
from openai import OpenAI

MODEL = "llama3.2"
SYS_PROMPT = {
    "role": "system",
    "content": """
        ## role
        you are a prompt expert who can help to add tags to a prompt

        ## skill
        you will review the input prompt and add key tags to it based on its contents

        ## constraints
        - you will output the prompt according to the example format
        - you only output the prompt, don't output any other information

        ## example
        input prompt: "This video depicts a cat with brown hairs and a white apron washing dishes with its paws, 
                        we can see the head of the cat, the water is flowing rapidly, the dish is white and made of china, 
                        the background is a kitchen, the cat looks very happy"
        output prompt: caption: [
  {
    "description": "This video depicts a cat with brown hairs and a white apron washing dishes with its paws, we can see the head of the cat, the water is flowing rapidly, the dish is white and made of china, the background is a kitchen, the cat looks very happy",
    "tags": [
      "cat",
      "dishwashing",
      "faucet",
      "kitchen"
    ]
  }
]
    """
}

def prompt_rewrite(input_msg):
    user_messages = [
        SYS_PROMPT,
        {"role": "user", "content": input_msg}
    ]
    client = OpenAI(base_url='http://127.0.0.1:11434/v1',api_key="test")
    stream = client.chat.completions.create(
        model=MODEL,
        messages=user_messages,
        # stream=True  # Enable streaming
    )
    # Initialize a list to collect the streamed content
    response = []
    for chunk in stream:
        # 在这里，每个 chunk 的结构都与之前的 completion 相似，但 message 字段被替换成了 delta 字段
        delta = chunk.choices[0].delta  # <-- message 字段被替换成了 delta 字段

        if delta.content:
            # 我们在打印内容时，由于是流式输出，为了保证句子的连贯性，我们不人为地添加
            # 换行符，因此通过设置 end="" 来取消 print 自带的换行符。
            print(delta.content, end="")
            response.append(delta.content)
    # messages.append(completion.choices[0].message)
    # print(completion.choices[0].message.content)
    response = "".join(response)
    # print(response)
    return response_message

if __name__ == '__main__':
    summary = prompt_rewrite(
        "generate new prompt for 'A mystical forest with ancient trees twisted into intricate shapes, glowing mushrooms illuminating the path, and mythical creatures roaming freely.'"
    )
    print("\nFull response received:")
    print(summary)
