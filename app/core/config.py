# this is very similar to configuration settings in java
# we have create a class and uploaded the env varibale and ampped to a class

# BaseSetting automatcially reads from env variables and .env
from pydantic_settings import BaseSettings
from pathlib import Path

# Get the project root directory (where .env is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG Doc"
    
    # Azure Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = ""  # Optional for testing
    AZURE_STORAGE_CONTAINER_NAME: str = "raw-books"  # by default value is this
    AZURE_PROCESSED_BOOK_CONTAINER: str = "processed_books"

    class Config:
        env_file = str(ENV_FILE)  # Use absolute path to .env
        env_file_encoding = "utf-8"

# 	settings is a singleton-style object you can import anywhere:
settings = Settings() # initilize the class and load the settings
