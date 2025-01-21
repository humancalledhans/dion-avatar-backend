from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from response_side.openai_generate_response import generate_response
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
