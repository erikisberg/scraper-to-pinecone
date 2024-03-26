import os
import jsonlines
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# Print the variables to check if they are loaded correctly
print(f"PINECONE_API_KEY: {PINECONE_API_KEY}")
print(f"INDEX_NAME: {INDEX_NAME}")

try:
    # Initialize Pinecone client
    pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone_client.Index(name=INDEX_NAME)
    print("Pinecone client initialized successfully")  # Success message
except Exception as e:
    print(f"Error: {e}")

# Open the JSONL file and iterate over its items
with jsonlines.open('chunks_with_metadata.jsonl') as reader:
    for item in reader:
        try:
            # Update the metadata of the item in the Pinecone index
            index.update(
                id=item['id'],
                set_metadata={"text": item["text"]}
            )
            print(f"Item {item['id']} updated successfully")  # Success message
        except Exception as e:
            print(f"Error updating item {item['id']}: {e}")