import hashlib
import json
import os
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
import tiktoken

def tiktoken_len(text):
    """Calculate the length of text in tokens using tiktoken."""
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

def load_processed_files_list(filename='processed_files.json'):
    """Load the list of processed files."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    else:
        return []

def save_processed_files_list(processed_files, filename='processed_files.json'):
    """Save the updated list of processed files."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(processed_files, file, ensure_ascii=False, indent=4)

def process_single_json_file(file_path, processed_files):
    """Process a single JSON file, chunk its content, and save the chunks with metadata."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Adjust as needed
        chunk_overlap=20,  # Adjust as needed
        length_function=tiktoken_len
    )

    documents = []

    try:
        m = hashlib.md5()
        m.update(file_path.encode('utf-8'))
        uid = m.hexdigest()[:12]

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        content = data['content']
        metadata = data['metadata']

        chunks = text_splitter.split_text(content)

        for i, chunk in enumerate(chunks):
            documents.append({'id': f'{uid}-{i}', 'text': chunk, 'metadata': metadata, 'source': file_path})

        # Append documents to the output file
        with open('chunks_with_metadata.jsonl', 'a', encoding='utf-8') as f:  # Note 'a' for appending
            for doc in documents:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    # Update the list of processed files
    processed_files.append(file_path)
    save_processed_files_list(processed_files)

    return documents

directory_path = "websites"
processed_files = load_processed_files_list()  # Load list of processed files
processed_documents = []

for filename in os.listdir(directory_path):
    if filename.endswith(".json"):
        file_path = os.path.join(directory_path, filename)
        if file_path not in processed_files:  # Check if the file has been processed
            documents = process_single_json_file(file_path, processed_files)
            processed_documents.extend(documents)

print(f"Processed {len(processed_documents)} chunks.")
