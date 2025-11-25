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

    It connects using the connection string.

You store the container name.

        """
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError(
                "AZURE_STORAGE_CONNECTION_STRING is not set. "
                "Please set it in your .env file or environment variables."
            )
        self.service_client = (BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING))
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME

    """
    write a method to generate the sas url for say 15 mins -- we can decide on this 
    """

    def generate_sas_url(self, file_name: str, expiry_minutes: int = 15) -> tuple[str, str]:
        blob_name = f"{str(uuid.uuid4())}_{file_name}"
        sas_token = generate_blob_sas(
            account_name=self.service_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.service_client.credential.account_key,
            permission=BlobSasPermissions(write=True),  # Only allow writing
            expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        )

        # # Construct full URL
        upload_url = f"https://{self.service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"

        return blob_name, upload_url

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
