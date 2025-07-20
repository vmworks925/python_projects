import os
import requests
import cohere
from pinecone import Pinecone, ServerlessSpec
from pymongo import MongoClient
from sympy import true
import time

pc = Pinecone(api_key="pcsk_3ErmbN_Nw1raDwAD1ycbPq6RXBgrw8Xdnys4JKxce1AMVJYVcHce7fLe5M7iYbp8GTHDZj")
co = cohere.Client("Cj1OpLxjMTqbWew5VvgAPxMyk80OeZuLj5LCXoAG")

mongo_uri = "mongodb://10.0.2.115:27017"
mongo_client = MongoClient(mongo_uri)
db = mongo_client["online_gateway"]
collection = db["product-info"]

def embed(texts, input_type="search_document"):
    resp = co.embed(
        texts=texts,
        model="embed-english-light-v3.0",
        input_type=input_type
    )
    return resp.embeddings

index_name = "moglix-product-info"

existing_indexes = [index.name for index in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,     # depends on your embedding model
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",    # or gcp
            region="us-east-1"  # your preferred region
        )   
    )

index = pc.Index(index_name)    

batch_size = 500  # Adjust as needed for memory and API limits
batch_texts = []
batch_ids = []
batch_metadata = []
i = 0

def safe_embed(texts, input_type="search_document", max_retries=5, wait_seconds=60):
    for attempt in range(max_retries):
        try:
            return embed(texts, input_type)
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f"Rate limit hit. Waiting {wait_seconds} seconds before retrying (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_seconds)
            else:
                raise
    raise RuntimeError("Max retries exceeded for embedding API.")

cursor = collection.find({"chatBotEnabled": True})
for doc in cursor:
    try:
        product_bo = doc.get("productGroup", {}).get("productBO", {})
        name = product_bo.get("productName", "")
        description = product_bo.get("desciption", "")
        if name or description:
            text = f"{name} {description}".strip()
            batch_texts.append(text)
            batch_ids.append(f"doc-{i}")
            batch_metadata.append({"text": text})
            i += 1
        if len(batch_texts) == batch_size:
            print(f"Generating embeddings for batch {i // batch_size}")
            embeddings = safe_embed(batch_texts)
            to_upsert = list(zip(batch_ids, embeddings, batch_metadata))
            index.upsert(vectors=to_upsert)
            print(f"Upserted batch {i // batch_size} ({len(batch_texts)} vectors)")
            batch_texts, batch_ids, batch_metadata = [], [], []
    except Exception as e:
        print(f"Error processing document: {e}")
        continue

if batch_texts:
    print(f"Generating embeddings for final batch")
    embeddings = safe_embed(batch_texts)
    to_upsert = list(zip(batch_ids, embeddings, batch_metadata))
    index.upsert(vectors=to_upsert)
    print(f"Upserted final batch ({len(batch_texts)} vectors)")

# ...existing (commented) query code...


# query_text = "motor for irrigation in farm"
# query_vec = embed([query_text], input_type="search_query")[0]

# result = index.query(
#     vector=query_vec,
#     top_k=2,
#     include_metadata=True
# )

# #print("results:",result)

# for match in result.matches:
#     print(f"Score: {match.score:.3f} — Text: {match.metadata['text']}")


