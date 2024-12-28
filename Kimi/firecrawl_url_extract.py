import os,html2text,re
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json

# Load environment variables from .env file
load_dotenv()

# Initialize Firecrawl app with your API key
api_key = "fc-34f9366437b74425b1a719b762b41c18"  # Ensure your API key is stored in an environment variable
app = FirecrawlApp(api_key)

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
if __name__ == "__main__":
    print("processing...")
    url = "https://36kr.com/information/AI/"
    total_list = get_links(url)
    article_url_list = total_list
    print("process this article: {}", format(article_url_list))
    contents = get_batch_url_content(article_url_list)
    print("get this content: {}", format(contents))
    summaries = summarize_contents(contents)
    print("totally {} articles".format(len(summaries)))

