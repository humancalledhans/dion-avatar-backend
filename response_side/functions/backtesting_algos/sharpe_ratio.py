import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

from response_side.agents.agent_s import get_agent_s_response


def sharpe_ratio(symbol, days=252, risk_free_rate=0.04, interval="1d"):
    """
    Calculate the Sharpe ratio for a financial asset by fetching price data from Yahoo Finance
    and return an interpreted response. Sharpe ratio is excess return over volatility.
    symbol: str, stock ticker (e.g., "TSLA")
    days: int, days of historical data to fetch (default: 252, ~1 year of trading days)
    risk_free_rate: float, annualized risk-free rate (default: 0.04, ~4%)
    interval: str, data frequency (default: "1d" for daily)
    Returns: str, interpreted Sharpe ratio analysis
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days * 2)

    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date, interval=interval)

    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")

    prices = df["Close"].to_numpy()

    if len(prices) < days:
        return "Insufficient data to calculate Sharpe ratio."

    returns = np.diff(prices) / prices[:-1]
    recent_returns = returns[-days:] if len(returns) > days else returns
    # Annualized return
    avg_return = np.mean(recent_returns) * 252
    # Volatility
    vol = np.std(recent_returns, ddof=1) * np.sqrt(252)
    # Sharpe ratio
    sharpe = (avg_return - risk_free_rate) / vol if vol != 0 else np.nan
    sharpe_str = f"{sharpe:.2f}" if not np.isnan(
        sharpe) else "undefined (zero volatility)"

    prompt = f"""
    The user asked for a Sharpe ratio analysis for {symbol} under Quantitative Analysis.
    The Sharpe ratio, calculated using a NumPy algorithm, is {sharpe_str} (excess return per unit of risk,
    assuming a risk-free rate of {risk_free_rate}).
    A higher ratio indicates better risk-adjusted returns.
    Please describe these results in simple terms without giving explicit buy/sell advice.
    """
    return get_agent_s_response(prompt=prompt)
