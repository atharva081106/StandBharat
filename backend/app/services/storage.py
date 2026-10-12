import os
import io
import uuid
import re
from abc import ABC, abstractmethod
from typing import BinaryIO, Tuple, Union, Optional
from uuid import UUID

from app.core.config import settings

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.csv'}
CHUNK_SIZE = 64 * 1024 # 64 KB streaming buffer

class StorageError(Exception):
    """Base storage exception."""
    pass

class UploadSizeLimitExceededError(StorageError):
    """Raised when an upload exceeds the configured size limit."""
    pass

class InvalidFileTypeError(StorageError):
    """Raised when an uploaded file extension is not permitted."""
    pass

class StorageFileNotFoundError(StorageError):
    """Raised when a requested file or object does not exist."""
    pass

class StorageNotConfiguredError(StorageError):
    """Raised when the configured storage backend is not properly configured."""
    pass


class BaseStorageService(ABC):
    """Abstract storage interface for persistent document storage."""

    @abstractmethod
    def upload_file(self, key: str, file_obj: BinaryIO, max_size_bytes: int) -> int:
        """
        Uploads a binary stream to storage under the given key while enforcing max_size_bytes.
        Returns the total number of bytes written.
        """
        pass

    @abstractmethod
    def read_file(self, key: str) -> bytes:
        """Reads and returns the complete binary content for the given key."""
        pass

    @abstractmethod
    def delete_file(self, key: str) -> bool:
        """Deletes the file under the given key. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Checks if a file exists under the given key."""
        pass

    def generate_key(
        self,
        workspace_id: Union[str, UUID],
        brand_id: Union[str, UUID],
        original_filename: str
    ) -> Tuple[str, str]:
        """
        Generates a secure, path-traversal-free storage key and sanitized filename.
        Returns: (storage_key, safe_filename)
        """
        # Strip directory components to prevent traversal
        basename = os.path.basename(original_filename or "unnamed_document")
        ext = os.path.splitext(basename)[1].lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(
                f"Unsupported file format: extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
            
        # Clean the base name (remove non-alphanumeric except hyphen, underscore, dot)
        name_part = os.path.splitext(basename)[0]
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name_part)[:80]
        if not clean_name:
            clean_name = "document"
            
        doc_uuid = uuid.uuid4()
        safe_filename = f"{clean_name}_{doc_uuid.hex[:8]}{ext}"
        
        # Scope strictly to workspace and brand
        storage_key = f"workspaces/{str(workspace_id)}/brands/{str(brand_id)}/documents/{safe_filename}"
        return storage_key, safe_filename


class LocalStorageService(BaseStorageService):
    """Local filesystem storage implementation for development and single-instance deployments."""

    def __init__(self, base_root: Optional[str] = None):
        self.base_root = os.path.abspath(base_root or settings.STORAGE_LOCAL_ROOT)
        os.makedirs(self.base_root, exist_ok=True)

    def _resolve_path(self, key: str) -> str:
        # Normalize and prevent directory traversal
        # Clean leading slashes
        clean_key = key.lstrip("/\\")
        target_path = os.path.abspath(os.path.join(self.base_root, clean_key))
        if not target_path.startswith(self.base_root):
            raise StorageError(f"Path traversal detected: {key}")
        return target_path

    def upload_file(self, key: str, file_obj: BinaryIO, max_size_bytes: int) -> int:
        target_path = self._resolve_path(key)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        temp_path = f"{target_path}.tmp_{uuid.uuid4().hex}"
        bytes_written = 0

        try:
            with open(temp_path, "wb") as buffer:
                while True:
                    chunk = file_obj.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    chunk_len = len(chunk)
                    if bytes_written + chunk_len > max_size_bytes:
                        raise UploadSizeLimitExceededError(
                            f"File upload exceeds the maximum allowed size limit of {max_size_bytes} bytes."
                        )
                    buffer.write(chunk)
                    bytes_written += chunk_len
                    
            # Atomic rename on completion
            os.replace(temp_path, target_path)
            return bytes_written
        except Exception:
            # Clean up partial temporary file on failure
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def read_file(self, key: str) -> bytes:
        target_path = self._resolve_path(key)
        if not os.path.exists(target_path):
            raise StorageFileNotFoundError(f"File not found in storage: {key}")
        with open(target_path, "rb") as f:
            return f.read()

    def delete_file(self, key: str) -> bool:
        target_path = self._resolve_path(key)
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
                return True
            except OSError as e:
                raise StorageError(f"Failed to delete file {key}: {str(e)}")
        return False

    def exists(self, key: str) -> bool:
        target_path = self._resolve_path(key)
        return os.path.exists(target_path)


