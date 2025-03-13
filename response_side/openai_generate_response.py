from datetime import datetime
import json
from openai import OpenAI

from response_side.append_sites import append_sites
from response_side.functions.get_yahoo_finance import extract_yahoo_finance_params, get_yahoo_finance
from response_side.decider_agents.get_suitable_approach import get_suitable_approach

# from append_sites import append_sites
# from functions.get_yahoo_finance import extract_yahoo_finance_params, get_yahoo_finance
# from decider_agents.get_suitable_approach import get_suitable_approach


def generate_response(query, relevant_docs):
    # Prepare the context by concatenating relevant documents
    context = "\n\n".join([doc['text'] for doc in relevant_docs])

    # Construct the prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides answers based on given context."},
        {"role": "user", "content": f"""Given the context:\n\n{
            context}\n\nAnswer the following query: {query}"""}
    ]

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return completion.choices[0].message.content.strip()


def generate_agent_t_response(query, relevant_docs, previous_user_message=None, previous_bot_reply=None):
    try:
        # Prepare the context from relevant documents, including product names and websites if present
        context = "\n\n".join(
            [f"Product: {doc['product']}" + (f" - Website: {doc['website']}" if 'website' in doc else "") + f" - {doc['text']}"
             for doc in relevant_docs]
        )

        # Construct past conversation context with explicit instructions
        past_context = ""
        if previous_user_message or previous_bot_reply:
            past_context = (
                "You have access to recent conversation history, which you must use to ensure your response aligns with the user’s intent. "
                f"Previous user message: {previous_user_message if previous_user_message else 'None'} "
                f"Previous bot reply: {previous_bot_reply if previous_bot_reply else 'None'} "
                "Analyze this history to understand the user’s prior questions and maintain context in your answer."
            )
        else:
            past_context = "No prior conversation history is available, so respond based solely on the current query and customer service database."

        # Construct the messages array with improved prompts
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Agent T, an expert customer service agent for the Trade Like The Pros program. "
                    "Your role is to answer students’ questions about offers, enrollment, and general program details concisely within 1999 characters for Discord, persuasively to encourage engagement, and accurately based on the customer service database. "
                    "You must remain aware of conversation history when provided and use it to maintain context. "
                    "For questions about offers or products, provide precise answers from the database, using the product names (e.g., 'TLTP Toolkit, Mid Level Offer')."
                    "Whenever your response mentions a product that has a website URL in the database, you must include that website URL as plain text, formatted as 'See [URL]' (e.g., 'See https://www.tradelikethepros.com'), without any brackets or labels like '[Trade Like The Pros]'; do not omit the URL under any circumstances if it exists in the database."
                )
            },
            {
                "role": "user",
                "content": (
                    f"{past_context} "
                    "The user has asked the following question, and you must prioritize past chats to ensure consistency. "
                    f"Here is the customer service database information, labeled by product and including website URLs where available, which you should use only if relevant: {context} "
                    f"Answer the current query accurately and concisely: {query} "
                )
            }
        ]

        import logging
        print("full message payload", messages)

        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return append_sites(completion.choices[0].message.content.strip())

    except Exception as er:
        logging.error(f"Exception in generate_agent_t_response: {er}")
        return "Sorry, I encountered an error while processing your request."


def generate_agent_ta_response(query, relevant_docs, previous_user_message=None, previous_bot_reply=None):
    # Prepare the context from relevant documents
    context = "\n\n".join([doc['text'] for doc in relevant_docs])

    # Construct the prompt with past message awareness
    past_context = ""
    if previous_user_message or previous_bot_reply:
        past_context = "You have access to the following recent conversation history:\n"
        if previous_user_message:
            past_context += f"Previous user message: {previous_user_message}\n"
        if previous_bot_reply:
            past_context += f"Previous bot reply: {previous_bot_reply}\n"
        past_context += "Use this chat history to provide a more informed and context-aware response.\n\n"

    messages = [
        {
            "role": "system",
            "content": (
                "You are Agent TLTP, an expert Q&A agent for the course \"Trade Like The Pros\". "
                "Your role is to answer students’ questions about the course curriculum concisely, step by step, and accurately based on the curriculum database. "
                "You must remain aware of conversation history when provided and use it to maintain context. "
                "You must be able to provide the answers, and give course members the exact step by step on how to achieve their desired situation."
                "Plese provide suitable breakdowns, and use cases as well for each question as well, if not mentioned."
                "Keep the responses and exmaples relevant to Futures and Crypto, as that is the courses's main focus."
            )
        },
        {
            "role": "user",
            "content": (
                f"User has asked these: {past_context}"
                f"Prioritise and understand user's past chats. If and Only if useful, use these information from the TLTP Course:\n\n{context}\n\n"
                f"Here is the course curriculum database information, labeled by product and including website URLs where available, which you should use only if relevant: {context} "
                f"Answer the current query accurately and concisely: {query} "
            )
        }
    ]

    print("full message with gpt ta", messages)

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return append_sites(completion.choices[0].message.content.strip())


