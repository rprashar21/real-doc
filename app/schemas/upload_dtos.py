# this will be mostly the dto classes

from pydantic import BaseModel
from datetime import datetime


# Upload response class
class UploadInitResponse(BaseModel):
    blob_name: str
    blob_url: str
    expire_minutes: int


# Request for /complete
class UploadCompleteRequest(BaseModel):
    blob_name: str


# Response for /complete
class FileMetadata(BaseModel):
    file_name: str
    size_bytes: int
    content_type: str
    last_modified: datetime
    path: str
