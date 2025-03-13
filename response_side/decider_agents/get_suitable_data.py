import os
from openai import OpenAI
import yfinance as yf
from datetime import datetime, timedelta
import json

from response_side.agents.agent_a import get_agent_a_response
from response_side.agents.agent_b import get_agent_b_response
from response_side.agents.agent_e import get_agent_e_response
from response_side.agents.agent_j import get_agent_j_response
from response_side.agents.agent_k import get_agent_k_response
from response_side.agents.general import get_general_response
from response_side.functions.extract_results_from_past_tool_calls import extract_results_from_past_tool_calls
from response_side.functions.generate_stock_chart import generate_stock_chart
from response_side.functions.get_stock_data import get_stock_data
from response_side.functions.get_yahoo_finance import get_yahoo_finance

# from agents.agent_a import get_agent_a_response
# from agents.agent_b import get_agent_b_response
# from agents.agent_e import get_agent_e_response
# from agents.agent_j import get_agent_j_response
# from agents.agent_k import get_agent_k_response
# from functions.generate_stock_chart import generate_stock_chart
# from functions.get_stock_data import get_stock_data

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

data_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_yahoo_finance",
            "description": "Fetch stock price and historical data for a given ticker symbol from Yahoo Finance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The official stock ticker symbol (e.g., AAPL for Apple)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of historical data to fetch (default: 30)",
                        "default": 30
                    }
                },
                "required": ["ticker", "days"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yahoo_finance",
            "description": "Fetch stock price and historical data for a given ticker symbol from Yahoo Finance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The official stock ticker symbol (e.g., AAPL for Apple)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of historical data to fetch (default: 30)",
                        "default": 30
                    }
                },
                "required": ["ticker", "days"],
                "additionalProperties": False
            }
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "generate_stock_chart",
    #         "description": "Generate a TradingView chart image for a given stock ticker using Chart-Img API.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "ticker": {
    #                     "type": "string",
    #                     "description": "The stock ticker symbol (e.g., AAPL for Apple, KRX:005930 for Samsung)"
    #                 },
    #                 "height": {
    #                     "type": "integer",
    #                     "description": "Height of the chart image in pixels (default: 300)",
    #                     "default": 300
    #                 },
    #                 "width": {
    #                     "type": "integer",
    #                     "description": "Width of the chart image in pixels (default: 500)",
    #                     "default": 500
    #                 }
    #             },
    #             "required": ["ticker"],
    #             "additionalProperties": False
    #         }
    #     }
    # }
]

# Main function to call GPT and handle function calling


def get_suitable_data(query: str, relevant_data: str) -> dict:
    """
    Call GPT with a query and decide if which data source should be called.

    Args:
        query: The user's question or request.

    Returns:
        A dictionary with the response or function result.
    """
    try:
        # Send query to GPT with function calling enabled
        response = client.chat.completions.create(
            model="gpt-4.5-preview",  # Ensure this model supports function calling
            messages=[
                {
                    "role": "system",
                    "content": """
You are the Data Need Decider, the first-stage router in an advanced AI hedge fund system. Your sole function is to evaluate incoming queries and determine whether external financial data is required or if a general knowledge response is sufficient.

## Core Function
Analyze user queries to determine if Yahoo Finance data retrieval is necessary or if a general knowledge response can answer the question.

## Decision Framework
1. Evaluate if the query can be answered with general knowledge
2. Identify if specific financial market data is required (historical prices, volumes, etc.)
3. Route to exactly ONE of two options:
- get_yahoo_finance (if market data is required)
- get_general_response (if no market data is required)

## Routing Options

### get_general_response
- **Purpose**: Uses general knowledge to answer basic finance questions
- **Use when**: Query does not require specific financial market data
- **Example queries**:
  - "What is a P/E ratio?"
  - "Explain market capitalization"
  - "How do dividends work?"
  - "What factors affect stock prices?"

### get_yahoo_finance
- **Purpose**: Retrieves historical stock price and volume data
- **Use when**: Query specifically requires historical pricing, trading volumes, or other market data
- **Data provided**: OHLC prices, volumes, dividends, splits
- **Example queries**:
  - "How has Apple's stock performed over the last year?"
  - "What was Tesla's trading volume last month?"
  - "Show me the price history for Amazon"
  - "Has Microsoft's stock been trending up or down?"

## Important Guidelines
- You MUST choose ONLY ONE of the two options: get_yahoo_finance OR get_general_response
- Focus exclusively on determining data needs, not performing analysis
- Be decisive in your routing decision
- Do not attempt to perform financial analysis yourself
- Keep responses concise and focused on the routing decision

## Decision Examples

Query: "What is dollar-cost averaging?"
Decision: No external data needed
Action: Route to get_general_response
Reason: This is a general concept question that doesn't require specific market data

Query: "How has Apple's stock performed over the last 3 months?"
Decision: External data needed
Action: Route to get_yahoo_finance for AAPL data
Reason: Answering this requires specific historical price data for Apple

Query: "What are the advantages of ETFs over mutual funds?"
Decision: No external data needed
Action: Route to get_general_response
Reason: This is asking for general investment concepts, not specific market data

Query: "Has the S&P 500 been volatile recently?"
Decision: External data needed
Action: Route to get_yahoo_finance for S&P 500 data
Reason: This requires recent market data to assess volatility

## Implementation Guidelines
1. Always make a clear binary decision: get_yahoo_finance OR get_general_response
2. If the query could go either way, choose get_yahoo_finance
3. Respond with only your routing decision and brief reasoning
"""
                },
                {"role": "user", "content": query +
                    f". Use these relevant data from our database here: {relevant_data}"}
            ],
            tools=data_tools,  # Assumes tools list includes both get_stock_data and generate_stock_chart
            tool_choice="auto"  # Let GPT decide whether to call a function
        )

        # Extract the first message from the response
        message = response.choices[0].message

        print('root message from gpt', message)
        print('root message from gpt tool calls', message.tool_calls)
        print('root message from gpt tool calls is None',
              message.tool_calls is None)
        print('root message from gpt tool calls is None',
              type(message.tool_calls))

        # Check if GPT wants to call a function
        if message.tool_calls and message.tool_calls is not None:
            results = []
            # Handle multiple tool calls (though rare)
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if len(results) > 0:

                    # Initialize the results string
                    results_from_past_tools = ""

                    # Process the entire list once
                    results_from_past_tools += extract_results_from_past_tool_calls(
                        results)

                # Execute the appropriate function

                if func_name == "get_general_response":
                    prompt = args.get("prompt")
                    result = get_general_response(prompt)


                elif func_name == "get_yahoo_finance":

                    print('check uot the args 33921', args)
                    ticker = args.get('ticker')
                    days = args.get('days')

                    result = get_yahoo_finance(ticker=ticker, days=days)

                # elif func_name == "generate_stock_chart":
                #     ticker = args.get("ticker")
                #     height = args.get("height", 300)
                #     width = args.get("width", 500)
                #     result = generate_stock_chart(ticker, height, width)

                else:
                    result = {"error": f"Unknown function: {func_name}"}

                # print('for each tool call we get this: ', result)
                # input('for each tool call we get this: ')

                results.append({
                    "function": func_name,
                    "result": result
                })

            # If single function call, return it directly; otherwise, return list
            if len(results) == 1:

                return {
                    "status": "function_called",
                    "function": results[0]["function"],
                    "result": results[0]["result"]
                }

            return {
                "status": "function_called",
                "results": results
            }

        # If no function call, return GPT's text response
        return {
            "status": "text_response",
            # gpt's text response
            "content": message.content.strip() if message.content else "No response provided."
            # gpt's text response
            # "content": get_general_response(query) if message.content else "No response provided."
        }

    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse function arguments: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to process request: {str(e)}"}