class S3StorageService(BaseStorageService):
    """S3-compatible object storage implementation (AWS S3, MinIO, Wasabi, Cloudflare R2)."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        client: Optional[object] = None,
    ):
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.region_name = region_name or settings.S3_REGION_NAME
        self.access_key_id = access_key_id or settings.S3_ACCESS_KEY_ID
        self.secret_access_key = secret_access_key or settings.S3_SECRET_ACCESS_KEY
        self._client = client

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.bucket_name:
            raise StorageNotConfiguredError("S3_BUCKET_NAME is not configured.")
        try:
            import boto3
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
            )
            return self._client
        except ImportError:
            raise StorageNotConfiguredError(
                "boto3 package is required for S3 object storage but is not installed."
            )

    def upload_file(self, key: str, file_obj: BinaryIO, max_size_bytes: int) -> int:
        client = self._get_client()
        clean_key = key.lstrip("/\\")

        # Stream into a bounded buffer to verify size without holding unlimited bytes
        bytes_written = 0
        buffer = io.BytesIO()

        while True:
            chunk = file_obj.read(CHUNK_SIZE)
            if not chunk:
                break
            chunk_len = len(chunk)
            if bytes_written + chunk_len > max_size_bytes:
                raise UploadSizeLimitExceededError(
                    f"File upload exceeds the maximum allowed size limit of {max_size_bytes} bytes."
                )
            buffer.write(chunk)
            bytes_written += chunk_len

        buffer.seek(0)
        try:
            client.put_object(
                Bucket=self.bucket_name,
                Key=clean_key,
                Body=buffer.getvalue(),
            )
            return bytes_written
        except Exception as e:
            raise StorageError(f"Failed to upload object to S3: {str(e)}")

    def read_file(self, key: str) -> bytes:
        client = self._get_client()
        clean_key = key.lstrip("/\\")
        try:
            response = client.get_object(Bucket=self.bucket_name, Key=clean_key)
            return response["Body"].read()
        except Exception as e:
            error_str = str(e)
            if "NoSuchKey" in error_str or "404" in error_str:
                raise StorageFileNotFoundError(f"Object not found in S3: {key}")
            raise StorageError(f"Failed to read object from S3: {error_str}")

    def delete_file(self, key: str) -> bool:
        client = self._get_client()
        clean_key = key.lstrip("/\\")
        try:
            client.delete_object(Bucket=self.bucket_name, Key=clean_key)
            return True
        except Exception as e:
            raise StorageError(f"Failed to delete object from S3: {str(e)}")

    def exists(self, key: str) -> bool:
        client = self._get_client()
        clean_key = key.lstrip("/\\")
        try:
            client.head_object(Bucket=self.bucket_name, Key=clean_key)
            return True
        except Exception:
            return False


_storage_instance: Optional[BaseStorageService] = None

def get_storage_service() -> BaseStorageService:
    """Returns the configured storage service instance."""
    global _storage_instance
    if _storage_instance is None:
        backend_type = settings.STORAGE_BACKEND.lower()
        if backend_type == "s3":
            _storage_instance = S3StorageService()
        else:
            _storage_instance = LocalStorageService()
    return _storage_instance
