from fastapi import APIRouter
from app.api.v1.endpoints import upload, process  # this imports a moudule named upload which contains all the endpoints

api_router = APIRouter()
# It takes the routes defined in upload.router and mounts them under:  tags=["uploads] These tags appear in Swagger UI. # This is for documentation only.
api_router.include_router(upload.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(process.router, prefix="/process", tags=["processing"])
