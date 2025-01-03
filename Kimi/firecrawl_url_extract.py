import os,html2text,re
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize Firecrawl app with your API key
api_key = "fc-34f9366437b74425b1a719b762b41c18"  # Ensure your API key is stored in an environment variable
app = FirecrawlApp(api_key)

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
# URL to scrape

def get_one_url_content(url,input_format=["html"]):
    # Scrape the URL and get its content in LLM-ready format (markdown, structured data, etc.)
    try:
        scrape_result = app.scrape_url(url, {
            "formats": input_format
        })
        print(scrape_result)
        if scrape_result['html']:
            soup = BeautifulSoup(scrape_result['html'], 'html.parser')
            target_div = soup.find("div", class_="common-width content articleDetailContent kr-rich-text-wrapper")
            print(target_div)
            if target_div:
                print("Extracted Content:")
                contents=target_div.text.strip()
                print(contents)
                return contents # Print plain text content of the div
            else:
                print("The specified div was not found.")
        else:
            return "No html contents scraped"

    except Exception as e:
        if str(e) == "success":
            pass

def get_batch_url_content(url,input_format=["html"]):
    # Scrape the URL and get its content in LLM-ready format (markdown, structured data, etc.)
    try:
        scrape_result = app.batch_scrape_urls(url, {
            "formats": input_format
        })
        # print(scrape_result)
        contents=[]
        if len(scrape_result['data']) > 1:
            for data_html in scrape_result['data']:
                soup = BeautifulSoup(data_html['html'], 'html.parser')
                target_div = soup.find("div", class_="common-width content articleDetailContent kr-rich-text-wrapper")
                # print(target_div)
                if target_div:
                    contents.append(target_div.text.strip())
                else:
                    print("The specified div was not found.")
            print("Extracted Content:",contents)
            return contents
        else:
            return "The specified div was not found."
    except Exception as e:
        if str(e) == "success":
            pass
def get_links(url,input_format=["links"]):
    try:
        ai_article=[]
        # use re to match patterns
        # Regex pattern to match the specific URL
        pattern = r'https://36kr\.com/p/\d+'
        scrape_result = app.scrape_url(url, {
            "formats": input_format
        })
        if scrape_result['links']:
            for link in scrape_result['links']:
                # Check if the URL matches the pattern
                if re.match(pattern, link):
                    ai_article.append(link)
                else:
                    pass
            return ai_article
        else:
            print("The specified link was not found.")
            return []

    except Exception as e:
        if str(e) == "success":
            pass

def get_contents(input_url):
    if isinstance(input_url, str):
        result=get_one_url_content(input_url)
    elif isinstance(input_url, list):
        result=get_batch_url_content(input_url)
    else:
        result=""
        print("Input must be a string or a list")
    return result

def summarize_contents(input_contents):
    summaries = []
    print("summarizing contents...")
    i=1
    for article in input_contents:
        print("processing item {}".format(i))
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
            result=completion.choices[0].message.content.replace('```html',"").replace('```',"")
            print("{}:  {}".format(i,result))
            i=i+1
            summaries.append(result)

        except Exception as e:
            print("Error:  {}".format(str(e)))
            return ("error")
    print(summaries)
    return (summaries)

if __name__ == "__main__":
    print("processing...")
    url = "https://36kr.com/information/AI/"
    total_list = get_links(url)
    article_url_list = total_list[:3]
    print("process this article: {}", format(article_url_list))
    contents = get_batch_url_content(article_url_list)
    print("get this content: {}".format(contents))
    summaries = summarize_contents(contents)
    print("totally {} articles".format(len(summaries)))

