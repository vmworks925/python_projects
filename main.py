from fastapi import FastAPI,HTTPException;
from pydantic import BaseModel;
from typing import List;
from embedding_search import EmbeddingSearchService;

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

app = FastAPI()
items = []

# Initialize the embedding search service (replace with your keys/index)
embedding_service = EmbeddingSearchService(
    cohere_api_key="Cj1OpLxjMTqbWew5VvgAPxMyk80OeZuLj5LCXoAG",
    pinecone_api_key="pcsk_3ErmbN_Nw1raDwAD1ycbPq6RXBgrw8Xdnys4JKxce1AMVJYVcHce7fLe5M7iYbp8GTHDZj",
    index_name="moglix-product-info"
)



@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/items",response_model=List[Item])
def get_items():
    return items

@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.post("/search")
def search_items(request: QueryRequest):
    try:
        results = embedding_service.search(request.query, top_k=request.top_k)
        return {"matches": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

