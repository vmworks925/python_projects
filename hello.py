import os
import requests
import cohere
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="pcsk_3ErmbN_Nw1raDwAD1ycbPq6RXBgrw8Xdnys4JKxce1AMVJYVcHce7fLe5M7iYbp8GTHDZj")
co = cohere.Client("Cj1OpLxjMTqbWew5VvgAPxMyk80OeZuLj5LCXoAG")

def embed(texts, input_type="search_document"):
    resp = co.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type=input_type
    )
    return resp.embeddings

index_name = "products"

existing_indexes = [index.name for index in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=1024,     # depends on your embedding model
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",    # or gcp
            region="us-east-1"  # your preferred region
        )   
    )

index = pc.Index(index_name)    

texts = [
     "Lenovo IdeaPad S540-14IWL Mineral Grey Laptop with Intel Core i7-8565U/12GB/1TB SSD/Win 10 Home 64Bits & 14 inch FHD IPS Display, 81ND006UAX",
    "Lenovo Legion 5 Black Laptop with 10th Gen Intel Core i7-10750H/16GB/256GB SSD & 1TB HDD/Win 10 Home & 15.6 inch Full HD IPS Display, 81Y6009NAX-RBG",
    "Ador Welding Welding holder ador welding Welding & Soldering Welding Accessories Electrode Holders",
    "Khaitan COOLER MOTOR - DESERTcooler motor",
    "Motors Water Pumps Shallow Well Pumps for irrigation in farm"
]
embeddings = embed(texts)


ids = [f"doc-{i}" for i in range(len(texts))]

# upsert
to_upsert = list(zip(ids, embeddings, [{"text": t} for t in texts]))

index.upsert(vectors=to_upsert)


query_text = "motor for irrigation in farm"
query_vec = embed([query_text], input_type="search_query")[0]

result = index.query(
    vector=query_vec,
    top_k=2,
    include_metadata=True
)

#print("results:",result)

for match in result.matches:
    print(f"Score: {match.score:.3f} — Text: {match.metadata['text']}")


