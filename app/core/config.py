# this is very similar to configuration settings in java
# we have create a class and uploaded the env varibale and ampped to a class

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG Doc"
    
    # Azure Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = ""  # Optional for testing
    AZURE_STORAGE_CONTAINER_NAME: str = "documents"  # by default value is this

    class Config:
        env_file = ".env"

settings = Settings() # initilize the class and load the settings
