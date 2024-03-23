# Scraper to Pinecone to GPT

## Overview
The project consists of these main components:

_scraper.py:_ Scrapes articles from the ImpactLoop website, capturing both the content and metadata of each article.

- Folder: websites

_chunker.py:_ Processes the scraped HTML content, divides it into manageable chunks, and includes metadata for better context.

- JSON - chuncks_with_metadata
- JSON - processed_files.json

_vectorizer.py:_  The `vectorizor.py` script is used to create embeddings for a given dataset and index them using Pinecone.


_query.py:_ 