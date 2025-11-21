from fastapi import FastAPI

app = FastAPI(title="Rag-Doc")

@app.get("/")
def home():
    return {"Hello": "World"}
