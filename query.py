from pinecone import Pinecone
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone client
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
index = pinecone_client.Index(name=INDEX_NAME)

def generate_query_vector(query_text, model="text-embedding-ada-002"):
    """
    Convert query text into an embedding using the specified OpenAI model.
    """
    response = openai.Embedding.create(input=query_text, engine=model)
    query_vector = response["data"][0]["embedding"]
    return query_vector

def query_pinecone(query_vector, top_k=5, include_values=False, include_metadata=True, filter=None):
    """
    Query the Pinecone index with the provided query vector.
    Optionally refine the search results with metadata filters.
    """
    query_params = {
        "vector": query_vector,
        "top_k": top_k,
        "include_values": include_values,
        "include_metadata": include_metadata
    }
    if filter:
        query_params["filter"] = filter
    
    response = index.query(**query_params)
    return response

def construct_gpt_prompt(matches):
    """
    Construct a prompt for GPT based on Pinecone query results without relying on document summaries.
    """
    prompt = "Ge ett svar baserat på följande dokumentuppgifter:\n\n"
    for match in matches:
        doc_id = match.get('id')
        text = match.get('text')  # Get the document content
        prompt += f"Document ID: {doc_id}\n\n"
        prompt += f"Document Content: {text}\n\n"  # Include the document content in the prompt
    prompt += "Answer:"
    return prompt




def query_gpt_with_context(prompt):
    """
    Query the GPT model with the constructed prompt using the chat API endpoint.
    """
    chat_session_params = {
        "model": "gpt-4",  # Adjust the model as necessary
        "messages": [{"role": "system", "content": "Du är onlinetidningen Impact Loops hjälpfulla assistent, med tillgång till deras artiklar och information. "},
                     {"role": "user", "content": prompt}]
    }
    
    response = openai.ChatCompletion.create(**chat_session_params)
    gpt_answer = response["choices"][0]["message"]["content"]
    return gpt_answer.strip()

# Example usage
query_text = "Vad kan du berätta om bikupor?"
query_vector = generate_query_vector(query_text)

# Query Pinecone
response = query_pinecone(query_vector, top_k=5)

# Check if response is valid and contains 'matches'
if response and 'matches' in response:
    # Construct a GPT prompt based on the query results
    prompt = construct_gpt_prompt(response['matches'])
    # Query GPT with the constructed prompt
    gpt_answer = query_gpt_with_context(prompt)
    print("GPT's Answer:", gpt_answer)
else:
    print("No matches found or invalid response.")
