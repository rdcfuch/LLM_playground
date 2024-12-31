from pathlib import Path
from openai import OpenAI
import json

KIMI_MODEL = "moonshot-v1-8k"
Ollama_MODEL = "llama3.2:latest"
KIMI_API_KEY = 'sk-e2elzR10u4Tv2UXxx9kYC6Te0OrzM87qlpgHJsWVjzHd6Ouw'

client = OpenAI(
    api_key=KIMI_API_KEY,  # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
    base_url="https://api.moonshot.cn/v1",

)

# moonshot.pdf 是一个示例文件, 我们支持文本文件和图片文件，对于图片文件，我们提供了 OCR 的能力
# 上传文件时，我们可以直接使用 openai 库的文件上传 API，使用标准库 pathlib 中的 Path 构造文件
# 对象，并将其传入 file 参数即可，同时将 purpose 参数设置为 file-extract；注意，目前文件上传
# 接口仅支持 file-extract 一种 purpose 值。
file_object = client.files.create(file=Path("/Users/fcfu/Downloads/aa.txt"), purpose="file-extract")

# 获取结果
# file_content = client.files.retrieve_content(file_id=file_object.id)
# 注意，某些旧版本示例中的 retrieve_content API 在最新版本标记了 warning, 可以用下面这行代替
# （如果使用旧版本的 SDK，可以继续延用 retrieve_content API）
file_content = client.files.content(file_id=file_object.id).text

# 把文件内容通过系统提示词 system prompt 放进请求中
messages = [
    {
        "role": "system",
        "content": "你是人工智能助手，你更擅长中文和英文的对话,并且回答问题",
    },
    {
        "role": "system",
        "content": file_content,  # <-- 这里，我们将抽取后的文件内容（注意是文件内容，而不是文件 ID）放置在请求中
    },
    # {"role": "user", "content": "what is the secret code"},
]

while True:
    # 然后调用 chat-completion, 获取 Kimi 的回答
    user_input = input("User:> ")
    messages.append({"role": "user", "content": user_input})
    stream = client.chat.completions.create(
        model=KIMI_MODEL,
        messages=messages,
        temperature=0.9,
        stream=True,
    )
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
    messages.append({"role":"assistant","content": response})
