import jsonlines
import openai
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

print("PINECONE_API_KEY:", PINECONE_API_KEY)

# Initialize Pinecone client
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# Access the index
index = pinecone_client.Index(name=INDEX_NAME)

def preprocess_metadata(metadata):
    """
    Preprocess metadata to replace null values with an appropriate placeholder.
    This ensures all metadata values are compatible with Pinecone's requirements.
    """
    print("Before preprocessing: ", metadata)  # Print metadata before preprocessing


    for key, value in metadata.items():
        if value is None:
            metadata[key] = "unknown"  # Replace None with "unknown" or another placeholder
        elif isinstance(value, list) and not value:
            metadata[key] = ["unknown"]  # Replace empty lists with a list containing a placeholder
    return metadata

def load_data(file_path):
    """
    Load data from a JSON lines file.
    """

    print(f"Loading data from {file_path}")  # Print the file path

    data = []
    with jsonlines.open(file_path) as f:
        for item in f:
            # Preprocess metadata for each item
            item["metadata"] = preprocess_metadata(item.get("metadata", {}))
            data.append(item)
    return data

def init_openai(api_key):
    """
    Initialize OpenAI API.
    """

    print("Initializing OpenAI API with provided API key")  # Print a message before initialization

    openai.api_key = api_key

    print("OpenAI API initialized successfully")  # Print a message after initialization

    return "text-embedding-ada-002"

import numpy as np
import base64

def create_and_index_embeddings(data, model):
    """
    Create embeddings and populate the Pinecone index.
    """
    batch_size = 32
    for start_index in range(0, len(data), batch_size):
        batch = data[start_index:start_index + batch_size]
        text_batch = [item["text"] for item in batch if item["text"].strip()]
        ids_batch = [item["id"] for item in batch if item["text"].strip()]
        metadata_batch = [item["metadata"] for item in batch if item["text"].strip()]
        
        if not text_batch:  # Skip if the batch is empty after filtering
            continue
        
        res = openai.Embedding.create(input=text_batch, engine=model)
        embeds = [record["embedding"] for record in res["data"]]
        
        # Prepare the data for upserting into Pinecone
        vectors_to_upsert = [
            {
                "id": ids_batch[i],
                "values": embeds[i],
                "metadata": metadata_batch[i]
            }
            for i in range(len(embeds))
        ]
        
        # Upsert the batch of vectors into Pinecone
        index.upsert(vectors=vectors_to_upsert)


if __name__ == "__main__":
    # Load the data from chunks_with_metadata.jsonl
    train_data = load_data("chunks_with_metadata.jsonl")

    # Initialize OpenAI Embedding API with your API key
    MODEL = init_openai(OPENAI_API_KEY)

    # Create embeddings and populate the index with the train data
    create_and_index_embeddings(train_data, MODEL)
