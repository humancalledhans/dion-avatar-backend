import uuid
import time
import os
import jwt

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agora_token_builder import RtcTokenBuilder
from fastapi.middleware.cors import CORSMiddleware

from response_side.openai_generate_response import generate_agent_q_response, generate_agent_t_response, generate_agent_ta_response, generate_response
from response_side.pinecone_query import retrieve_relevant_docs
from scehema import SchemasCopy, TokenRequest

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AVAILABLE_ROLES = ['host', 'guest']

# Agora credentials from environment variables
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")


@app.get("/")
async def root():
    return {"message": "Hello World"}

# Token expiration time (24 hours)
TOKEN_EXPIRATION_TIME = 24 * 3600


class TokenRequest(BaseModel):
    channel_name: str
    uid: str
    role: str = "host"  # "host" or "audience"


class TokenResponse(BaseModel):
    token: str
    app_id: str
    channel_name: str
    uid: str
    expires_at: int


@app.post("/generate-agora-token", response_model=TokenResponse)
async def generate_agora_token(request: TokenRequest):
    try:
        # Validate environment variables
        if not AGORA_APP_ID or not AGORA_APP_CERTIFICATE:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: Missing Agora credentials"
            )

        # Validate inputs
        if not request.channel_name or not request.uid:
            raise HTTPException(
                status_code=400,
                detail="channel_name and uid are required"
            )

        # Set role
        if request.role == "host":
            role = 1  # RtcRole.Role_Publisher
        else:
            role = 2  # RtcRole.Role_Subscriber

        # Calculate expiration time
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + TOKEN_EXPIRATION_TIME

        # Use fixed UIDs instead of auto-assignment
        if request.uid == "Dion (Admin)":
            uid_int = 1001  # Fixed UID for admin
        elif request.uid.isdigit():
            uid_int = int(request.uid)
        else:
            # Generate consistent UID from username hash
            uid_int = abs(hash(request.uid)) % 900000 + 100000  # 6-digit range

        print(
            f"Generating token for: channel={request.channel_name}, uid={uid_int}, role={role}")

        # Generate token with integer UID
        token = RtcTokenBuilder.buildTokenWithUid(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            request.channel_name,
            uid_int,
            role,
            privilege_expired_ts
        )

        return TokenResponse(
            token=token,
            app_id=AGORA_APP_ID,
            channel_name=request.channel_name,
            uid=str(uid_int),  # Return the integer UID as string
            expires_at=privilege_expired_ts
        )

    except Exception as e:
        print(f"Token generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate token: {str(e)}"
        )


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
    # max_tries = 5
    # for attempt in range(max_tries):
    #     if len(response) <= 1999:
    #         break
    #     response = generate_agent_t_response(
    #         query, relevant_docs, previous_user_message, previous_bot_reply)
    #     print(
    #         f'Attempt {attempt + 1} to shorten response. Current length: {len(response)}')

    # if len(response) > 1999:
    #     print("Unable to generate a response shorter than 2000 characters after several attempts.")
    #     # Optionally truncate the response, but this should be rare
    #     response = response[:1999]
    # #

    return {'data': response}


@app.post("/fetch_agent_ta_output")
async def fetch_embedding(req_body: SchemasCopy):
    query = req_body.user_input
    previous_user_message = req_body.previous_user_message
    previous_bot_reply = req_body.previous_bot_reply

    print('previous user msg', previous_user_message)
    print('previous bot reply', previous_bot_reply)

    relevant_docs = retrieve_relevant_docs(query, index_name="agent-ta")

    if not relevant_docs:
        return "No relevant documents found to answer this query."

    response = generate_agent_ta_response(
        query, relevant_docs, previous_user_message, previous_bot_reply)

    # Ensure response fits Discord's 2000-character limit
    # max_tries = 5
    # for attempt in range(max_tries):
    #     if len(response) <= 1999:
    #         break
    #     response = generate_agent_ta_response(
    #         query, relevant_docs, previous_user_message, previous_bot_reply)
    #     print(
    #         f'Attempt {attempt + 1} to shorten response. Current length: {len(response)}')

    # if len(response) > 1999:
    #     print("Unable to shorten response below 2000 characters after attempts.")
    #     response = response[:1999]

    return {'data': response}


@app.post("/fetch_agent_q_output")
async def fetch_embedding(req_body: SchemasCopy):
    query = req_body.user_input
    previous_user_message = req_body.previous_user_message
    previous_bot_reply = req_body.previous_bot_reply

    # relevant_docs = retrieve_relevant_docs(
    #     query, index_name="agent-ta", top_k=3, max_per_product=1)

    # if not relevant_docs:
    #     return "No relevant documents found to answer this query."

    relevant_docs = ''

    response = generate_agent_q_response(
        query, relevant_docs, previous_user_message, previous_bot_reply, poppy=True)

    if type(response) == dict:
        print("RESPOnse 395", response)

        if response['status'] == 'text_response':
            response = response['content']

        elif response['status'] == 'function_called':

            print("check returned data", response)
            # returned data would be in this form:
            """
            {'status': 'function_called', 'results': 
                [
                    {'function': 'get_yahoo_finance', 'result': {<result here>}},
                    {'function': 'get_agent_b_response', 'result': {<result here>}}
                ]
            }

            note that agent responses are usually like:
            {'text': '', 'cost': 1.4634}
            """
            try:
                results = response['results']

                # assuming that the final function call will always be an agent call, which returns poppy text, in poppy format.
                print("resutlts ", results[-1])
                response = results[-1]['result']['text']

            except KeyError:
                if isinstance(response, dict) and 'result' in response and isinstance(response['result'], dict) and 'text' in response['result']:
                    response = response['result']['text']
                else:
                    response = response['result']

        elif response['status'] == 'question':
            response = response['result']

        else:
            response = response['result']['ai_reply']

    else:
        print("RESponse NOT dict", response)

    # Ensure response fits Discord's 2000-character limit
    # max_tries = 5
    # for attempt in range(max_tries):
    #     if len(response) <= 1999:
    #         break
    #     response = generate_agent_ta_response(
    #         query, relevant_docs, previous_user_message, previous_bot_reply)
    #     print(
    #         f'Attempt {attempt + 1} to shorten response. Current length: {len(response)}')

    # if len(response) > 1999:
    #     print("Unable to shorten response below 2000 characters after attempts.")
    #     response = response[:1999]

    return {'data': response}
