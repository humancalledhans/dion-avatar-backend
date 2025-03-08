import re
import os
from typing import Dict, Optional
from openai import OpenAI
import openai
from typing import Optional
from fastapi import HTTPException
from datetime import datetime, timedelta
import yfinance as yf
import json
import pytz


def get_yahoo_finance(ticker, days=30):
    stock = yf.Ticker(ticker.upper())

    # Get basic info
    info = stock.info
    if not info or 'symbol' not in info:
        raise HTTPException(
            status_code=404, detail=f"No data found for ticker {ticker}")

    # Get historical data
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=days)
    history = stock.history(start=start_date, end=end_date)

    if history.empty:
        raise HTTPException(
            status_code=404, detail="No historical data available")

    # Prepare response
    response = {
        "ticker": ticker.upper(),
        "company_name": info.get("longName", "N/A"),
        "current_price": info.get("regularMarketPrice", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "historical_data": history[["Open", "High", "Low", "Close", "Volume"]].to_dict(orient="index"),
        "last_updated": datetime.now().isoformat()
    }

    # Convert historical data timestamps to strings
    response["historical_data"] = {
        str(date): values for date, values in response["historical_data"].items()
    }

    return response


# Assuming OpenAI client is initialized elsewhere
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
client = OpenAI()


def extract_yahoo_finance_params(sentence: str) -> Dict:
    """
    Analyzes a sentence and returns parameters for yahoo_finance function in OpenAI function calling format.

    Args:
        sentence (str): User input sentence

    Returns:
        Dict: Function calling parameters compatible with OpenAI API
    """

    params = {}
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Extract stock ticker symbol and number of days from the sentence. If not specified, days defaults to 30. Return in JSON format. Use the ticker symbol widely accepted across the globe. eg: if user types in S&P 500, use SPY."
                },
                {
                    "role": "user",
                    "content": sentence
                }
            ],
            response_format={"type": "json_object"}
        )

        gpt_params = response.choices[0].message.content
        gpt_dict = json.loads(gpt_params)
        params["ticker"] = gpt_dict.get("ticker")
        if gpt_dict.get("days"):
            params["days"] = int(gpt_dict.get("days"))

    except Exception as e:
        print(f"Error using GPT for extraction: {e}")

    # Format for OpenAI function calling
    function_call = {
        "name": "get_yahoo_finance",
        "arguments": {}
    }

    # Only include parameters that have values
    if params["ticker"]:
        function_call["arguments"]["ticker"] = params["ticker"]
    if params["days"] != 30:  # Only include days if different from default
        function_call["arguments"]["days"] = params["days"]

    return {
        "function_call": function_call,
        # Lower confidence if no ticker found
        "confidence": 0.95 if params["ticker"] else 0.6
    }
