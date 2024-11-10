from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
import requests

app = FastAPI()

class Prompt(BaseModel):
    prompt: str
    n_predict: int

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/llama")
def ask_llama(prompt: Prompt):
    response = requests.post(
            "http://llamacpp-server:8080/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt.prompt, "n_predict": prompt.n_predict}
        )
    return response.json()