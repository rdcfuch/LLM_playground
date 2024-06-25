# !pip install phidata openai duckdb duckduckgo-search pydantic pandas wikipedia sqlalchemy pgvector pypdf psycopg arxiv yfinance ollama
# 1. AI Assistant
from phi.assistant import Assistant

assistant = Assistant(description="You help people with their health and fitness goals.")
assistant.print_response("Share a quick healthy breakfast recipe.", markdown=True)

# 2. Assistant with DuckDuckGo for latest AI news
from phi.tools.duckduckgo import DuckDuckGo

assistant = Assistant(tools=[DuckDuckGo()], show_tool_calls=True)
assistant.print_response("Whats the latest AI News? Summarize top stories with sources.")

# 3. Stock Price Tool for retrieving current stock prices
import yfinance as yf
from phi.tools import Toolkit

class StockPriceTool(Toolkit):
    def __init__(self):
        super().__init__()

    def stock_price(self, ticker: str) -> str:
        """Retrieves the current stock price for the given ticker symbol.
        Args:
            ticker (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA').
        Returns:
            str: A message indicating the current stock price, or an error message if the ticker is invalid.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[0]  # Extract closing price
                return f"The current stock price of {ticker} is ${current_price:.2f}."
            else:
                return f"Could not find current stock price for {ticker}."
        except Exception as e:
            return f"Error retrieving stock price for {ticker}: {str(e)}"

# Stock price retrieval assistant
assistant = Assistant(
    description="You are a helpful Assistant to get stock prices using tools",
    tools=[StockPriceTool().stock_price],
    show_tool_calls=True,
    debug_mode=True,
)

assistant.print_response("What's the stock price of Apple?")

# 4. DuckDbAssistant for querying movies database
import json
from phi.assistant.duckdb import DuckDbAssistant

duckdb_assistant = DuckDbAssistant(
    semantic_model=json.dumps({
        "tables": [
            {
                "name": "movies",
                "description": "Contains information about movies from IMDB.",
                "path": "https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
            }
        ]
    }),
)

duckdb_assistant.print_response("What is the average rating of movies? Show me the SQL.", markdown=True)

# 5. PythonAssistant for calculating average movie rating
from phi.assistant.python import PythonAssistant
from phi.file.local.csv import CsvFile

python_assistant = PythonAssistant(
    files=[
        CsvFile(
            path="https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
            description="Contains information about movies from IMDB.",
        )
    ],
    pip_install=True,
    show_tool_calls=True,
    debug_mode=True,
)

python_assistant.print_response("What is the average rating of movies?", markdown=True)

# 6. PgVectorDb and WikipediaKnowledgeBase setup
from phi.docker.app.postgres import PgVectorDb
from phi.vectordb.pgvector import PgVector2
from phi.knowledge.wikipedia import WikipediaKnowledgeBase

vector_db = PgVectorDb(
    pg_user="ai",
    pg_password="ai",
    pg_database="ai",
)

knowledge_base = WikipediaKnowledgeBase(
    topics=["Manchester United", "Real Madrid"],
    vector_db=PgVector2(
        collection="wikipedia_documents",
        db_url=vector_db.get_db_connection_local(),
    ),
)

# Assistant with knowledge base configuration

assistant = Assistant(
    knowledge_base=knowledge_base,
    add_references_to_prompt=True,
)

assistant.knowledge_base.load(recreate=False)
assistant.print_response("Ask me about something from the knowledge base")

# 7. Ollama Integration
from phi.llm.ollama import Ollama

prompt = "Who are you and who created you? Answer in 1 short sentence."
temp = 0.3
models = ["mistral", "orca2"]

for model in models:
    print(f"================ {model} ================")
    Assistant(llm=Ollama(model=model, options={"temperature": temp}), system_prompt=prompt).print_response(
        markdown=True
    )
