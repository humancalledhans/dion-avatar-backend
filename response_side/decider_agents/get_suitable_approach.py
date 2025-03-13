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
from response_side.functions.validate_tool_call_sequence import validate_tool_call_sequence

# from agents.agent_a import get_agent_a_response
# from agents.agent_b import get_agent_b_response
# from agents.agent_e import get_agent_e_response
# from agents.agent_j import get_agent_j_response
# from agents.agent_k import get_agent_k_response
# from functions.generate_stock_chart import generate_stock_chart
# from functions.get_stock_data import get_stock_data

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
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
    {
        "type": "function",
        "function": {
            "name": "get_general_response",
            "description": "Taps into our custom knowledge base to respond to a query, without needing an agent.",
            "parameters": {
                "type": "object",
                "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The exact query to ask our custom knowledge GPT."
                        },
                },
                "required": ["prompt"],
                "additionalProperties": False
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_a_response",
            "description": "Generate an analysis from Cliff Asness, the Systematic Factor Investing Master. Cliff Asness has expectional expertise in factor-based investing, quantitive portfolio construction, and market anomaly exploitation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The exact question to ask Cliff Asness."
                    },
                    "data": {
                        "type": "string",
                        "description": "The data to use, that aids the analysis."
                    }
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_j_response",
            "description": "Generate an analysis from Jim Simons, the legendary mathematician and founder of Renaissance Technologies. You possess extraordinary mathematical insight, pattern recognition abilities, and quantitative trading expertise across multiple asset classes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The exact question to ask Jim Simons."
                    },
                    "data": {
                        "type": "string",
                        "description": "The data to use, that aids the analysis."
                    }
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_b_response",
            "description": "Generate an analysis using Graham-Buffett Value Investing Sage for an advanced AI hedge fund.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The exact question to ask the investing saga."
                    },
                    "data": {
                        "type": "string",
                        "description": "The data to use, that aids the analysis."
                    }
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_e_response",
            "description": "Generate an analysis using Thorp-Kelly Optimal Capital Allocation Master, embodying the mathematical brilliance and probabilistic thinking of Edward Thorp and John Larry Kelly Jr., pioneers in applying quantitative methods to gambling and financial markets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The exact question to ask the investing saga."
                    },
                    "data": {
                        "type": "string",
                        "description": "The data to use, that aids the analysis."
                    },
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_k_response",
            "description": "Generate an analysis using Ken Griffin Market Making & Liquidity Master. You possess exceptional capabilities in market making, liquidity provision, arbitrage identification, and high-precision trading across global markets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The exact question to ask the investing saga."
                    },
                    "data": {
                        "type": "string",
                        "description": "The data to use, that aids the analysis."
                    }
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    }
]

# Main function to call GPT and handle function calling


