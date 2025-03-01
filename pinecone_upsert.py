import os
import time
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
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_KEY = "pcsk_6jqwp5_BLPY9FFhok3LcbUWMWpkjBouoobnRDgwn1KWLcwi1ncXiv1XSrTsWxBtpuvWd27"
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
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Fetch indexes list directly from the API
        headers = {
            "Api-Key": PINECONE_API_KEY,
            "X-Pinecone-API-Version": "2025-04"
        }

        # Product mapping with optional websites
        product_mapping = {
            "tltp_main_course": {
                "name": "TLTP Program",
                "website": "https://www.tradelikethepros.com/regular"
            },
            "trade_journal_offer": {
                "name": "Trade Journal Offer",
                "website": "https://www.tradelikethepros.com/trade-journal"
            },
            "tltp_toolkit_mid_ticket_offer": {
                "name": "TLTP Toolkit Offer",
                "website": "https://www.tradelikethepros.com/"
            },
            "tltp_offers_description": "All TLTP Offers & Brief Descriptions",  # No website
            "7_day_funded_trader_challenge": {
                "name": "7-day Funded Trader Challenge",
                "website": "https://www.tradelikethepros.com/challenge"
            },
            "faq": "Frequently Asked Questions & Answers"  # No website
        }

        response = requests.get(
            "https://api.pinecone.io/indexes", headers=headers)

        if response.status_code == 200:
            indexes = json.loads(response.text)
            index_names = [index['name'] for index in indexes['indexes']]
            index_name = "agent-ta"

            # If index exists, delete it to start fresh
            if index_name in index_names:
                print(
                    f"Index '{index_name}' exists. Deleting it to start with fresh data.")
                delete_response = requests.delete(
                    f"https://api.pinecone.io/indexes/{index_name}", headers=headers
                )
                if delete_response.status_code != 202:
                    print(
                        f"Failed to delete index '{index_name}'. Status code: {delete_response.status_code}, Response: {delete_response.text}")
                    return
                print(f"Index '{index_name}' deleted successfully.")

                # Wait briefly to ensure deletion propagates (optional)
                time.sleep(2)

            # Create the index (either after deletion or if it didn’t exist)
            print(f"Creating index '{index_name}'.")
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

            # Wait for index to be ready
            while True:
                try:
                    describe_response = requests.get(
                        f"https://api.pinecone.io/indexes/{index_name}", headers=headers)
                    if describe_response.status_code == 200:
                        break
                except Exception as ep:
                    print(f"Waiting for index to be ready: {ep}")
                    time.sleep(5)
            print(f"Index '{index_name}' created and is now ready.")

            index = pc.Index(index_name)

            # Directories where txt files are stored
            training_data_dir = f"training_data/{index_name}"
            common_dir = "training_data/common"
            directories = [training_data_dir, common_dir]

            # Iterate over each directory
            for directory in directories:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):

                        if filename.endswith(".txt"):
                            file_path = os.path.join(directory, filename)

                            with open(file_path, 'r', encoding='utf-8') as file:
                                text = file.read().strip()

                                # Extract base filename (without extension)
                                base_name = filename.split(".")[0].lower()

                                # Get product info from mapping; default to filename without underscores
                                product_info = product_mapping.get(base_name)
                                if product_info is None:
                                    product_name = base_name.replace("_", "")
                                    metadata = {
                                        "product": product_name,
                                        "source": filename,
                                        "directory": directory,
                                    }
                                else:
                                    # Handle cases with dictionary vs. string
                                    if isinstance(product_info, dict):
                                        product_name = product_info["name"]
                                        metadata = {
                                            "product": product_name,
                                            "source": filename,
                                            "directory": directory,
                                        }
                                        # Only add website if it exists
                                        if "website" in product_info:
                                            metadata["website"] = product_info["website"]
                                    else:
                                        product_name = product_info
                                        metadata = {
                                            "product": product_name,
                                            "source": filename,
                                            "directory": directory,
                                        }

                                # Chunk the text
                                chunks = chunk_text(text)

                                for i, chunk in enumerate(chunks):
                                    vector = get_text_embedding(chunk)
                                    doc_id = f"{directory.split('/')[-1]}_{base_name}_{i}"

                                    # Add chunk-specific fields to metadata
                                    metadata.update({
                                        "chunk_index": i,
                                        "total_chunks": len(chunks),
                                        "text": chunk
                                    })

                                    print("base aname", base_name)
                                    if base_name == 'all_tltp_offers_and_prices':
                                        print('the text from chunking', chunk)

                                    index.upsert(
                                        vectors=[(doc_id, vector, metadata)], namespace="ns1")
                                    # print(
                                    #     f"Upserted: {directory}/{filename}, chunk {i}, product: {product_name}, metadata: {metadata}")

        else:
            print(
                f"Failed to fetch indexes. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error in pinecone_upsert: {str(e)}")


if __name__ == '__main__':
    pinecone_upsert()
