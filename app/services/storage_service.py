# This handles the Azure SDK logic.

# connect to the blob storage and generate a unique sas url for the document and
# upload the document to storage account

from datetime import datetime, timedelta, timezone
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions
)
from app.core.config import settings
import uuid


class StorageService:
    """
    Storage Service Class
    We have initialize this class with storage connection string and container_name
    """

    def __init__(self):
        """
        similar to java
        BlobServiceClient blobServiceClient =
        new BlobServiceClientBuilder()
        .connectionString(connectionString)
        .buildClient();

        self.service_client is your main Azure Blob client.

        """
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError(
                "AZURE_STORAGE_CONNECTION_STRING is not set. "
                "Please set it in your .env file or environment variables."
            )
        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self.service_client = (BlobServiceClient.from_connection_string(connection_string))
        self.container_name = container_name

    """
    write a method to generate the sas url for say 15 mins -- we can decide on this 
    """

    def generate_sas_url(self, file_name: str, file_hash: str = None, expiry_minutes: int = 15) -> tuple[
        str, str, bool]:
        """
        Generate SAS URL for upload.
        If file_hash provided, use hash-based naming for idempotency.
        Returns: (blob_name, upload_url, is_existing)
        """
        # Use hash-based naming for idempotency if hash provided
        if file_hash:
            # Clean filename (remove path, keep extension)
            clean_filename = file_name.split('/')[-1]
            blob_name = f"{file_hash}_{clean_filename}"
        else:
            # Fallback to UUID-based naming if no hash
            blob_name = f"{str(uuid.uuid4())}_{file_name}"

        # Check if blob already exists (idempotency check)
        blob_client = self.service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        is_existing = blob_client.exists()

        if is_existing:
            # File exists - generate read SAS URL for verification
            sas_token = generate_blob_sas(
                account_name=self.service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),  # Read permission for existing file
                expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            )
        else:
            # File doesn't exist - generate write SAS URL
            sas_token = generate_blob_sas(
                account_name=self.service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.service_client.credential.account_key,
                permission=BlobSasPermissions(write=True),  # Write permission for new file
                expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            )

        # Construct full URL
        upload_url = f"https://{self.service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"

        return blob_name, upload_url, is_existing

    def verify_and_get_metadata(self, blob_name: str) -> dict:
        blob_service_client = self.service_client.get_blob_client(container=self.container_name, blob=blob_name)

        # check if the file exists
        if not blob_service_client.exists():
            return None

        properties = blob_service_client.get_blob_properties()

        return {
            "file_name": blob_name.split("_")[-1],  # if the file is uuid_somename it will split and get the last name
            "size_bytes": properties.size,
            "content_type": properties.content_settings.content_type,
            "last_modified": properties.last_modified,
            "path": blob_name
        }

    """
    write a method to Download a blob and return its content as bytes.
    """

    def download_blob(self, blob_name: str) -> bytes:
        downloader = self.service_client.get_blob_client(container=self.container_name, blob=blob_name).download_blob()
        return downloader.readall()

    """
    write a method to upload json in another container this will be the represntation of the book its like the metadata about the book
    ie user uploads a book or a note in one conatier -- we download the notes and make soe information and reupload in another container
    
    """

    def upload_json(self, container_name: str, blob_name: str, data: dict) -> None:
        import json

        container_client = self.service_client.get_container_client(container=container_name)
        # upload_blob requires 'name' as first positional arg, then 'data'
        container_client.upload_blob(name=blob_name, data=json.dumps(data), overwrite=True)
