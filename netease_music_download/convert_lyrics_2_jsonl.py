import os
import json
import re
from openai import OpenAI

# Define the input and output directories
input_directory = "./test"  # Replace with your input directory
output_file = "output.jsonl"  # Define the output JSONL file

# Regular expressions to match timestamps and lines with a colon
timestamp_pattern = re.compile(r"\[.*?\]")
colon_line_pattern = re.compile(r" : ")

client = OpenAI(
    # base_url = 'http://192.168.1.199:11434/v1',
    base_url = 'http://127.0.0.1:11434/v1', # <<<<< you need to do the port mapping kuberate desktop in VScode
    api_key='ollama', # required, but unused
)


# Function to process a single file
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Remove timestamps and lines with a colon
    cleaned_lines = []
    for line in lines:

        if not colon_line_pattern.search(line):
            line = timestamp_pattern.sub("", line).strip()
            # print(line)
            if line:  # Exclude empty lines
                cleaned_lines.append(line)

    return ",".join(cleaned_lines)

def summary(message):
    user_model="qwen2.5-coder:7b"
    # user_model="qwen2.5:3b"
    user_messages = [
        {"role": "system", "content": '你是一个古风歌词翻译家，你可以把你收到的古风歌词用用现代白话文的方式描述总结成20字左右的总结, 输出格式为文本，不要有任何不相关的信息'},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model=user_model,
        messages=user_messages,
        # tools=tools,
        # tool_choice="auto",  # auto is default, but we'll be explicit
    )
    # Access the summarized text from the message property
    response_message = response.choices[0].message.content  # Remove leading/trailing whitespace
    return response_message


# Read all files in the input directory
all_data = []

for file_name in os.listdir(input_directory):
    file_path = os.path.join(input_directory, file_name)
    if os.path.isfile(file_path):
        processed_content = process_file(file_path)
        if processed_content:
            print(f"歌词：{processed_content}")
            summary_msg=summary(processed_content)
            print(f"总结: {summary_msg}")
            all_data.append({"instruct": "你是一个古风歌词作者，你可以根据输入，写出一套古风的歌词", "input":summary_msg, "output": processed_content})

# Write the processed content to the JSONL file
with open(output_file, 'w', encoding='utf-8') as out_file:
    for entry in all_data:
        json.dump(entry, out_file, ensure_ascii=False)
        out_file.write("\n")

print(f"Processing complete. Output saved to {output_file}")
