from azure.storage.blob import BlobServiceClient
from app.config import get_settings


def _container():
    settings = get_settings()
    service = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
    container = service.get_container_client(settings.blob_container)
    if not container.exists():
        container.create_container()
    return container

def save_pdf(name: str, data: bytes) -> None:
    _container().upload_blob(name, data, overwrite = True)

def list_pdfs() -> list[dict]:
    return [
        {"name": b.name, "size_bytes": b.size, "uploaded_at": b.last_modified}
        for b in _container().list_blobs()
    ]

def read_pdf(name: str) -> bytes:
    return _container().download_blob(name).readall()

