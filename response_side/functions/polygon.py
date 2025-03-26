import requests
import json
import datetime
from typing import Dict, List, Optional, Union, Any


class PolygonAPI:
    def __init__(self, api_key: str):
        """Initialize Polygon.io API with your API key."""
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def get_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed information about a stock ticker.

        Args:
            ticker: The stock ticker symbol (e.g., AAPL, MSFT, GOOG)

        Returns:
            Dictionary containing ticker details
        """
        endpoint = f"/v3/reference/tickers/{ticker}"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=self.headers)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("error", "Unknown error occurred")}

        if not data.get("results"):
            return {"error": f"No data found for ticker {ticker}"}

        ticker_data = data["results"]

        # Format response for GPT-4
        result = {
            "ticker": ticker_data.get("ticker", ""),
            "name": ticker_data.get("name", ""),
            "market": ticker_data.get("market", ""),
            "primary_exchange": ticker_data.get("primary_exchange", ""),
            "type": ticker_data.get("type", ""),
            "currency_name": ticker_data.get("currency_name", ""),
            "locale": ticker_data.get("locale", ""),
            "description": ticker_data.get("description", ""),
            "homepage_url": ticker_data.get("homepage_url", ""),
            "total_employees": ticker_data.get("total_employees", 0),
            "list_date": ticker_data.get("list_date", ""),
            "market_cap": ticker_data.get("market_cap", 0),
            "weighted_shares_outstanding": ticker_data.get("weighted_shares_outstanding", 0),
            "sic_code": ticker_data.get("sic_code", ""),
            "sic_description": ticker_data.get("sic_description", "")
        }

        return result

    def get_stock_price(self, ticker: str) -> Dict[str, Any]:
        """
        Get the latest stock price information.

        Args:
            ticker: The stock ticker symbol (e.g., AAPL, MSFT, GOOG)

        Returns:
            Dictionary containing current stock price data
        """
        endpoint = f"/v2/aggs/ticker/{ticker}/prev"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=self.headers)
        data = response.json()

        if response.status_code != 200 or data.get("status") != "OK":
            return {"error": data.get("error", "Unknown error occurred")}

        if not data.get("results"):
            return {"error": f"No price data found for ticker {ticker}"}

        price_data = data["results"][0]

        result = {
            "ticker": ticker,
            "close": price_data.get("c"),
            "high": price_data.get("h"),
            "low": price_data.get("l"),
            "open": price_data.get("o"),
            "volume": price_data.get("v"),
            "volume_weighted_avg_price": price_data.get("vw"),
            "trading_date": data.get("queryCount")
        }

        return result

    def get_daily_bars(self, ticker: str, from_date: str, to_date: str) -> Dict[str, Any]:
        """
        Get daily price bars for a ticker within a date range.

        Args:
            ticker: The stock ticker symbol (e.g., AAPL, MSFT, GOOG)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary containing daily price data
        """
        # Format the dates to the expected format: YYYY-MM-DD
        try:
            # Validate date format
            datetime.datetime.strptime(from_date, "%Y-%m-%d")
            datetime.datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD format."}

        endpoint = f"/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=self.headers)
        data = response.json()

        if response.status_code != 200 or data.get("status") != "OK":
            return {"error": data.get("error", "Unknown error occurred")}

        if not data.get("results"):
            return {"error": f"No price data found for ticker {ticker} in the specified date range"}

        # Format the response for GPT-4
        results = []
        for bar in data["results"]:
            timestamp_ms = bar.get("t")
            date = datetime.datetime.fromtimestamp(
                timestamp_ms / 1000).strftime('%Y-%m-%d') if timestamp_ms else "unknown"

            results.append({
                "date": date,
                "open": bar.get("o"),
                "high": bar.get("h"),
                "low": bar.get("l"),
                "close": bar.get("c"),
                "volume": bar.get("v"),
                "volume_weighted_avg_price": bar.get("vw", 0),
                "transactions": bar.get("n", 0)
            })

        return {
            "ticker": ticker,
            "from_date": from_date,
            "to_date": to_date,
            "results": results
        }

    def search_tickers(self, query: str) -> Dict[str, Any]:
        """
        Search for tickers based on a query string.

        Args:
            query: Search term for company name or ticker

        Returns:
            Dictionary containing search results
        """
        endpoint = "/v3/reference/tickers"
        url = f"{self.base_url}{endpoint}"

        params = {
            "search": query,
            "active": True,
            "sort": "ticker",
            "order": "asc",
            "limit": 10
        }

        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("error", "Unknown error occurred")}

        if not data.get("results"):
            return {"error": f"No tickers found matching '{query}'"}

        results = []
        for ticker in data["results"]:
            results.append({
                "ticker": ticker.get("ticker", ""),
                "name": ticker.get("name", ""),
                "market": ticker.get("market", ""),
                "locale": ticker.get("locale", ""),
                "primary_exchange": ticker.get("primary_exchange", ""),
                "type": ticker.get("type", ""),
                "currency_name": ticker.get("currency_name", ""),
                "last_updated_utc": ticker.get("last_updated_utc", "")
            })

        return {
            "query": query,
            "count": len(results),
            "results": results
        }

    def get_market_news(self, ticker: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get market news, optionally filtered by ticker.

        Args:
            ticker: Optional ticker symbol to filter news
            limit: Maximum number of news items to return (default: 10)

        Returns:
            Dictionary containing market news
        """
        endpoint = "/v2/reference/news"
        url = f"{self.base_url}{endpoint}"

        params = {"limit": limit}
        if ticker:
            params["ticker"] = ticker

        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("error", "Unknown error occurred")}

        if not data.get("results"):
            return {"error": "No news found"}

        results = []
        for news in data["results"]:
            results.append({
                "title": news.get("title", ""),
                "author": news.get("author", ""),
                "published_utc": news.get("published_utc", ""),
                "article_url": news.get("article_url", ""),
                "tickers": news.get("tickers", []),
                "amp_url": news.get("amp_url", ""),
                "image_url": news.get("image_url", ""),
                "description": news.get("description", "")
            })

        return {
            "ticker_filter": ticker if ticker else "All markets",
            "count": len(results),
            "results": results
        }

    def get_market_holidays(self) -> Dict[str, Any]:
        """
        Get upcoming market holidays and trading hours.

        Returns:
            Dictionary containing market holidays
        """
        endpoint = "/v1/marketstatus/upcoming"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=self.headers)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("error", "Unknown error occurred")}

        return {
            "holidays": data
        }

    def get_ticker_types(self) -> Dict[str, Any]:
        """
        Get available ticker types and asset classes.

        Returns:
            Dictionary containing ticker types
        """
        endpoint = "/v3/reference/tickers/types"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=self.headers)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("error", "Unknown error occurred")}

        if not data.get("results"):
            return {"error": "No ticker types found"}

        return {
            "ticker_types": data["results"]
        }

