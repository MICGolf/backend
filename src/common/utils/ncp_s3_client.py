from common.utils.object_storage import ObjectStorageClient

_object_storage_client: ObjectStorageClient | None = None


def get_object_storage_client() -> ObjectStorageClient:
    global _object_storage_client
    if _object_storage_client is None:
        _object_storage_client = ObjectStorageClient()
    return _object_storage_client
