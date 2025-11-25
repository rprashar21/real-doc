# ui to backend to basically upload the file

from fastapi import APIRouter, HTTPException
from app.schemas.upload_dtos import UploadInitResponse, UploadCompleteRequest, FileMetadata
from app.services.storage_service import StorageService

# initialize the router
router = APIRouter()

# Lazy initialization - only create service when endpoints are called
def get_storage_service() -> StorageService:
    return StorageService()


@router.post("/init", response_model=UploadInitResponse)
async def init_upload(filename: str) -> UploadInitResponse:
    storage_service = get_storage_service()
    """ this will generate a sas url and upload the file in blob storage """
    blob_name, upload_url = storage_service.generate_sas_url(filename)

    return UploadInitResponse(blob_name=blob_name, blob_url=upload_url, expire_minutes=15)


# check if the upload is complete
@router.post("/complete", response_model=FileMetadata)
async def complete_upload(upload_request: UploadCompleteRequest):
    storage_service = get_storage_service()
    metadata = storage_service.verify_and_get_metadata(upload_request.blob_name)

    if metadata is None:
        raise HTTPException(status_code=400, detail="Blob name not found")

    return FileMetadata(**metadata)
