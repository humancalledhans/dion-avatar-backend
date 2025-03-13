def extract_results_from_past_tool_calls(results_from_past_tool_calls):
    # Extract 'result' only from objects where function is 'get_yahoo_finance'
    results = [item["result"] for item in results_from_past_tool_calls
               if "function" in item and item["function"] == "get_yahoo_finance" and "result" in item]

    if not results:
        return ""

    # Format the results with all historical data
    formatted_results = "\n\n".join(
        f"Ticker: {r['ticker']}\n"
        f"Company: {r['company_name']}\n"
        f"Current Price: ${r['current_price']}\n"
        f"Market Cap: ${r['market_cap']}\n"
        f"Historical Data:\n" + "\n".join(
            f"  {date}:\n"
            f"    Open: ${data['Open']:.2f}\n"
            f"    High: ${data['High']:.2f}\n"
            f"    Low: ${data['Low']:.2f}\n"
            f"    Close: ${data['Close']:.2f}\n"
            f"    Volume: {data['Volume']}"
            for date, data in r['historical_data'].items()
        )
        for r in results
    )

    # print('check out formatted reulst. messed up?', formatted_results)
    # input('formattedres')

    return formatted_results
