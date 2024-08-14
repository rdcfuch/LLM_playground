import requests
from bs4 import BeautifulSoup

# Navigate to the URL
url = "https://mp.weixin.qq.com/s/6z2ztBjDg_P5XawhSrm0kA"

# Step 1: Fetch the HTML content from the webpage
response = requests.get(url)

# Step 2: Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Step 3: Extract all text from the HTML document
text_content = soup.get_text()

# Step 4: Split the text into lines and remove any blank lines
lines = text_content.splitlines()
non_blank_lines = [line.strip() for line in lines if line.strip()]

# Step 5: Join the non-blank lines back into a single string
cleaned_text = '\n'.join(non_blank_lines)

# Print the cleaned text
print(cleaned_text)


