from openai import OpenAI


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
        messages=[
            {"role": "developer", "content": "You are a helpful assistant that provides answers based on given context."},
            {"role": "user", "content": f"""Given the context:\n\n{
                context}\n\nAnswer the following query: {query}"""}
        ]
    )

    return completion.choices[0].message.content.strip()


def generate_agent_t_response(query, relevant_docs, previous_user_message=None, previous_bot_reply=None):
    try:
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
                    "You are Agent T, an expert customer service agent for the course \"Trade Like The Pros\". "
                    "You answer students' questions concisely on Discord (under 1999 characters), persuasively, "
                    "and with awareness of the conversation history when provided."
                    "Feel free to answer anything regarding offers, if you have them in the customer service database."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User has asked these: {past_context}"
                    f"Prioritise and understand user's past chats. If and Only if useful, use these information from the Customer Service Database:\n\n{context}\n\n"
                    f"Answer this query: {query}"
                )
            }
        ]

        import logging
        logging.info("full message with gpt t", messages)

        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return completion.choices[0].message.content.strip()

    except Exception as er:
        print("exception in genet t response", er)


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
                "You are Agent TLTP, an expert customer service agent for the course \"Trade Like The Pros\". "
                "You answer students' questions concisely on Discord (under 1999 characters), persuasively, "
                "and with awareness of the conversation history when provided."
            )
        },
        {
            "role": "user",
            "content": (
                f"User has asked these: {past_context}"
                f"Prioritise and understand user's past chats. If and Only if useful, use these information from the TLTP Course:\n\n{context}\n\n"
                f"Answer the following question in less than 1999 characters: {query}"
            )
        }
    ]

    print("full message with gpt ta", messages)

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return completion.choices[0].message.content.strip()
