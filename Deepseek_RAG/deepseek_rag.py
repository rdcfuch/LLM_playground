import os
from dotenv import load_dotenv
from pymilvus import MilvusClient, model as milvus_model
from openai import OpenAI
from tqdm import tqdm

# Load environment variables
load_dotenv()

DEEPSEEK_MODEL = os.getenv("DeepSeek_MODEL", "deepseek-chat")
DEEPSEEK_API_KEY = os.getenv("DeepSeek_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DeepSeek_BASE_URL", "https://api.deepseek.com")

# Initialize DeepSeek Client
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# Initialize Milvus
milvus_client = MilvusClient(uri="./milvus_demo.db")
collection_name = "web_summaries"

# Prepare Embedding Model
embedding_model = milvus_model.DefaultEmbeddingFunction()


# Function to Insert Data into Milvus
def insert_data_to_milvus(documents):
    if milvus_client.has_collection(collection_name):
        milvus_client.drop_collection(collection_name)

    milvus_client.create_collection(
        collection_name=collection_name,
        dimension=len(embedding_model.encode_queries(["test"])[0]),
        metric_type="IP",
        consistency_level="Strong",
    )

    data = []
    doc_embeddings = embedding_model.encode_documents(documents)
    for i, embedding in enumerate(tqdm(doc_embeddings, desc="Creating embeddings")):
        data.append({"id": i, "vector": embedding, "text": documents[i]})

    milvus_client.insert(collection_name=collection_name, data=data)


# Summarize Function
def summarize_page(text):
    summary = deepseek_client.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "You are an AI summarizer."},
            {"role": "user", "content": text},
        ]
    )
    return summary.choices[0].message.content


# Retrieve Similar Content
def retrieve_context(question):
    embedding = embedding_model.encode_queries([question])[0]
    results = milvus_client.search(
        collection_name=collection_name,
        data=[embedding],
        limit=3,
        search_params={"metric_type": "IP"},
        output_fields=["text"],
    )
    return "\n".join([res["entity"]["text"] for res in results[0]])


# Main Workflow
def main():
    # Example Web Content
    web_content = ["Sample text from web page.", "Another paragraph.", "More content."]

    # Step 1: Insert Web Content into Milvus
    insert_data_to_milvus(web_content)

    # Step 2: Summarize Page
    full_text = " ".join(web_content)
    summary = summarize_page(full_text)
    print("Summary:\n", summary)

    # Step 3: RAG Query
    question = "What is the main idea?"
    context = retrieve_context(question)
    answer = deepseek_client.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "Use context to answer questions."},
            {"role": "user", "content": f"<context>{context}</context> <question>{question}</question>"},
        ],
    )
    print("Answer:\n", answer.choices[0].message.content)


if __name__ == "__main__":
    main()
