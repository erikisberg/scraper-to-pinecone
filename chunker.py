from bs4 import BeautifulSoup
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
import hashlib
import json
import tiktoken

def tiktoken_len(text):
    """Calculate the length of text in tokens using tiktoken."""
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

def clean_html_text(html_content):
    """Convert HTML content to clean text."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def process_single_html_file(file_path):
    """Process a single HTML file, chunk its content, and save the chunks."""
    # Initialize the text splitter with desired settings
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Adjust as needed
        chunk_overlap=20,  # Adjust as needed
        length_function=tiktoken_len
    )

    documents = []

    try:
        # Generate a unique ID based on the file path
        m = hashlib.md5()
        m.update(file_path.encode('utf-8'))
        uid = m.hexdigest()[:12]

        # Load the HTML content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"HTML content: {content[:100]}")  # print the first 100 characters of the HTML content

        # Clean the HTML content to get plain text
        clean_text = clean_html_text(content)
        print(f"Clean text content: {clean_text[:100]}")  # print the first 100 characters
        print(f"Clean text length: {len(clean_text)}")  # print the length of the clean text

        # Split the clean text into chunks
        chunks = text_splitter.split_text(clean_text)
        print(f"Number of chunks: {len(chunks)}")  # print the number of chunks

        # Create document data for each chunk
        for i, chunk in enumerate(chunks):
            documents.append({
                'id': f'{uid}-{i}',
                'text': chunk,
                'source': file_path
            })

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    # Save the documents to a JSONL file
    with open('train.jsonl', 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')

    return documents

# Path to your HTML file
file_path = "scraped_content.html"
documents = process_single_html_file(file_path)

print(f"Processed {len(documents)} chunks.")
