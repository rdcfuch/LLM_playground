import os
from utils.chroma_v_db import process_file

def build_vector_database():
    """Build vector database from example.pdf"""
    file_path = "/Users/fcfu/PycharmProjects/LLM_playground/FC_RAG/utils/example.pdf"
    
    print(f"Processing {file_path}...")
    if process_file(file_path):
        print("\nVector database build complete! Successfully processed the file.")
    else:
        print("\nFailed to process the file.")

if __name__ == "__main__":
    build_vector_database()
