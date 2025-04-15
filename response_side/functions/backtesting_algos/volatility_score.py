import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

from response_side.agents.agent_s import get_agent_s_response


def volatility_score(symbol, days=252, interval="1d"):
    """
    Calculate a volatility score for a financial asset by fetching price data from Yahoo Finance
    and return an interpreted response. Volatility is the annualized standard deviation of daily returns.
    symbol: str, stock ticker (e.g., "TSLA")
    days: int, days of historical data to fetch (default: 252, ~1 year of trading days)
    interval: str, data frequency (default: "1d" for daily; use "1m" for intraday)
    Returns: str, interpreted volatility analysis
    """
    # Calculate date range
    end_date = datetime.now().date()
    # ~2 years to ensure enough trading days
    start_date = end_date - timedelta(days=days * 2)

    # Fetch data
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date, interval=interval)

    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")

    # Extract adjusted close prices
    prices = df["Close"].to_numpy()

    if len(prices) < days:
        return "Insufficient data to calculate volatility score."

    # Calculate daily returns
    returns = np.diff(prices) / prices[:-1]
    # Take most recent 'days' returns
    recent_returns = returns[-days:] if len(returns) > days else returns
    # Annualized volatility (std dev of returns * sqrt(252))
    vol = np.std(recent_returns, ddof=1) * np.sqrt(252)
    vol_str = f"{vol:.4f}"

    # Pass to agent
    prompt = f"""
    The user asked for a volatility analysis for {symbol} under Quantitative Analysis.
    The volatility score, calculated using a NumPy algorithm, is {vol_str} (annualized standard deviation of daily returns).
    A higher score indicates larger price swings, suggesting greater risk.
    Please describe these results in simple terms without giving explicit buy/sell advice.
    """
    return get_agent_s_response(prompt=prompt)
