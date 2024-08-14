from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


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


# Example usage
url = "https://www.36kr.com/p/2904514951518852"
content = extract_article_content(url)
print(content)