def call_poppy(prompt):
    import requests
    import json

    # Base URL without query parameters for cleanliness
    base_url = "https://poppyai-api.vercel.app/api/conversation"

    # Parameters that might be required by the API (kept in URL or headers)
    params = {
        "api_key": "gp_Energetic_Turtle_LZyL1NFyUhbsQdCWjFQq8T0xm7g2",
        "board_id": "falling-waterfall-DSk9F",
        "chat_id": "1-chatNode-cold-rock-HFkyy"
    }

    print("prompt 3392", prompt)

    with open('prompt_33920', 'w', encoding='utf-8') as file:
        file.write(prompt)

    # Payload with the prompt (sent in the body as JSON)
    payload = {
        "prompt": prompt,
        "model": "claude-3.7-sonnet"
    }

    # Headers to specify JSON content
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request
        response = requests.post(
            url=base_url,
            params=params,  # Query parameters in the URL
            data=json.dumps(payload),  # JSON-encoded body
            headers=headers
        )

        # Check if the request was successful
        response.raise_for_status()

        # Print the response for debugging
        print("RESPONSE 55339", response.content)

        # Return the response content
        return response.content.decode('utf-8')

    except requests.exceptions.RequestException as e:
        # Handle errors (e.g., network issues, bad status codes)
        print(f"Error calling PoppyAI API: {e}")
        return None


def generate_agent_q_response(query, relevant_data, previous_user_message=None, previous_bot_reply=None, poppy=None):
    # Prepare the context from relevant documents
    # context = "\n\n".join([doc['text'] for doc in relevant_docs])

    # user_preferences = input(
    #     "Please state your analysis preferences (Quantitative, Analytical, Fundamental)")

    analysed_approach = get_suitable_approach(
        query + "\n Below are the past user replies:" + f"\n{previous_user_message}" + "Please use the information appropriately.", relevant_data)

    return analysed_approach

    # # add yahoo finance context.
    # yahoo_context = call_gpt_with_function(query)

    # if yahoo_context is None:
    #     yahoo_context = call_gpt_with_function(query)

    # print('check out yahoo context', yahoo_context)

    # if yahoo_context.get('status') and yahoo_context.get('status') == 'text_response':
    #     print("yahoo text res", yahoo_context)
    #     yahoo_context == ''

    # else:
    #     yahoo_context = yahoo_context.get('result') if yahoo_context.get(
    #         'result') is not None else yahoo_context.get('results')

    # # Construct the prompt with past message awareness
    # past_context = ""

    # current_datetime = datetime.now()

    # if len(yahoo_context) > 5:
    #     past_context += f"You have acquired data below from Yahoo Finance, that is directly relevant to the user's question. Use it appropriately.\n\n{yahoo_context}. Today's date is {current_datetime}."

    # if previous_user_message or previous_bot_reply:
    #     past_context += "You have access to the following recent conversation history:\n"
    #     if previous_user_message:
    #         past_context += f"Previous user message: {previous_user_message}\n"
    #     if previous_bot_reply:
    #         past_context += f"Previous bot reply: {previous_bot_reply}\n"
    #     past_context += "Use this chat history to provide a more informed and context-aware response.\n\n"

    # if poppy:

    # cpcp = call_poppy(
    #     f"User has asked these: {past_context}"
    #     f"Prioritise and understand user's past chats. If and Only if useful, use these information from the TLTP Course:\n\n{context}\n\n"
    #     f"Here is the course curriculum database information, labeled by product and including website URLs where available, which you should use only if relevant: {context} "
    #     f"Answer the current query accurately and concisely: {query}"
    # )

    # result_dict = json.loads(cpcp)

    # return append_sites(result_dict['ai_reply'])

    # messages = [
    #     {
    #         "role": "system",
    #         "content": (
    #             "You are Agent TLTP, an expert Q&A agent for the course \"Trade Like The Pros\". "
    #             "Your role is to answer students’ questions about the course curriculum concisely, step by step, and accurately based on the curriculum database. "
    #             "You must remain aware of conversation history when provided and use it to maintain context. "
    #             "You must be able to provide the answers, and give course members the exact step by step on how to achieve their desired situation."
    #             "Plese provide suitable breakdowns, and use cases as well for each question as well, if not mentioned."
    #             "Keep the responses and exmaples relevant to Futures and Crypto, as that is the courses's main focus."
    #         )
    #     },
    #     {
    #         "role": "user",
    #         "content": (
    #             f"User has asked these: {past_context}"
    #             f"Prioritise and understand user's past chats. If and Only if useful, use these information from the TLTP Course:\n\n{context}\n\n"
    #             f"Here is the course curriculum database information, labeled by product and including website URLs where available, which you should use only if relevant: {context} "
    #             f"Answer the current query accurately and concisely: {query} "
    #         )
    #     }
    # ]

    # print("full message with gpt ta", messages)

    # client = OpenAI()

    # completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=messages
    # )

    # return append_sites(completion.choices[0].message.content.strip())


def write_pretty_response(query, filename='answer'):
    # Generate the response (assuming it returns a list of dicts)
    response = generate_agent_q_response(query=query)

    print('check out response no get', response)
    # Safely extract ai_reply from either 'result' or 'content'
    result_dict = response.get('result')  # Try 'result' first
    if result_dict is None:
        # Fallback to 'content' if 'result' is None
        result_dict = response.get('content')

    if type(result_dict) == 'dict':
        # Now get ai_reply from whichever dictionary we found (or None if neither exists)
        ai_reply = result_dict.get('ai_reply') if result_dict else None

    else:
        ai_reply = result_dict

    # Print for debugging
    print('check out response with get ----------\n', ai_reply)

    # Write to file (convert to string if needed)
    with open('response_33920', 'w', encoding='utf-8') as file:
        file.write(str(ai_reply) if ai_reply is not None else "No ai_reply found")


if __name__ == '__main__':
    query = input("Hi! Please enter your question below...\n")
    write_pretty_response(query=query)

    # print(generate_agent_q_response(query=query))
    # print("------\n\n" + generate_agent_q_response(query=query))
