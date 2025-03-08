from typing import Optional
from fastapi import HTTPException
from datetime import datetime, timedelta
import yfinance as yf

# from response_side.functions.get_yahoo_finance import get_yahoo_finance
from functions.get_yahoo_finance import get_yahoo_finance


def get_stock_data(ticker: str, days: Optional[int] = 30):
    """
    Fetch stock data given a ticker.
    """
    try:

        yahoo_finance_data = get_yahoo_finance(ticker, days)

        return yahoo_finance_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch data: {str(e)}")


if __name__ == '__main__':
    get_stock_data('AAPL')
