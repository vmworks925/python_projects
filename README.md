# Moglix Product Info Search API

This project provides a FastAPI-based service to search product information using semantic embeddings and Pinecone vector search.

## Features

- REST API for adding and retrieving items
- Semantic search endpoint using Cohere embeddings and Pinecone
- MongoDB integration for product data

## Setup

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Set your API keys:**
   - Update your Cohere and Pinecone API keys in `main.py` and `embedding_search.py`.

3. **Run the API server:**
   ```
   uvicorn main:app --reload
   ```

4. **API Endpoints:**
   - `GET /` — Health check
   - `GET /items` — List items
   - `POST /items` — Add item
   - `GET /items/{item_id}` — Get item by ID
   - `POST /search` — Search items by query

## File Structure

- `main.py` — FastAPI app and endpoints
- `embedding_search.py` — Embedding and search service class
- `hello.py` — Data ingestion and Pinecone upsert script

## Notes

- Ensure MongoDB, Cohere, and Pinecone services are accessible.
- For production, secure your API keys and consider environment variables.