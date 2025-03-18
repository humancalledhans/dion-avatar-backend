import json
import yfinance as yf
import vectorbt as vbt
from datetime import datetime, timedelta
from typing import Dict
import pandas as pd

from response_side.agents.agent_s import get_agent_s_response


def run_intraday_backtest_vectorbt(
    symbol: str,
    days_back: int = 1,
    interval: str = "1m",
    initial_cash: float = 10000.0,
    short_window: int = 5,
    long_window: int = 20
) -> Dict:
    """
    Run an intraday backtest using vectorBT with SMA strategy.
    """
    try:

        print("symbol 3992", symbol)
        print("days back 3992", days_back)
        print("interval 3992", interval)
        print("initial cash 3992", initial_cash)
        print("short window 3992", short_window)
        print("long window 3992", long_window)

        if interval is None:
            interval = '1m'

        if initial_cash is None:
            initial_cash = 10000.0
        
        if short_window is None:
            short_window = 5

        if long_window is None:
            long_window = 20

        # Get current date and time
        current_datetime = datetime.now()

        # Adjust end_date to the last weekday (Friday if today is weekend)
        days_to_subtract = 0
        if current_datetime.weekday() == 5:  # Saturday
            days_to_subtract = 1
        elif current_datetime.weekday() == 6:  # Sunday
            days_to_subtract = 2

        # Set end_date to last weekday's market close (16:00 EST, approx 21:00 UTC)
        end_date = (current_datetime - timedelta(days=days_to_subtract)
                    ).replace(hour=21, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days_back)

        # Fetch data
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            raise ValueError(f"No data found for symbol {symbol}")

        # Calculate moving averages using vectorBT
        short_ma = vbt.MA.run(df['Close'], window=short_window)
        long_ma = vbt.MA.run(df['Close'], window=long_window)

        # Generate signals
        entries = short_ma.ma_crossed_above(long_ma)
        exits = short_ma.ma_crossed_below(long_ma)

        # Run portfolio simulation
        pf = vbt.Portfolio.from_signals(
            close=df['Close'],
            entries=entries,
            exits=exits,
            init_cash=initial_cash,
            freq=interval
        )

       # Get stats and trades
        stats = pf.stats()
        trades = pf.trades.records_readable

        # Format times
        start_time = start_date.strftime("%m/%d/%Y %H:%M")
        end_time = end_date.strftime("%m/%d/%Y %H:%M")

        # Calculate profit/loss
        final_value = float(stats['End Value'])
        profit_loss = final_value - initial_cash

        # Convert trades to JSON-serializable format
        trades_dict = trades.to_dict('records')
        for trade in trades_dict:
            for key, value in trade.items():
                if isinstance(value, pd.Timestamp):
                    # Convert Timestamp to string
                    trade[key] = value.strftime("%m/%d/%Y %H:%M:%S")

        # final_data = {
        #     "symbol": symbol,
        #     "initial_cash": initial_cash,
        #     "final_value": final_value,
        #     "profit_loss": profit_loss,
        #     "trades": trades.to_dict('records'),
        #     "trade_count": int(stats['Total Trades']),
        #     "start_time": start_time,
        #     "end_time": end_time,
        #     "data_points": len(df)
        # }

        final_data = {
            "symbol": symbol,
            "initial_cash": initial_cash,
            "final_value": final_value,
            "profit_loss": profit_loss,
            "trades": trades_dict,  # Use the modified trades list
            "trade_count": int(stats['Total Trades']),
            "start_time": start_time,
            "end_time": end_time,
            "data_points": len(df)
        }

        final_data_str = json.dumps(final_data, indent=2)

        return get_agent_s_response(prompt="The user asked to run a backtest. Please describe these results obtained from vectorBT with SMA strategy. results" + final_data_str)

    except Exception as e:
        return {"error": str(e), "symbol": symbol}


# Example usage
if __name__ == "__main__":
    result = run_intraday_backtest_vectorbt("AAPL")
    if "error" not in result:
        print(f"Profit/Loss: ${result['profit_loss']:.2f}")
        print(f"Trade Count: {result['trade_count']}")