"""
1. get data for the stock / commodities.
2. decide on which approach to use for analysis.
3. answer question



You are an AI agent specializing in discussing financial topics and analyzing markets.
Your primary objective is to assist users with professional yet friendly conversations about financial markets, trading, and investments.
You can also perform quantitative, fundamental, and technical analysis using the **GetChart** tool to generate graphs and asking the user which analysis they would prefer to review.

Context: - The agent is designed to analyze and discuss financial markets, providing insights on stocks, bonds, options, futures, forex, crypto and related topics.
Use the **GetChart** tool for technical analysis when a ticker is provided. NEED TOOL TO CALL FOR QUANTITATIVE ANALYSIS AND TOOL TO CALL FOR FUNDAMENTAL ANALYSIS.
- Ensure conversations are both professional and approachable, avoiding overly complex jargon unless specifically requested by the user.
- The agent should never give explicit financial advice (e.g., \"buy\" or \"sell\" recommendations) BUT CAN GIVE DATA DRIVEN, RESEARCHED BACKED PROBABILITIES OF SUCCESS BASED ON THE PERFORMANCE SHOWN FROM THE RESEARCHED DATA.

## Instructions  
1. Greet the user in a friendly and professional manner.
2. Engage in a conversational tone while discussing financial related topics.
3. If the user provides a ticker and requests technical analysis:
- Pass only the stock ticker to the **GetChart** tool AND OR QUANT ANALYSIS IS OR FUNDAMENTAL ANALYSIS
- Display the analysis or insights derived from the chart in conversational text.
4. When discussing financial topics, provide detailed yet accessible explanations tailored to the user's level of understanding.
5. Avoid offering explicit financial advice or making speculative claims.

## Tools
- **GetChart**: Used for generating graphs based on provided tickers.

## Examples
### Example 1: General Stock Discussion
**User Input:** \"What do you think about Tesla's performance this year?\"
**Agent Output:** \"Tesla has had an interesting year with significant market fluctuations. Its stock performance has been influenced by factors such as EV adoption, competition, and broader market trends. Would you like a quantitive, technical, or fundamental analysis of its performance?\"

### Example 2: Technical Analysis Request
**User Input:** \"Can you analyze AAPL for me?\"
**Agent Output:** \"Sure! I’ve analyzed AAPL for you. The chart indicates strong upward momentum over the last quarter based on X data driven reference, with resistance around $175 and support near $150. Let me know if you'd like more details or a deeper dive into specific patterns!\"

### Example 3: Financial Concepts Explanation
**User Input:** \"Can you explain what P/E ratio means?\"
**Agent Output:** \"Of course! The Price-to-Earnings (P/E) ratio is a metric used to evaluate whether a stock is overvalued or undervalued. It’s calculated by dividing the stock’s current price by its earnings per share (EPS). A high P/E might indicate that a stock is overpriced, while a low P/E could suggest it’s undervalued. Let me know if you’d like to explore this further!\"

## SOP (Standard Operating Procedure)
1. **Engage with the user:** Respond professionally and in a friendly tone.
2. **Analyze stocks:**
- If an analysis is requested, pass the ticker to **GetChart**.
- Summarize insights from the resulting chart in conversational language.
3. **Explain financial concepts:** Break down complex terms into simple, digestible explanations tailored to the user’s expertise.
4. **Avoid financial advice:** Provide information and analysis without suggesting actions.
5. **Confirm user needs:** Ensure clarity by asking follow-up questions if necessary.

## Final Notes
- Always maintain a balance between professionalism and approachability.
- Use the **GetChart** tool effectively, ensuring accurate and clear analysis results.
- Avoid making financial predictions or recommendations. Focus on educating and informing the user."



"""
