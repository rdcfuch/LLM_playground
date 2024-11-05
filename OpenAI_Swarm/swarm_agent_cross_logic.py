import os
import requests
import yfinance as yf
from swarm import Swarm, Agent

# Load OpenWeatherMap API key from environment variable

os.environ['OPENAI_API_KEY'] = 'your_openai_api_key'
os.environ['OPENAI_MODEL_NAME'] = 'llama3.2'
os.environ['OPENAI_BASE_URL'] = 'http://localhost:11434/v1'
os.environ['OPENWEATHER_API_KEY'] = 'e7fbf600db5cdf23222adff8825f5587'

# Initialize Swarm client
client = Swarm()

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


class WebCrawler:
    def warmup(self):
        # Load necessary models
        pass

    def run(self, url):
        # Simulate crawling the URL and extracting content
        return self.extract_content(url)

    def extract_content(self, url):
        # Placeholder for content extraction logic
        return {"markdown": f"Extracted content from {url}"}


def crawl_url(url):
    crawler = WebCrawler()
    crawler.warmup()
    result = crawler.run(url)
    print(result['markdown'])
    return result['markdown']


# Function to fetch real weather data
def get_weather(location):
    print(f"Running weather function for {location}...")

    params = {
        "q": location,
        "appid": 'e7fbf600db5cdf23222adff8825f5587',
        "units": "metric"  # Change to 'imperial' for Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        city_name = data['name']
        return f"The weather in {city_name} is {temperature}°C with {weather_description}."
    else:
        return f"Could not get the weather for {location}. Please try again."


# Function to fetch stock price using yfinance
import datetime


def get_stock_info(ticker, start_date=None, end_date=None):
    """
    Queries stock information from Yahoo Finance using the yfinance library.

    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT").
        start_date (str, optional): The start date for the data in YYYY-MM-DD format. Defaults to None.
        end_date (str, optional): The end date for the data in YYYY-MM-DD format. Defaults to None.

    Returns:
        pandas.DataFrame: A DataFrame containing the stock data.
    """

    stock = yf.Ticker(ticker)

    if start_date and end_date:
        data = stock.history(start=start_date, end=end_date)
    else:
        data = stock.history()

    return data


# Function to transfer from manager agent to weather agent
def transfer_to_weather_assistant():
    print("Transferring to Weather Assistant...")
    return weather_agent


# Function to transfer from manager agent to stock price agent
def transfer_to_stockprice_assistant(ticker):
    print("Transferring to Stock Price Assistant...")
    return stockprice_agent


def transfer_to_web_assistant(url):
    print("Transferring to Weather Assistant...")
    return web_agent


# manager Agent
manager_agent = Agent(
    name="manager Assistant",
    instructions="You help users by directing them to the right assistant.",
    functions=[transfer_to_weather_assistant, transfer_to_stockprice_assistant, transfer_to_web_assistant],
    model="llama3.2"  # 必须加上，不然默认会call gpt-4o
)

# Web_agent
web_agent = Agent(
    name="Web Assistant",
    instructions="You help users by extract the contents from the give url, and summarize in markdown format",
    functions=[crawl_url],
    model="llama3.2"
)

# Weather Agent
weather_agent = Agent(
    name="Weather Assistant",
    instructions="You provide weather information for a given location using the provided tool",
    functions=[get_weather],
    model="llama3.2"
)

# Stock Price Agent
stockprice_agent = Agent(
    name="Stock Price Assistant",
    instructions="You provide the latest stock price for a given ticker symbol using the yfinance library.",
    functions=[get_stock_info],
    model="llama3.2"
)

# print("Running manager Assistant for Weather...")
# response = client.run(
#     agent=manager_agent,
#     messages=[{"role": "user", "content": "What's the weather in San Jose?"}],
# )
# print(response.messages[-1]["content"])

# Example: User query handled by manager agent to get stock price

# get_stock_price("APPL")

# print("\nRunning manager Assistant for Stock Price...")
# response = client.run(
#     agent=manager_agent,
#     messages=[{"role": "user", "content": "Get me the stock price of AAPL."}],
# )
#
# print(response.messages[-1]["content"])


# print("\nRunning manager Assistant for web page")
# response = client.run(
#     agent=manager_agent,
#     messages=[{"role": "user", "content": "summarize the web page from the url below:  https://techcrunch.com/2024/11/03/openai-has-hired-the-co-founder-of-twitter-challenger-pebble/."}],
# )

# print(response.messages[-1]["content"])

while True:
    user_input = input("\nWhat do you wnat to know?\nUser:")
    response = client.run(
        agent=manager_agent,
        messages=[{"role": "user",
                   "content": user_input}],
    )

    print(response.messages[-1]["content"])
