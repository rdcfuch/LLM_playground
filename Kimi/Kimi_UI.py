import gradio as gr
from openai import OpenAI
import bs4
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import WebBaseLoader, SeleniumURLLoader, TextLoader, PyPDFLoader
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain.llms import Ollama
from pathlib import Path
from firecrawl_url_extract import get_url_content

import ollama

# 1. Load the data
# loader = WebBaseLoader(
#     web_paths=("https://ollama.com/blog/llama-3-is-not-very-censored",),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             class_=("post-content", "post-title", "post-header")
#         )
#     ),
# )


KIMI_MODEL = "moonshot-v1-8k"
Ollama_MODEL = "llama3.2:latest"
KIMI_API_KEY = 'sk-e2elzR10u4Tv2UXxx9kYC6Te0OrzM87qlpgHJsWVjzHd6Ouw'
KIMI_API_URL = "https://api.moonshot.cn/v1"

# input_urls = ["https://ollama.com/blog/llama-3-is-not-very-censored"]
# base_ollama_url = "http://127.0.0.1:11434/v1"
# embedding_ollama_url = "http://127.0.0.1:11434/api/embeddings"
# llm_model = "llama3.2:latest"
# embedding_model = "nomic-embed-text:latest"
client = OpenAI(
    # base_url = 'http://192.168.1.199:11434/v1',
    base_url=KIMI_API_URL,  # <<<<< you need to do the port mapping kuberate desktop in VScode
    api_key=KIMI_API_KEY  # required, but unused
)

msg_history = []

"""NOTE: you must pull the embedding model: ollama pull nomic-embed-text"""


def get_file_type(filepath):
    """
    This function determines the file type based on the suffix of the filepath using pathlib.

    Args:
        filepath: The path to the file represented as a string.

    Returns:
        The file type as a string (e.g., "txt", "jpg", "pdf") or None if no extension is found.
    """
    path = Path(filepath)
    if path.suffix:
        return path.suffix[1:]  # Remove the leading dot
    else:
        return None


# Function to format documents

def kimi_plain_chat(user_question):
    global msg_history, client
    print(user_question)
    try:
        messages = [
            {
                "role": "system",
                "content": "你是人工智能助手，你更擅长中文和英文的对话,并且回答问题",
            },
            {"role": "user", "content": user_question},
        ]
        completion = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=messages,
            temperature=0.9,
        )
        msg_history.append(completion)
        return completion.choices[0].message.content
    except Exception as e:
        return ("error")


def upload_and_get_file_content(file_path, input_client):
    # 上传文件
    file_object = input_client.files.create(file=Path(file_path), purpose="file-extract")

    # 获取文件内容
    file_content = input_client.files.content(file_id=file_object.id).text

    return file_content


def kimi_file_chat(file_path, user_question, client=client):
    try:
        messages = [
            {
                "role": "system",
                "content": "你是人工智能助手，你更擅长中文和英文的对话,并且回答问题",
            },
            {
                "role": "system",
                "content": upload_and_get_file_content(file_path, client),  # <-- 这里，我们将抽取后的文件内容（注意是文件内容，而不是文件 ID）放置在请求中
            },
            {"role": "user", "content": user_question},
        ]
        completion = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=messages,
            temperature=0.9,
        )
        msg_history.append(completion)
        return completion.choices[0].message.content
    except Exception as e:
        return ("error")


def kimi_url_chat(input_url, user_question):
    global msg_history, client
    try:
        print(user_question)
        web_content = get_url_content(input_url)
        print(web_content)
        messages = [
            {
                "role": "system",
                "content": "你是人工智能助手，你更擅长中文和英文的对话,并且回答问题",
            },
            {
                "role": "system",
                "content": web_content,  # <-- 这里，我们将抽取后的URL内容放置在请求中
            },
            {"role": "user", "content": user_question},
        ]
        completion = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=messages,
            temperature=0.9,
        )
        msg_history.append(completion)
        return completion.choices[0].message.content
    except Exception as e:
        return ("error")




with gr.Blocks() as demo:
    gr.Markdown("# RAG")

    with gr.Row():
        with gr.Column():
            gr.Markdown("## chat with the llm")
            input1 = gr.Textbox(label="Input questions")
            button1 = gr.Button("Ask LLM")
        with gr.Column():
            output1 = gr.Textbox(label="answer from LLM")
        button1.click(fn=kimi_plain_chat, inputs=input1, outputs=output1)
    gr.Markdown("<hr>")  # Horizontal line

    with gr.Row():
        with gr.Column():
            gr.Markdown("## File RAG")
            input_2 = gr.File(label="File RAG")
            input2 = gr.Textbox(label="Input questions")
            button2 = gr.Button("File RAG")
        with gr.Column():
            output2 = gr.Textbox(label="answer from LLM")
        button2.click(fn=kimi_file_chat, inputs=[input_2, input2], outputs=output2)
    gr.Markdown("<hr>")  # Horizontal line

    with gr.Row():
        with gr.Column():
            gr.Markdown("## URL RAG")
            input_3 = gr.Textbox(label="Input URL")
            input3 = gr.Textbox(label="Input questions")
            button3 = gr.Button("URL RAG")
        with gr.Column():
            output3 = gr.Textbox(label="answer from LLM")
        button3.click(fn=kimi_url_chat, inputs=[input_3, input3], outputs=output3)


if __name__ == "__main__":

    # kimi_url_chat("https://36kr.com/p/3096576696372743", "总结这个url")
    demo.launch()

