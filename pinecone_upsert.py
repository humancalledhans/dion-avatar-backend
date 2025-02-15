import os
import requests
import json

from dotenv import load_dotenv
from chunk_text import chunk_text
from pinecone import Pinecone
from openai import OpenAI
import openai

load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")

openai.api_key = OPENAI_API_KEY
client = OpenAI()


def get_text_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def pinecone_upsert():
    pc = Pinecone(
        api_key="pcsk_6jqwp5_BLPY9FFhok3LcbUWMWpkjBouoobnRDgwn1KWLcwi1ncXiv1XSrTsWxBtpuvWd27")

    # Fetch indexes list directly from the API
    headers = {
        "Api-Key": "pcsk_6jqwp5_BLPY9FFhok3LcbUWMWpkjBouoobnRDgwn1KWLcwi1ncXiv1XSrTsWxBtpuvWd27",
        "X-Pinecone-API-Version": "2025-04"
    }
    response = requests.get("https://api.pinecone.io/indexes", headers=headers)

    if response.status_code == 200:
        indexes = json.loads(response.text)
        index_names = [index['name'] for index in indexes['indexes']]
        index_name = "agent-c"

        if index_name not in index_names:
            print(f"Index '{index_name}' does not exist. Creating it now.")
            index_data = {
                "name": index_name,
                "dimension": 1536,
                "metric": "cosine",
                "spec": {
                    "serverless": {
                        "cloud": "aws",
                        "region": "us-east-1"
                    }
                },
                "tags": {
                    "example": "tag",
                    "environment": "production"
                },
                "deletion_protection": "disabled"

            }

            create_response = requests.post(
                "https://api.pinecone.io/indexes", headers=headers, data=json.dumps(index_data))
            if create_response.status_code != 201:
                print(
                    f"Failed to create index. Status code: {create_response.status_code}, Response: {create_response.text}")
                return

            # Wait for index to be ready. Note: This is a simplistic wait; in practice, you might want a more robust check.
            import time
            while True:
                try:
                    describe_response = requests.get(
                        f"https://api.pinecone.io/indexes/{index_name}", headers=headers)
                    if describe_response.status_code == 200:
                        break
                except Exception:
                    time.sleep(5)  # Wait for 5 seconds before checking again
            print(f"Index '{index_name}' created and is now ready.")

        index = pc.Index(index_name)

        # Directory where txt files are stored
        training_data_dir = "training_data/agent_c"

        # Iterate over each file in the directory
        for filename in os.listdir(training_data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(training_data_dir, filename)

                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read().strip()  # Read content of the file

                    # Chunk the text
                    chunks = chunk_text(text)

                    for i, chunk in enumerate(chunks):
                        # Convert each chunk to vector using OpenAI's embedding model
                        vector = get_text_embedding(chunk)

                        # Create an entry for upsert with a unique ID based on filename and chunk index
                        entry = {
                            "id": f"{filename.split('.')[0]}_{i}",
                            "values": vector,
                            "metadata": {
                                "source": filename,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "text": chunk
                            }
                        }

                        # Upsert the vector into Pinecone
                        index.upsert(vectors=[entry], namespace="ns1")
                        print(f"Upserted: {filename}, chunk {i}")
    else:
        print(f"Failed to fetch indexes. Status code: {response.status_code}")


if __name__ == '__main__':
    pinecone_upsert()
