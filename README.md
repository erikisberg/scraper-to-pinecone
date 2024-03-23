# Scraper to Pinecone to GPT

## Overview
The project consists of these main components:

scraper.py: Scrapes articles from the ImpactLoop website, capturing both the content and metadata of each article.

- Folder: websites

chunker.py: Processes the scraped HTML content, divides it into manageable chunks, and includes metadata for better context.

- JSON - chuncks_with_metadata
- JSON - processed_files.json

vectorizer.py: 

query.py: 