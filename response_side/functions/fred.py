import requests
import json
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

class FREDAPI:
    def __init__(self, api_key: str):
        """Initialize FRED API with your API key."""
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
    
    def get_series(self, series_id: str, observation_start: Optional[str] = None, 
                  observation_end: Optional[str] = None) -> Dict[str, Any]:
        """
        Get time series data for a specific economic indicator.
        
        Args:
            series_id: The FRED series ID (e.g., GDP, UNRATE)
            observation_start: Optional start date in YYYY-MM-DD format
            observation_end: Optional end date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing the series data
        """
        endpoint = "/series/observations"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        # Add date filters if provided
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        if not data.get("observations"):
            return {"error": f"No data found for series {series_id}"}
        
        # Process the observations - handle missing values and convert to proper types
        observations = []
        for obs in data["observations"]:
            # FRED uses '.' to indicate missing values
            value = obs.get("value")
            if value == ".":
                numeric_value = None
            else:
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    numeric_value = None
            
            observations.append({
                "date": obs.get("date"),
                "value": numeric_value,
                "realtime_start": obs.get("realtime_start"),
                "realtime_end": obs.get("realtime_end")
            })
        
        # Get series information for context
        series_info = self.get_series_info(series_id)
        if "error" in series_info:
            series_title = "Unknown"
            series_units = "Unknown"
            series_frequency = "Unknown"
        else:
            series_title = series_info.get("title", "Unknown")
            series_units = series_info.get("units", "Unknown")
            series_frequency = series_info.get("frequency", "Unknown")
        
        result = {
            "series_id": series_id,
            "title": series_title,
            "units": series_units,
            "frequency": series_frequency,
            "observation_start": observation_start or data.get("observations", [{}])[0].get("date", ""),
            "observation_end": observation_end or data.get("observations", [{}])[-1].get("date", ""),
            "observations": observations
        }
        
        return result
    
    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata about a specific economic indicator.
        
        Args:
            series_id: The FRED series ID (e.g., GDP, UNRATE)
            
        Returns:
            Dictionary containing series metadata
        """
        endpoint = "/series"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        if not data.get("seriess"):
            return {"error": f"No information found for series {series_id}"}
        
        series = data["seriess"][0]
        
        result = {
            "id": series.get("id", ""),
            "title": series.get("title", ""),
            "units": series.get("units", ""),
            "frequency": series.get("frequency", ""),
            "frequency_short": series.get("frequency_short", ""),
            "seasonal_adjustment": series.get("seasonal_adjustment", ""),
            "seasonal_adjustment_short": series.get("seasonal_adjustment_short", ""),
            "observation_start": series.get("observation_start", ""),
            "observation_end": series.get("observation_end", ""),
            "popularity": series.get("popularity", 0),
            "last_updated": series.get("last_updated", ""),
            "notes": series.get("notes", "")
        }
        
        return result
    
    def search_series(self, search_text: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for economic data series based on keywords.
        
        Args:
            search_text: Keywords to search for
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            Dictionary containing search results
        """
        endpoint = "/series/search"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "search_text": search_text,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        if not data.get("seriess"):
            return {"error": f"No series found matching '{search_text}'"}
        
        results = []
        for series in data["seriess"]:
            results.append({
                "id": series.get("id", ""),
                "title": series.get("title", ""),
                "units": series.get("units", ""),
                "frequency": series.get("frequency", ""),
                "seasonal_adjustment": series.get("seasonal_adjustment", ""),
                "observation_start": series.get("observation_start", ""),
                "observation_end": series.get("observation_end", ""),
                "popularity": series.get("popularity", 0)
            })
        
        return {
            "search_text": search_text,
            "count": len(results),
            "results": results
        }
    
    def get_category(self, category_id: int = 0) -> Dict[str, Any]:
        """
        Get information about a category of economic data.
        
        Args:
            category_id: FRED category ID (default: 0, which is the root category)
            
        Returns:
            Dictionary containing category information
        """
        endpoint = "/category"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "category_id": category_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        if not data.get("categories"):
            return {"error": f"No information found for category {category_id}"}
        
        category = data["categories"][0]
        
        # Get child categories
        children = self.get_category_children(category_id)
        
        # Get series in this category
        series = self.get_category_series(category_id)
        
        result = {
            "id": category.get("id", 0),
            "name": category.get("name", ""),
            "parent_id": category.get("parent_id", 0),
            "children": children.get("categories", []),
            "series": series.get("seriess", [])
        }
        
        return result
    
    def get_category_children(self, category_id: int = 0) -> Dict[str, Any]:
        """
        Get child categories for a specific category.
        
        Args:
            category_id: FRED category ID (default: 0, which is the root category)
            
        Returns:
            Dictionary containing child categories
        """
        endpoint = "/category/children"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "category_id": category_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        return data
    
    def get_category_series(self, category_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        Get series belonging to a specific category.
        
        Args:
            category_id: FRED category ID
            limit: Maximum number of series to return (default: 10)
            
        Returns:
            Dictionary containing series in the category
        """
        endpoint = "/category/series"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "category_id": category_id,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        return data
    
    def get_releases(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get economic data releases.
        
        Args:
            limit: Maximum number of releases to return (default: 10)
            
        Returns:
            Dictionary containing release information
        """
        endpoint = "/releases"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error_code" in data:
            return {"error": data.get("error_message", "Unknown error occurred")}
        
        return data

# Common FRED series IDs with descriptions for reference
COMMON_FRED_SERIES = {
    "GDP": "Gross Domestic Product",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index for All Urban Consumers: All Items",
    "FEDFUNDS": "Federal Funds Effective Rate",
    "GS10": "10-Year Treasury Constant Maturity Rate",
    "MORTGAGE30US": "30-Year Fixed Rate Mortgage Average",
    "DCOILWTICO": "Crude Oil Prices: West Texas Intermediate (WTI)",
    "GASREGW": "US Regular All Formulations Gas Price",
    "HOUST": "Housing Starts: Total: New Privately Owned Housing Units Started",
    "RSXFS": "Advance Retail Sales: Retail and Food Services, Total",
    "INDPRO": "Industrial Production Index",
    "PAYEMS": "All Employees, Total Nonfarm",
    "PCE": "Personal Consumption Expenditures",
    "M2": "M2 Money Stock",
    "DFF": "Federal Funds Effective Rate",
    "SP500": "S&P 500",
    "VIXCLS": "CBOE Volatility Index: VIX",
    "T10Y2Y": "10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity",
    "USREC": "NBER based Recession Indicators for the United States",
    "GFDEBTN": "Federal Debt: Total Public Debt"
}

# OpenAI Function Definition
def fred_tools_definition():
    """Return the function definitions for GPT-4 function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_series",
                "description": "Get time series data for a specific economic indicator from FRED",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "series_id": {
                            "type": "string",
                            "description": "The FRED series ID (e.g., GDP, UNRATE, CPIAUCSL)"
                        },
                        "observation_start": {
                            "type": "string",
                            "description": "Optional start date in YYYY-MM-DD format"
                        },
                        "observation_end": {
                            "type": "string",
                            "description": "Optional end date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["series_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_series_info",
                "description": "Get metadata about a specific economic indicator from FRED",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "series_id": {
                            "type": "string",
                            "description": "The FRED series ID (e.g., GDP, UNRATE, CPIAUCSL)"
                        }
                    },
                    "required": ["series_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_series",
                "description": "Search for economic data series based on keywords",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_text": {
                            "type": "string",
                            "description": "Keywords to search for (e.g., unemployment, inflation, housing)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "required": ["search_text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_category",
                "description": "Get information about a category of economic data in FRED",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category_id": {
                            "type": "integer",
                            "description": "FRED category ID (default: 0, which is the root category)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_releases",
                "description": "Get economic data releases from FRED",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of releases to return (default: 10)"
                        }
                    }
                }
            }
        }
    ]

# Function to handle function calls from GPT-4
def handle_function_call(api_instance, function_name, arguments):
    """
    Handle function calls from GPT-4.
    
    Args:
        api_instance: An instance of FREDAPI
        function_name: The name of the function to call
        arguments: Dictionary of arguments for the function
        
    Returns:
        The result of the function call
    """
    if function_name == "get_series":
        series_id = arguments["series_id"]
        observation_start = arguments.get("observation_start")
        observation_end = arguments.get("observation_end")
        return api_instance.get_series(series_id, observation_start, observation_end)
    
    elif function_name == "get_series_info":
        return api_instance.get_series_info(arguments["series_id"])
    
    elif function_name == "search_series":
        search_text = arguments["search_text"]
        limit = arguments.get("limit", 10)
        return api_instance.search_series(search_text, limit)
    
    elif function_name == "get_category":
        category_id = arguments.get("category_id", 0)
        return api_instance.get_category(category_id)
    
    elif function_name == "get_releases":
        limit = arguments.get("limit", 10)
        return api_instance.get_releases(limit)
    
    else:
        return {"error": f"Unknown function: {function_name}"}

# Example usage with OpenAI API
def example_openai_integration():
    """Example showing how to use these functions with OpenAI API."""
    import openai
    
    # Setup your keys
    openai.api_key = "your-openai-api-key"
    fred_api_key = "your-fred-api-key"
    
    # Initialize FRED API
    fred_api = FREDAPI(fred_api_key)
    
    # Get the function definitions
    tools = fred_tools_definition()
    
    # Example conversation with function calling
    messages = [
        {"role": "user", "content": "What's the current unemployment rate in the US?"}
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
            function_response = handle_function_call(fred_api, function_name, function_args)
            
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

# Helper function to visualize FRED data
def plot_fred_series(series_data, title=None, figsize=(12, 6)):
    """
    Create a simple plot of FRED data.
    
    Args:
        series_data: Result from get_series() function
        title: Optional custom title for the plot
        figsize: Size of the figure (width, height)
        
    Returns:
        matplotlib figure
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    
    # Extract data and convert to DataFrame
    observations = series_data.get("observations", [])
    df = pd.DataFrame(observations)
    
    # Convert date to datetime and value to float
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    # Drop rows with missing values
    df = df.dropna(subset=["value"])
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df["date"], df["value"])
    
    # Add details
    plot_title = title or f"{series_data.get('title')} ({series_data.get('series_id')})"
    ax.set_title(plot_title)
    ax.set_xlabel("Date")
    ax.set_ylabel(series_data.get("units", "Value"))
    ax.grid(True)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # For testing purposes only
    API_KEY = "your-fred-api-key"
    fred = FREDAPI(API_KEY)
    
    # Example: Get unemployment rate data
    print(fred.get_series("UNRATE", "2020-01-01", "2023-01-01"))
    
    # Example: Search for inflation data
    print(fred.search_series("inflation"))