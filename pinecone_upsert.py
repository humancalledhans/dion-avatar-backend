import os

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
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("dion-gpt")

    # Directory where txt files are stored
    training_data_dir = "training_data"

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

                    # print('checking the actual data', entry)
                    # input('waiting')
                    # Upsert the vector into Pinecone
                    index.upsert(vectors=[entry], namespace="ns1")
                    print(f"Upserted: {filename}, chunk {i}")


if __name__ == '__main__':
    pinecone_upsert()
