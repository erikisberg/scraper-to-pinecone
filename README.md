# Scraper to Pinecone to GPT

## Overview
The project consists of these main components:

- `scraper.py`: This script scrapes articles from the ImpactLoop website, capturing both the content and metadata of each article.
    - Folder: `websites` - Storage of each subpage crawled by the scraper.py function, one json-file for each subpage. 

- `chunker.py`: This script processes the scraped HTML content, divides it into manageable chunks, and includes metadata for better context.
    - JSON: `chunks_with_metadata.json` - Result from chunker.py process. 
    - JSON: `processed_files.json` - List of all json-files from the scraping-process that has been chunked.  

- `vectorizor.py`: This script is used to create embeddings for a given dataset and index them using Pinecone.

- `query.py`: This script is used to generate a query vector for a given text, query Pinecone with the vector, and then use the results to construct a prompt for the GPT model.