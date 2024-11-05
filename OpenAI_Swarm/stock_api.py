import yfinance as yf

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

# Example usage:
ticker = "AAPL"
start_date = "2024-10-01"
end_date = "2024-11-01"

stock_data = get_stock_info(ticker, start_date, end_date)

print(stock_data)
