from openai import OpenAI

from response_side.append_sites import append_sites


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
