import gradio as gr
from openai import OpenAI
import bs4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, SeleniumURLLoader, TextLoader,PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
from pathlib import Path

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

input_urls = ["https://ollama.com/blog/llama-3-is-not-very-censored"]
loader = SeleniumURLLoader(urls=input_urls)
base_ollama_url= "http://127.0.0.1:11435/v1"
embedding_ollama_url= "http://127.0.0.1:11435/api/embeddings"
llm_model="llama3:70b"
embedding_model="nomic-embed-text:latest"
client = OpenAI(
    # base_url = 'http://192.168.1.199:11434/v1',
    base_url = base_ollama_url, # <<<<< you need to do the port mapping kuberate desktop in VScode
    api_key='ollama' # required, but unused
)

msg_history=[]

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


def load_and_retrieve_url(input_url):
    input_urls = input_url
    loader = SeleniumURLLoader(urls=input_urls)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    embeddings = OllamaEmbeddings(model=embedding_model)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore.as_retriever()

def load_and_retrieve_file(input_file):
    file_path = input_file
    if get_file_type(input_file) == "txt":
        print(f"Loading {input_file}")
        loader = TextLoader(file_path=file_path)
    elif get_file_type(input_file) == "pdf":
        loader = PyPDFLoader(file_path=file_path)
    else:
        print("no loader found")
        loader = None
    if loader is not None:
        docs = loader.load()
        # print(f"docs: {docs}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        embeddings = OllamaEmbeddings(model=embedding_model)  # still use local ollama, not remote
        # embeddings = embedding_client.embeddings.create(model=embedding_model)
        print("embeddings loaded")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        print(f"vectorstore: {vectorstore.as_retriever()}")
        return vectorstore.as_retriever()

# Function to format documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Function that defines the RAG chain
def rag_chain_url(urls, question):
    retriever = load_and_retrieve_url(urls)
    retrieved_docs = retriever.invoke(question)
    formatted_context = format_docs(retrieved_docs)
    formatted_prompt = f"Question: {question}\n\nContext: {formatted_context}"
    print(f"Rag chain url: {urls}\nQuestion: {question}\nContext: {formatted_context}")
    response = client.chat.completions.create(
        model=llm_model,
        messages=[{'role': 'user', 'content': formatted_prompt}],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def rag_chain_file(files, question):
    print(f"Loading rag_chain_file {files}, {question}")
    retriever = load_and_retrieve_file(files)
    print(f"Retrieving {files}")
    retrieved_docs = retriever.invoke(question)
    formatted_context = format_docs(retrieved_docs)
    formatted_prompt = f"Question: {question}\n\nContext: {formatted_context}"
    print(f'Question: {question}\n\nContext: {formatted_context}')
    # response = ollama.chat(base_url=base_ollama_url,model=llm_model, messages=[{'role': 'user', 'content': formatted_prompt}])
    response = client.chat.completions.create(
        model=llm_model,
        messages=[{'role': 'user', 'content': formatted_prompt}],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def plain_chat(question):
    global msg_history,client
    msg_history.append({'role': 'user', 'content': question})
    response = client.chat.completions.create(
        model=llm_model,
        # messages=[{'role': 'user', 'content': question}],
        messages=msg_history,
    )
    response_content=response.choices[0].message.content
    msg_history.append({'role': 'assistant','content': response_content})
    print(msg_history)
    return response_content


# Gradio interface
# iface_url = gr.Interface(
#     fn=rag_chain_url,
#     inputs=["text", "text"],
#     outputs=gr.Textbox(lines=30),
#     title="RAG Chain Question Answering",
#     description="Enter a URL and a query to get answers from the RAG chain."
# )
#
# iface_file = gr.Interface(
#     fn=rag_chain_file,
#     inputs=["file", "text"],
#     outputs=gr.Textbox(lines=30),
#     title="RAG Chain Question Answering",
#     description="Enter a file (txt or pdf) and a query to get answers from the RAG chain."
# )
#
# iface_reg = gr.Interface(
#     fn=plain_chat,
#     inputs=["text"],
#     outputs=gr.Textbox(lines=30),
#     title="Regular chat",
#     description="chat with the llm"
# )
#
# demo = gr.TabbedInterface(interface_list=[iface_file, iface_url], tab_names=["File RAG", "URL RAG"])
#
# # Launch the app
# demo.launch()

with gr.Blocks() as demo:
    gr.Markdown("# RAG")

    with gr.Row():
        with gr.Column():
            gr.Markdown("## chat with the llm")
            input1 = gr.Textbox(label="Input questions")
            button1 = gr.Button("Ask LLM")
        with gr.Column():
            output1 = gr.Textbox(label="answer from LLM")
        button1.click(fn=plain_chat, inputs=input1, outputs=output1)
    gr.Markdown("<hr>")  # Horizontal line

    with gr.Row():
        with gr.Column():
            gr.Markdown("## File RAG")
            input_2 = gr.File(label="File RAG")
            input2 = gr.Textbox(label="Input questions")
            button2 = gr.Button("File RAG")
        with gr.Column():
            output2 = gr.Textbox(label="answer from LLM")
        button2.click(fn=rag_chain_file, inputs=[input_2,input2], outputs=output2)
    gr.Markdown("<hr>")  # Horizontal line

    with gr.Row():
        with gr.Column():
            gr.Markdown("## URL RAG")
            input_3 = gr.Textbox(label="Input URL")
            input3 = gr.Textbox(label="Input questions")
            button3 = gr.Button("URL RAG")
        with gr.Column():
            output3 = gr.Textbox(label="answer from LLM")
        button3.click(fn=rag_chain_url, inputs=[input_3, input3], outputs=output3)

demo.launch()
