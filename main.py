from fastapi import FastAPI,HTTPException;
from pydantic import BaseModel;
from typing import List;

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None



app = FastAPI()

items = []


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


