import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

from response_side.agents.agent_a import get_agent_a_response
from response_side.agents.agent_s import get_agent_s_response
from response_side.functions.get_yahoo_finance import get_yahoo_finance


def momentum_score(symbol, lookback=252, skip=21, days=450, interval="1d"):
    """
    Calculate momentum score for a financial asset by fetching price data from Yahoo Finance
    and return an interpreted response using an agent.
    symbol: str, stock ticker (e.g., "TSLA")
    lookback: int, days for momentum calculation (default: ~1 year)
    skip: int, days to skip for recent period (default: ~1 month)
    days: int, days of historical data to fetch (default: 365)
    interval: str, data frequency (default: "1d" for daily; use "1m" for intraday)
    Returns: str, interpreted momentum analysis from agent
    """
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Fetch data
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date, interval=interval)

    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")

    # Extract adjusted close prices
    prices = df["Close"].to_numpy()

    if len(prices) < lookback + skip:
        return "Insufficient data to calculate momentum score."

    # Calculate daily returns
    returns = np.diff(prices) / prices[:-1]
    # Slice for lookback period
    momentum_returns = returns[-(lookback + skip):-skip]
    # Cumulative return
    cum_return = np.prod(1 + momentum_returns) - 1
    # Normalize with tanh
    final_data = np.tanh(cum_return)
    final_data_str = f"{final_data:.2f}"

    # Pass to agent for interpretation
    prompt = f"""
    The user asked for a momentum analysis for {symbol} under Quantitative Analysis.
    The momentum score, calculated using a NumPy algorithm based on a momentum factor strategy,
    is {final_data_str} (range -1 to 1, where positive indicates upward momentum,
    negative indicates downward, and near-zero indicates no trend).
    Please describe these results in simple terms without giving explicit buy/sell advice.
    """
    return get_agent_s_response(prompt=prompt)

    # return get_agent_s_response(prompt="The user asked to run a momentum score backtest. Please describe these results obtained from a nnumpy algorithm, based off the momentum factor strategy. results" + final_data_str)


# Example usage
# prices = get_yahoo_finance("TSLA", days=365)
# score = momentum_score(prices)
# print(f"Tesla Momentum Score: {score:.2f}")