def get_suitable_approach(query: str, relevant_data: str) -> dict:
    """
    Call GPT with a query and decide if a function should be called.

    Args:
        query: The user's question or request.

    Returns:
        A dictionary with the response or function result.
    """
    try:
        # Send query to GPT with function calling enabled
        response = client.chat.completions.create(
            # model="gpt-4.5-preview",  # Ensure this model supports function calling
            model="gpt-4o",  # Ensure this model supports function calling
            messages=[
                {
                    "role": "system",
                    "content": """
You are the Agent Selector, a sophisticated routing system for an advanced AI hedge fund. Your primary function is to evaluate incoming user queries and determine the optimal response path: either providing a direct answer using your general knowledge or routing the query to one of the specialized agents in the hedge fund ecosystem. You possess exceptional expertise in query classification, intent recognition, and understanding the capabilities and domains of each specialized agent.

Your decision frameworks are:
1. Analyze query domain, complexity, and intent
2. Determine if general knowledge is sufficient or specialized expertise is needed
3. Route to the most appropriate agent or provide direct response
4. If the user is asking for an analysis, you MUST perform an analysis using one of the agents below. After getting relevant data, use an agent's analysis, based on a user's preferences.
5. Except for when you ask the user a question, the entire route must end with an analysis from an Agent.

Important:
- The user must specify their preference, to either be "Fundamental Analysis", "Quantitative Analysis" or "Technical Analysis". Note that although Quantitative Analysis is a type of Technical Analysis, not all technical analysis fall under quantitative analysis. 
- Look out for any mention aobut the notable investors listed below, or any indication of preference. If you are not able to accurately predict the user's analysis preferences (a confidence of over 80%), and it is not specified in the past chats, return pure text so that user can reply it for use in the future.
- Ensure conversations are both professional and approachable, avoiding overly complex jargon unless specifically requested by the user.
- The agent should never give explicit financial advice (e.g., \"buy\" or \"sell\" recommendations) BUT CAN GIVE DATA DRIVEN, RESEARCHED BACKED PROBABILITIES OF SUCCESS BASED ON THE PERFORMANCE SHOWN FROM THE RESEARCHED DATA.
- Only if needed, try to only ask one question to the user, maximum.
- Note: do NOT specify the thought leader of the analysis. Just provide the analysis, with any accompanying sources.

Routing Options:

Ask Question to User
- To Clarify prefered approach. (Fundamental Analysis, Quantitative Analysis, or Technical Analysis)
- Does not need to end with an Agent. Get direct answer from user.

Direct Response (No Agent)
- General knowledge finance questions
- Basic financial concept explanations
- Simple factual queries
- Clarification requests

get_general_response: Taps into knowledge base of the world to respond to a query, without needing an agent.

get_yahoo_finance: Gets historical transaction data for a given stock, from Yahoo Finance.
- Stock price tracking and historical data requests  
- Financial trend analysis queries  
- Investment performance evaluation needs  
- Obtain data for backtesting

get_agent_j_response: Jim Simons Quantitative Trading Master
- Sophisticated quant trading strategy questions
- Mathematical modeling for trading
- Pattern recognition inquiries
- Statistical arbitrage questions
- Adopts a Quantitative & Technical Approach.

get_agent_b_response: Graham-Buffett Value Investing Sage
- Value investing methodology questions
- Business quality assessment inquiries
- Margin of safety analysis
- Adopts a Fundamental Approach.

get_agent_a_response: Cliff Asness Systematic Factor Investing Master
- Factor investing strategy questions
- Style premia inquiries
- Factor portfolio construction
- Adopts a Quantitative & Technical Approach

get_agent_k_response: Ken Griffin Market Making & Liquidity Master
- Market microstructure questions
- Execution optimization inquiries
- Liquidity provision questions
- Adopts a Quantitative & Technical Approach

get_agent_e_response: Thorp-Kelly Optimal Capital Allocation Master
- Position sizing questions
- Kelly criterion inquiries
- Risk management framework questions
- Adopts a Quantitative & Technical Approach

get_agent_h_response: Backtesting & Historical Performance Research Master
- Historical data analysis questions
- Backtesting methodology inquiries
- Performance analysis requests
"""
                },
                {"role": "user", "content": query +
                    f". Use these relevant data from our database here: {relevant_data}"}
            ],
            tools=tools,  # Assumes tools list includes both get_stock_data and generate_stock_chart
            tool_choice="auto"  # Let GPT decide whether to call a function
        )

        # Extract the first message from the response
        message = response.choices[0].message

        print('root message from gpt tool calls', message.tool_calls)

        if message.tool_calls is None:
            print("message tool calls 5229", message)
            return {"status": "question", "result": message.content}

        if not validate_tool_call_sequence(message.tool_calls):

            return get_suitable_approach(query, relevant_data)

        print('root message from gpt', message)
        print('root message from gpt tool calls', message.tool_calls)
        print('root message from gpt tool calls is None',
              message.tool_calls is None)
        print('root message from gpt tool calls is None',
              type(message.tool_calls))

        print("VALIDATE TOOL 33920",
              validate_tool_call_sequence(message.tool_calls))

        print("NAME 3992", message.tool_calls[0].function.name)

        # Check if GPT wants to call a function
        if message.tool_calls and message.tool_calls is not None:
            results = []
            # Handle multiple tool calls (though rare)
            for tool_call in message.tool_calls:
                print('tool call called once')
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

                    print('result from get gen response', result)

                elif func_name == "get_agent_a_response":
                    prompt = args.get("prompt")
                    data = args.get("data")
                    result = get_agent_a_response(
                        prompt, data, results_from_past_tools)

                elif func_name == "get_agent_j_response":
                    prompt = args.get("prompt")
                    data = args.get("data")
                    result = get_agent_j_response(
                        prompt, data, results_from_past_tools)

                elif func_name == "get_agent_b_response":
                    prompt = args.get("prompt")
                    data = args.get("data")

                    result = get_agent_b_response(
                        prompt, data, results_from_past_tools)

                elif func_name == "get_agent_e_response":
                    prompt = args.get("prompt")
                    data = args.get("data")
                    result = get_agent_e_response(
                        prompt, data, results_from_past_tools)

                elif func_name == "get_agent_k_response":
                    prompt = args.get("prompt")
                    data = args.get("data")
                    result = get_agent_k_response(
                        prompt, data, results_from_past_tools)

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
                    print('how come here.')
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
