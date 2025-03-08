import os
import requests

# New function: Generate chart using Chart-Img API


def generate_stock_chart(ticker: str = "BINANCE:BTCUSDT", interval: str = "4h", height: int = 300) -> dict:
    """
    Generate a stock chart URL using the Chart-Img API v1 GET endpoint.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'NASDAQ:MSFT' or 'BINANCE:BTCUSDT')
        interval (str): Time interval for the chart (e.g., '4h')
        height (int): Height of the chart in pixels
    Returns:
        dict: {'chart_url': str} on success, {'error': str} on failure
    """
    url = "https://api.chart-img.com/v1/tradingview/advanced-chart"
    params = {
        "symbol": ticker.upper(),  # Use provided ticker or default
        "interval": '4h',
        "height": height,
        "key": os.getenv("CHART_IMG_API_KEY")
    }

    try:

        print('check params', params)
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Check Content-Type
        content_type = response.headers.get("Content-Type", "").lower()
        print(f"Content-Type for {ticker}: {content_type}")
        print(f"Raw response (first 100 chars): {response.text[:100]}...")

        # Handle based on Content-Type
        if "application/json" in content_type:
            result = response.json()
            return {
                "ticker": ticker.upper(),
                "chart_url": result.get("url", "No URL in JSON response"),
                "status": "success"
            }
        elif "image" in content_type:
            # Determine file extension based on Content-Type
            ext = "png" if "png" in content_type else "jpeg"
            # Sanitize ticker for filename (replace invalid chars)
            safe_ticker = ticker.replace(":", "_")
            filename = f"chart_{safe_ticker}.{ext}"

            # Write image to file
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Saved image to {filename}")

            # Return local file path
            return {
                "ticker": ticker.upper(),
                # Full path for clarity
                "chart_url": os.path.abspath(filename),
                "status": "success"
            }
        else:
            return {
                "ticker": ticker.upper(),
                "chart_url": response.text.strip(),  # Fallback for unexpected text
                "status": "success"
            }

    except requests.exceptions.HTTPError as e:
        return {"error": f"Failed to generate chart: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except ValueError:
        return {"error": "Invalid response format from API"}


def get_stock_chart_url(yahoo_dict, default_ticker="BINANCE:BTCUSDT", interval="4h", height=300):
    """
    Returns a stock chart URL based on ticker from yahoo_dict or a default.

    Args:
        yahoo_dict (dict): Dictionary containing yahoo context (with 'result' or 'results')
        default_ticker (str): Fallback ticker symbol (e.g., 'BINANCE:BTCUSDT')
        interval (str): Time interval for the chart
        height (int): Height of the chart in pixels
    Returns:
        str: The chart URL if successful, or an error message if failed
    """
    try:
        # Try to get ticker from 'result' or 'results'
        content = yahoo_dict.get('result')
        if content is None:
            content = yahoo_dict.get('results')

        # If content is a dict, look for a ticker symbol; otherwise use default
        ticker = default_ticker
        if isinstance(content, dict):
            ticker = content.get(
                'symbol', content.get('ticker', default_ticker))
        elif isinstance(content, str):
            ticker = content.strip().upper()

        # Generate stock chart
        chart_result = generate_stock_chart(
            ticker, interval=interval, height=height)

        # Return URL or error message
        if "error" in chart_result:
            error_msg = chart_result["error"]
            if "422" in error_msg:
                return f"Invalid ticker '{ticker}' - try exchange prefix (e.g., 'NASDAQ:MSFT'): {error_msg}"
            return error_msg
        return chart_result["chart_url"]

    except Exception as e:
        return f"Error processing request: {str(e)}"
