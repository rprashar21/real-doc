from fastapi import FastAPI
from app.api.v1.api import api_router  # <--- Import the router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Mount the router under "/api/v1"
app.include_router(api_router, prefix=settings.API_V1_STR)




