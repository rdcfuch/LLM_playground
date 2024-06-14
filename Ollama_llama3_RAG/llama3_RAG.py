import gradio as gr
import bs4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, SeleniumURLLoader, TextLoader,PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
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
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore.as_retriever()

def load_and_retrieve_file(input_file):
    file_path = input_file
    print(f"Loading {input_file}")
    if get_file_type(input_file) == "txt":
        loader = TextLoader(file_path=file_path)
    if get_file_type(input_file) == "pdf":
        loader = PyPDFLoader(file_path=file_path)
    else:
        return None
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
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
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']

def rag_chain_file(files, question):
    retriever = load_and_retrieve_file(files)
    retrieved_docs = retriever.invoke(question)
    formatted_context = format_docs(retrieved_docs)
    formatted_prompt = f"Question: {question}\n\nContext: {formatted_context}"
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']


# Gradio interface
iface_url = gr.Interface(
    fn=rag_chain_url,
    inputs=["text", "text"],
    outputs=gr.Textbox(lines=30),
    title="RAG Chain Question Answering",
    description="Enter a URL and a query to get answers from the RAG chain."
)

iface_file = gr.Interface(
    fn=rag_chain_file,
    inputs=["file", "text"],
    outputs=gr.Textbox(lines=30),
    title="RAG Chain Question Answering",
    description="Enter a URL and a query to get answers from the RAG chain."
)

demo = gr.TabbedInterface([iface_file, iface_url], ["File RAG", "URL RAG"])

# Launch the app
demo.launch()
