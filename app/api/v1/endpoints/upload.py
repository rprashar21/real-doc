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
async def upload(filename: str, file_hash: str = None) -> UploadInitResponse:
    """
    Generate SAS URL for upload.
    If file_hash provided, uses hash-based naming for idempotency.
    """
    storage_service = get_storage_service()
    """ this will generate a sas url and upload the file in blob storage """
    blob_name, upload_url, is_existing = storage_service.generate_sas_url(
        filename, 
        file_hash=file_hash
    )

    return UploadInitResponse(
        blob_name=blob_name, 
        blob_url=upload_url, 
        expire_minutes=15,
        is_existing=is_existing
    )


# check if the upload is complete
@router.post("/complete", response_model=FileMetadata)
async def complete_upload(upload_request: UploadCompleteRequest):
    storage_service = get_storage_service()
    metadata = storage_service.verify_and_get_metadata(upload_request.blob_name)

    if metadata is None:
        raise HTTPException(status_code=400, detail="Blob name not found")

    return FileMetadata(**metadata)
