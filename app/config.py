from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    azure_storage_connection_string: str = "UseDevelopmentStorage=true"
    blob_container: str = "documents"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    demo_username: str
    demo_password: str
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()
