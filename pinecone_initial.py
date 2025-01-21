import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone_initial

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key-here")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT",
                         "your-pinecone-environment-here")

# Initialize Pinecone
pinecone_initial.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# Index name in Pinecone, ensure it's created or exists
index_name = "ai-assistant"

# Check if index exists, if not, create it
if index_name not in pinecone_initial.list_indexes():
    pinecone_initial.create_index(
        name=index_name,
        dimension=1536,  # Dimension of OpenAI's text-embedding-ada-002
        metric="cosine"
    )

# Connect to the index
index = pinecone_initial.Index(index_name)

# Load documents
# This path should be to your data file
loader = TextLoader('path/to/your/document.txt')
documents = loader.load()

# Split text into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# Create embeddings and insert into Pinecone
embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")
db = Pinecone.from_documents(docs, embeddings, index_name=index_name)

print(f"Data uploaded to Pinecone index: {index_name}")

# Optionally, check the stats of your index after upload
stats = index.describe_index_stats()
print(stats)
