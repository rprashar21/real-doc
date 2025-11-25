from fastapi import FastAPI
from app.api.v1.api import api_router  # <--- Import the router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Mount the router under "/api/v1"
app.include_router(api_router, prefix=settings.API_V1_STR)

list =["a","b","c","d","e","f"]

@app.get("/")
async def startup():
    print("Im at this line dow we need to do something")
    return {"hello": "world"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
