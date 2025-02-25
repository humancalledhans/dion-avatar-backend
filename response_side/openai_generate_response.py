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


def generate_agent_c_response(query, relevant_docs, previous_user_message=None, previous_bot_reply=None):
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
        past_context += "Use this history to provide a more informed and context-aware response.\n\n"

    messages = [
        {
            "role": "developer",
            "content": (
                "You are Agent C, an expert customer service agent for the course \"Trade Like The Pros\". "
                "You answer students' questions concisely on Discord (under 1999 characters), persuasively, "
                "and with awareness of the conversation history when provided."
            )
        },
        {
            "role": "user",
            "content": (
                f"User's past messages: {past_context}"
                f"Given the following information:\n\n{context}\n\n"
                f"Answer this query: {query}"
            )
        }
    ]

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return completion.choices[0].message.content.strip()


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
        past_context += "Use this history to provide a more informed and context-aware response.\n\n"

    messages = [
        {
            "role": "developer",
            "content": (
                "You are Agent TLTP, an expert customer service agent for the course \"Trade Like The Pros\". "
                "You answer students' questions concisely on Discord (under 1999 characters), persuasively, "
                "and with awareness of the conversation history when provided."
            )
        },
        {
            "role": "user",
            "content": (
                f"User's past messages: {past_context}"
                f"Given the following information:\n\n{context}\n\n"
                f"Answer the following question in less than 1999 characters: {query}"
            )
        }
    ]

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return completion.choices[0].message.content.strip()
