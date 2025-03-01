from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from response_side.openai_generate_response import generate_agent_t_response, generate_agent_ta_response, generate_response
from response_side.pinecone_query import retrieve_relevant_docs
from scehema import SchemasCopy

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/fetch_embedding_output")
async def fetch_embedding(req_body: SchemasCopy):
    query = req_body.user_input
    print('check out the query first pro', query)
    relevant_docs = retrieve_relevant_docs(query)

    if not relevant_docs:
        return "No relevant documents found to answer this query."

    response = generate_response(query, relevant_docs)
    print('whats the response? a string?', response)
    return {'data': response}


@app.post("/fetch_agent_output")
async def fetch_embedding(req_body: SchemasCopy):
    query = req_body.user_input
    previous_user_message = req_body.previous_user_message
    previous_bot_reply = req_body.previous_bot_reply
    relevant_docs = retrieve_relevant_docs(query, index_name="agent-t")

    if not relevant_docs:
        return "No relevant documents found to answer this query."

    response = generate_agent_t_response(
        query, relevant_docs, previous_user_message, previous_bot_reply)

    #
    max_tries = 5
    for attempt in range(max_tries):
        if len(response) <= 1999:
            break
        response = generate_agent_t_response(
            query, relevant_docs, previous_user_message, previous_bot_reply)
        print(
            f'Attempt {attempt + 1} to shorten response. Current length: {len(response)}')

    if len(response) > 1999:
        print("Unable to generate a response shorter than 2000 characters after several attempts.")
        # Optionally truncate the response, but this should be rare
        response = response[:1999]
    #

    return {'data': response}


@app.post("/fetch_agent_ta_output")
async def fetch_embedding(req_body: SchemasCopy):
    query = req_body.user_input
    previous_user_message = req_body.previous_user_message
    previous_bot_reply = req_body.previous_bot_reply

    relevant_docs = retrieve_relevant_docs(query, index_name="agent-ta")

    if not relevant_docs:
        return "No relevant documents found to answer this query."

    response = generate_agent_ta_response(
        query, relevant_docs, previous_user_message, previous_bot_reply)

    # Ensure response fits Discord's 2000-character limit
    max_tries = 5
    for attempt in range(max_tries):
        if len(response) <= 1999:
            break
        response = generate_agent_ta_response(
            query, relevant_docs, previous_user_message, previous_bot_reply)
        print(
            f'Attempt {attempt + 1} to shorten response. Current length: {len(response)}')

    if len(response) > 1999:
        print("Unable to shorten response below 2000 characters after attempts.")
        response = response[:1999]

    return {'data': response}
