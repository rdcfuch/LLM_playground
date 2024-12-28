import gradio as gr
from openai import OpenAI
import datetime
from firecrawl_url_extract import get_one_url_content,get_batch_url_content,get_links,get_contents
import time
# Initialize OpenAI client
KIMI_MODEL = "moonshot-v1-8k"
Ollama_MODEL = "llama3.2:latest"
KIMI_API_KEY = 'sk-e2elzR10u4Tv2UXxx9kYC6Te0OrzM87qlpgHJsWVjzHd6Ouw'
KIMI_API_URL = "https://api.moonshot.cn/v1"
Kr_ai_url = "https://36kr.com/information/AI/"
client = OpenAI(
    # base_url = 'http://192.168.1.199:11434/v1',
    base_url=KIMI_API_URL,  # <<<<< you need to do the port mapping kuberate desktop in VScode
    api_key=KIMI_API_KEY  # required, but unused
)

def summarize_contents(input_contents):
    summaries = []
    print("summarizing contents...")
    for article in input_contents:
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是人工智能助手，你更擅长从文章中总结出重点，包括：标题，核心内容，有价值的数据和案例，你总是可以输出结构化的总结",
                },
                {"role": "user", "content": "用中文总结这段文章，用纯html输出结果，不要有任何其他非html的输出，文章内容如下："+article},
            ]
            completion = client.chat.completions.create(
                model=KIMI_MODEL,
                messages=messages,
                temperature=0.9,
            )
            summaries.append(completion.choices[0].message.content.replace('```html',"").replace('```',""))

        except Exception as e:
            return ("error")
    print(summaries)
    return (summaries)



# Create Gradio Blocks interface
with gr.Blocks() as demo:
    gr.Markdown("# RAG Summarization Tool")

    # Input field
    input_text = gr.Textbox(
        label="总结今天的36kr ai文章：日期", lines=1,value=datetime.date.today()
    )

    # Predefined outputs (initially hidden)
    output_list = [gr.HTML(visible=False) for _ in range(60)]  # Adjust size as needed

    # Submit button
    submit_button = gr.Button("Process")
    status_indicator = gr.HTML(value="", visible=False)  # Status indicator


    def process_and_summarize(html_array):
        print("processing...")
        url = "https://36kr.com/information/AI/"
        total_list=get_links(url)
        article_url_list=total_list
        print("process this article: {}",format(article_url_list))
        contents = get_contents(article_url_list)
        print("get this content: {}",format(contents))
        summaries = summarize_contents(contents)
        print("totally {} articles".format(len(summaries)))
        updates = []
        # Process each summary and update outputs
        for i, summary in enumerate(summaries):
            print(summary)
            updates.append(gr.update(value=summary+"\n ===============================================", visible=True))

        # Hide remaining unused outputs
        empty=len(output_list)-len(updates)
        for i in range(empty):
            updates.append(gr.update(visible=False))

        # Final completion state
        return updates


    # Link submit button to process function
    submit_button.click(
        fn=process_and_summarize,
        inputs=input_text,
        outputs=output_list,
        queue=True,
    )

if __name__ == '__main__':

    demo.launch()
