import jsonlines
import openai
import pinecone
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "your_default_index_name") # Default index name if not set in .env
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp") # Default environment if not set in .env

# Load train.jsonl file
def load_data(file_path):
    data = []
    with jsonlines.open(file_path) as f:
        for item in f:
            data.append(item)
    return data

# Initialize OpenAI API
def init_openai(api_key):
    openai.api_key = api_key
    return "text-embedding-ada-002"

# Initialize Pinecone index
def init_pinecone(api_key, index_name, dimension):
    pinecone.init(api_key=api_key, environment=PINECONE_ENVIRONMENT)
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=dimension)
    index = pinecone.Index(index_name)
    return index

# Create embeddings and populate the index
def create_and_index_embeddings(data, model, index):
    batch_size = 32
    for start_index in range(0, len(data), batch_size):
        text_batch = [item["text"] for item in data[start_index:start_index + batch_size]]
        ids_batch = [item["id"] for item in data[start_index:start_index + batch_size]]
        res = openai.Embedding.create(input=text_batch, engine=model)
        embeds = [record["embedding"] for record in res["data"]]
        to_upsert = [
            {"id": ids_batch[i], "values": embeds[i]} for i in range(len(embeds))
        ]
        index.upsert(vectors=to_upsert)

if __name__ == "__main__":
    # Load the data from train.jsonl
    train_data = load_data("train.jsonl")

    # Initialize OpenAI Embedding API
    MODEL = init_openai(OPENAI_API_KEY)

    # Get embeddings dimension
    sample_embedding = openai.Embedding.create(input="sample text", engine=MODEL)["data"][0]["embedding"]
    EMBEDDING_DIMENSION = len(sample_embedding)

    # Initialize Pinecone index
    chatgpt_index = init_pinecone(PINECONE_API_KEY, INDEX_NAME, EMBEDDING_DIMENSION)

    # Create embeddings and populate the index with the train data
    create_and_index_embeddings(train_data, MODEL, chatgpt_index)
