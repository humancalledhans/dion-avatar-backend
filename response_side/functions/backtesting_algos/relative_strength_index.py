import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from response_side.agents.agent_s import get_agent_s_response


def relative_strength_index(symbol, period=14, days=30, interval="1d"):
    """
    Calculate the Relative Strength Index (RSI) for a financial asset by fetching price data
    from Yahoo Finance and return an interpreted response. RSI indicates momentum and overbought/oversold conditions.
    symbol: str, stock ticker (e.g., "TSLA")
    period: int, lookback period for RSI (default: 14, standard for daily data)
    days: int, days of historical data to fetch (default: 30, ~1 month)
    interval: str, data frequency (default: "1d" for daily)
    Returns: str, interpreted RSI analysis
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days * 2)

    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date, interval=interval)

    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")

    prices = df["Close"].to_numpy()

    if len(prices) < period + 1:
        return "Insufficient data to calculate RSI."

    # Calculate daily price changes
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    # Average gains and losses over period
    avg_gain = np.mean(gains[-period-1:-1])
    avg_loss = np.mean(losses[-period-1:-1])

    # RS and RSI
    rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
    rsi = 100 - (100 / (1 + rs)) if rs != np.inf else 100
    rsi_str = f"{rsi:.2f}"

    prompt = f"""
    The user asked for an RSI analysis for {symbol} under Quantitative Analysis.
    The RSI, calculated using a NumPy algorithm over {period} periods, is {rsi_str} (range 0-100).
    Values above 70 suggest overbought conditions, below 30 suggest oversold, and 30-70 indicate neutral momentum.
    Please describe these results in simple terms without giving explicit buy/sell advice.
    """
    return get_agent_s_response(prompt=prompt)