# OpenAI Function Definition


def polygon_tools_definition():
    """Return the function definitions for GPT-4 function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_ticker_details",
                "description": "Get detailed information about a specific stock ticker",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol, e.g., AAPL for Apple Inc."
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Get the latest price information for a stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol, e.g., AAPL for Apple Inc."
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_daily_bars",
                "description": "Get daily price bars for a ticker within a date range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol, e.g., AAPL for Apple Inc."
                        },
                        "from_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "to_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["ticker", "from_date", "to_date"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_tickers",
                "description": "Search for tickers based on a company name or partial ticker",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term for company name or ticker"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_market_news",
                "description": "Get market news, optionally filtered by ticker",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Optional ticker symbol to filter news"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of news items to return (default: 10)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_market_holidays",
                "description": "Get upcoming market holidays and trading hours",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_ticker_types",
                "description": "Get available ticker types and asset classes",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

# Function to handle function calls from GPT-4


def handle_function_call(api_instance, function_name, arguments):
    """
    Handle function calls from GPT-4.

    Args:
        api_instance: An instance of PolygonAPI
        function_name: The name of the function to call
        arguments: Dictionary of arguments for the function

    Returns:
        The result of the function call
    """
    if function_name == "get_ticker_details":
        return api_instance.get_ticker_details(arguments["ticker"])
    elif function_name == "get_stock_price":
        return api_instance.get_stock_price(arguments["ticker"])
    elif function_name == "get_daily_bars":
        return api_instance.get_daily_bars(
            arguments["ticker"],
            arguments["from_date"],
            arguments["to_date"]
        )
    elif function_name == "search_tickers":
        return api_instance.search_tickers(arguments["query"])
    elif function_name == "get_market_news":
        ticker = arguments.get("ticker")
        limit = arguments.get("limit", 10)
        return api_instance.get_market_news(ticker, limit)
    elif function_name == "get_market_holidays":
        return api_instance.get_market_holidays()
    elif function_name == "get_ticker_types":
        return api_instance.get_ticker_types()
    else:
        return {"error": f"Unknown function: {function_name}"}

# Example usage with OpenAI API


def example_openai_integration():
    """Example showing how to use these functions with OpenAI API."""
    import openai

    # Setup your keys
    openai.api_key = "your-openai-api-key"
    polygon_api_key = "your-polygon-api-key"

    # Initialize Polygon API
    polygon_api = PolygonAPI(polygon_api_key)

    # Get the function definitions
    tools = polygon_tools_definition()

    # Example conversation with function calling
    messages = [
        {"role": "user", "content": "What's the current stock price of Apple?"}
    ]

    # Call GPT-4 with function calling
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # Process the response
    message = response.choices[0].message

    # Check if GPT-4 wants to call a function
    if message.tool_calls:
        # Collect tool calls and add assistant message to conversation
        messages.append(message)

        # Process each tool call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Call the function
            function_response = handle_function_call(
                polygon_api, function_name, function_args)

            # Add the function response to the messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response)
            })

        # Get a new response from GPT-4
        second_response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        return second_response.choices[0].message.content

    return message.content


if __name__ == "__main__":
    # For testing purposes only
    API_KEY = "your-polygon-api-key"
    polygon = PolygonAPI(API_KEY)

    # Example: Get ticker details
    print(polygon.get_ticker_details("AAPL"))

    # Example: Search for a company
    print(polygon.search_tickers("Microsoft"))
