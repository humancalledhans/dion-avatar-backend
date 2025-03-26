import requests
import json
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field

class AlphaVantageAPI:
    def __init__(self, api_key: str):
        """Initialize Alpha Vantage API with your API key."""
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest stock price and basic information for a given symbol.
        
        Args:
            symbol: The stock symbol (e.g., AAPL, MSFT, GOOG)
            
        Returns:
            Dictionary containing stock price data
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            return {"error": data["Error Message"]}
        
        if "Global Quote" not in data or not data["Global Quote"]:
            return {"error": f"No data found for symbol {symbol}"}
        
        quote = data["Global Quote"]
        
        # Format the response in a clean way for GPT-4
        result = {
            "symbol": quote.get("01. symbol", ""),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", "").replace("%", ""),
            "volume": int(quote.get("06. volume", 0)),
            "latest_trading_day": quote.get("07. latest trading day", ""),
            "previous_close": float(quote.get("08. previous close", 0)),
            "open": float(quote.get("02. open", 0)),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0))
        }
        
        return result

    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview information for a given symbol.
        
        Args:
            symbol: The stock symbol (e.g., AAPL, MSFT, GOOG)
            
        Returns:
            Dictionary containing company information
        """
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if not data or "Error Message" in data:
            return {"error": f"No data found for symbol {symbol}"}
        
        # Return a subset of the most useful fields for GPT-4
        result = {
            "symbol": data.get("Symbol", ""),
            "name": data.get("Name", ""),
            "description": data.get("Description", ""),
            "exchange": data.get("Exchange", ""),
            "currency": data.get("Currency", ""),
            "country": data.get("Country", ""),
            "sector": data.get("Sector", ""),
            "industry": data.get("Industry", ""),
            "market_cap": data.get("MarketCapitalization", ""),
            "pe_ratio": data.get("PERatio", ""),
            "dividend_yield": data.get("DividendYield", ""),
            "52_week_high": data.get("52WeekHigh", ""),
            "52_week_low": data.get("52WeekLow", ""),
            "50_day_moving_avg": data.get("50DayMovingAverage", ""),
            "200_day_moving_avg": data.get("200DayMovingAverage", ""),
        }
        
        return result
    
    def search_symbol(self, keywords: str) -> List[Dict[str, str]]:
        """
        Search for stocks based on keywords/ticker symbols.
        
        Args:
            keywords: Search term (company name or symbol)
            
        Returns:
            List of matching stocks with their details
        """
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            return [{"error": data["Error Message"]}]
        
        matches = data.get("bestMatches", [])
        
        results = []
        for match in matches:
            results.append({
                "symbol": match.get("1. symbol", ""),
                "name": match.get("2. name", ""),
                "type": match.get("3. type", ""),
                "region": match.get("4. region", ""),
                "market_open": match.get("5. marketOpen", ""),
                "market_close": match.get("6. marketClose", ""),
                "timezone": match.get("7. timezone", ""),
                "currency": match.get("8. currency", ""),
                "match_score": match.get("9. matchScore", "")
            })
        
        return results
    
    def get_forex_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Get current exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code (e.g., USD)
            to_currency: Target currency code (e.g., EUR)
            
        Returns:
            Dictionary with exchange rate information
        """
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            return {"error": data["Error Message"]}
        
        if "Realtime Currency Exchange Rate" not in data:
            return {"error": f"No exchange rate data found for {from_currency} to {to_currency}"}
        
        exchange_data = data["Realtime Currency Exchange Rate"]
        
        result = {
            "from_currency_code": exchange_data.get("1. From_Currency Code", ""),
            "from_currency_name": exchange_data.get("2. From_Currency Name", ""),
            "to_currency_code": exchange_data.get("3. To_Currency Code", ""),
            "to_currency_name": exchange_data.get("4. To_Currency Name", ""),
            "exchange_rate": float(exchange_data.get("5. Exchange Rate", 0)),
            "last_refreshed": exchange_data.get("6. Last Refreshed", ""),
            "timezone": exchange_data.get("7. Time Zone", ""),
            "bid_price": float(exchange_data.get("8. Bid Price", 0)) if "8. Bid Price" in exchange_data else None,
            "ask_price": float(exchange_data.get("9. Ask Price", 0)) if "9. Ask Price" in exchange_data else None
        }
        
        return result

# OpenAI Function Definition
def alpha_vantage_tools_definition():
    """Return the function definitions for GPT-4 function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Get the latest price and basic information for a stock symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock symbol, e.g., AAPL for Apple Inc."
                        }
                    },
                    "required": ["symbol"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_company_overview",
                "description": "Get company overview information for a stock symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock symbol, e.g., MSFT for Microsoft Corporation"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_symbol",
                "description": "Search for stocks based on keywords or partial symbols",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "Search term (company name or symbol)"
                        }
                    },
                    "required": ["keywords"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_forex_rate",
                "description": "Get the current exchange rate between two currencies",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_currency": {
                            "type": "string",
                            "description": "Source currency code (e.g., USD)"
                        },
                        "to_currency": {
                            "type": "string",
                            "description": "Target currency code (e.g., EUR)"
                        }
                    },
                    "required": ["from_currency", "to_currency"]
                }
            }
        }
    ]

# Function to handle function calls from GPT-4
def handle_function_call(api_instance, function_name, arguments):
    """
    Handle function calls from GPT-4.
    
    Args:
        api_instance: An instance of AlphaVantageAPI
        function_name: The name of the function to call
        arguments: Dictionary of arguments for the function
        
    Returns:
        The result of the function call
    """
    if function_name == "get_stock_price":
        return api_instance.get_stock_price(arguments["symbol"])
    elif function_name == "get_company_overview":
        return api_instance.get_company_overview(arguments["symbol"])
    elif function_name == "search_symbol":
        return api_instance.search_symbol(arguments["keywords"])
    elif function_name == "get_forex_rate":
        return api_instance.get_forex_rate(
            arguments["from_currency"], 
            arguments["to_currency"]
        )
    else:
        return {"error": f"Unknown function: {function_name}"}

# Example usage with OpenAI API
def example_openai_integration():
    """Example showing how to use these functions with OpenAI API."""
    import openai
    
    # Setup your keys
    openai.api_key = "your-openai-api-key"
    alpha_vantage_api_key = "your-alpha-vantage-api-key"
    
    # Initialize Alpha Vantage API
    av_api = AlphaVantageAPI(alpha_vantage_api_key)
    
    # Get the function definitions
    tools = alpha_vantage_tools_definition()
    
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
            function_response = handle_function_call(av_api, function_name, function_args)
            
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
    API_KEY = "your-alpha-vantage-api-key"
    av = AlphaVantageAPI(API_KEY)
    
    # Example: Get stock price
    print(av.get_stock_price("AAPL"))
    
    # Example: Search for a company
    print(av.search_symbol("Microsoft"))