import requests
from bs4 import BeautifulSoup
import openai
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import markdown
import datetime

MODEL = "llama3.1:70b"
MODEL_BASE_URL = 'http://127.0.0.1:11436/v1'  # use my server
API_KEY_SET = 'ollama'


def extract_article_content(url):
    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open the URL
    driver.get(url)
    time.sleep(2)
    try:
        # Find the element with the specified class and extract its content
        article_element = driver.find_element(By.CLASS_NAME, "article-mian-content")
        article_content = article_element.text

        # You could also get inner HTML if needed:
        # article_content = article_element.get_attribute('innerHTML')

        return article_content
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        # Close the driver
        driver.quit()


def list_articles_from_36kr(url):
    """
    Fetches and lists all article titles and URLs from the specified 36kr search page.

    Args:
        url (str): The URL of the 36kr search page.

    Returns:
        list: A list of dictionaries containing 'title' and 'url' for each article.
    """
    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all article items
    article_items = soup.find_all('a', href=True)

    # Extract the title and href for each article
    articles = []
    added_urls = set()  # Set to keep track of added URLs

    for a in article_items:
        # Filter to get only the relevant article links
        if '/p/' in a['href'] and "36kr" not in a['href']:
            title = a.get_text(strip=True)
            url = "https://www.36kr.com" + a['href']

            # Check if the URL is already in the set
            if title != "" and url not in added_urls:
                articles.append({'title': title, 'url': url})
                added_urls.add(url)  # Add the URL to the set to track it

    return articles

def chat(input_msg):
    user_model = MODEL
    user_messages = [
        {"role": "system",
         "content": """
         ## role
        you are a AI expert and you will be able to summarize AI related articles
        
        ## skill
        1. you will take the input text, review it and genreate a summary report, which will include: 
        - the main idea
        - key data that support the idea
        - conclusion or proposal
        
        2. you can give tags based on the content, for example:
        - LLM
        - AI agent/application
        - industry insight
        - new product
        
        
        ## constraints
        you alway provide the output in mark down format
        
        ## example
        Title: {}
        Main topic:{}
        Main insight and data: {}
        Conclusion: {}
         
         """},
        # {"role": "user", "content": "Who won the world series in 2020?"},
        # {"role": "assistant", "content": "The LA Dodgers won in 2020."},
        {"role": "user", "content": input_msg}
    ]
    client = client = OpenAI(
        base_url=MODEL_BASE_URL,  # <<<<< you need to do the port mapping kuberate desktop in VScode
        api_key=API_KEY_SET,  # required, but unused
    )
    response = client.chat.completions.create(
        model=user_model,
        messages=user_messages,

        # tools=tools,
        # tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message.content
    print(response_message)
    return response_message


# Example usage
if __name__ == '__main__':
    url = "https://www.36kr.com/search/articles/AI"
    articles = list_articles_from_36kr(url)
    today = datetime.date.today()
    formatted_date = today.strftime("%B_%d")  # Output: August 13, 2024
    print(f"36kr_{formatted_date}.md")
    
    count=0
    
    with open(f"36kr_{formatted_date}.md", "w") as f:
        for article in articles:
            count += 1
            print(f"## Title{count}: {article['title']}")
            f.write(f"## Title{count}: {article['title']}\n")
            f.write(f"URL: {article['url']}")
            print(f"URL: {article['url']}")
            content = extract_article_content(article['url'])
            summary = chat(f"please summary this artile in Chinese, response in mark down format: {content}")
            f.write(summary)
            f.write("\n------------------------------")
            f.write("\n------------------------------\n\n")
            
            print("----------")

    with open(f"36kr_{formatted_date}.md", "r", encoding="utf-8") as input_file:
        text = input_file.read()
        html = markdown.markdown(text)

    with open(f"36kr_{formatted_date}.html", "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
        output_file.write(html)

    print(f"Report is generated, please check 36kr_{formatted_date}.html")
