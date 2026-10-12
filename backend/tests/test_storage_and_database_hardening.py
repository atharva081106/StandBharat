import io
import os
import tempfile
import uuid
from uuid import uuid4
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.publishing.models import PublicationAttempt
from app.models.all_models import BrandDocument
from app.services.storage import (
    LocalStorageService,
    S3StorageService,
    UploadSizeLimitExceededError,
    InvalidFileTypeError,
    StorageFileNotFoundError,
    StorageError,
    get_storage_service,
)
from app.services.document_processor import process_document, extract_text_from_bytes
from tests.test_isolation_business_overview import setup_user_and_workspace

def test_local_storage_crud_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorageService(base_root=tmpdir)
        ws_id = uuid4()
        brand_id = uuid4()
        
        # 1. Generate Key
        key, filename = storage.generate_key(ws_id, brand_id, "my_strategy_doc.txt")
        assert f"workspaces/{ws_id}/brands/{brand_id}/documents/" in key
        assert filename.startswith("my_strategy_doc_")
        assert filename.endswith(".txt")
        
        # 2. Upload file
        content = b"Strategic analysis for Q4 StandBharat release."
        stream = io.BytesIO(content)
        bytes_written = storage.upload_file(key, stream, max_size_bytes=1024 * 1024)
        assert bytes_written == len(content)
        assert storage.exists(key) is True
        
        # 3. Read file
        read_content = storage.read_file(key)
        assert read_content == content
        
        # 4. Delete file
        deleted = storage.delete_file(key)
        assert deleted is True
        assert storage.exists(key) is False
        
        # 5. Read deleted raises StorageFileNotFoundError
        with pytest.raises(StorageFileNotFoundError):
            storage.read_file(key)

def test_local_storage_size_limit_and_cleanup():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorageService(base_root=tmpdir)
        key = "workspaces/test/brands/test/documents/oversized.txt"
        
        # Limit to 50 bytes, upload 100 bytes
        oversized_data = b"A" * 100
        stream = io.BytesIO(oversized_data)
        
        with pytest.raises(UploadSizeLimitExceededError):
            storage.upload_file(key, stream, max_size_bytes=50)
            
        # Ensure target file was NOT created and no temporary file left behind
        assert storage.exists(key) is False
        files_in_dir = os.listdir(tmpdir)
        assert len(files_in_dir) == 1 # only 'workspaces' parent folder
        resolved_parent = os.path.dirname(storage._resolve_path(key))
        if os.path.exists(resolved_parent):
            assert len(os.listdir(resolved_parent)) == 0

def test_storage_path_traversal_prevention():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorageService(base_root=tmpdir)
        
        # 1. Traversal in key generation is sanitized
        ws_id = uuid4()
        brand_id = uuid4()
        key, filename = storage.generate_key(ws_id, brand_id, "../../etc/passwd.txt")
        assert ".." not in filename
        assert key.startswith(f"workspaces/{ws_id}/brands/{brand_id}/documents/")
        
        # 2. Direct path traversal in resolve_path is blocked
        with pytest.raises(StorageError, match="Path traversal"):
            storage._resolve_path("../../../outside.txt")

def test_storage_invalid_file_types():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorageService(base_root=tmpdir)
        ws_id = uuid4()
        brand_id = uuid4()
        
        for bad_file in ["malware.exe", "script.sh", "code.py", "payload.bin", "index.html"]:
            with pytest.raises(InvalidFileTypeError):
                storage.generate_key(ws_id, brand_id, bad_file)

def test_s3_storage_mocked_operations():
    """Validates S3StorageService operations using a mock S3 client."""
    mock_boto = MagicMock()
    mock_body = MagicMock()
    mock_body.read.return_value = b"S3 document data content"
    mock_boto.get_object.return_value = {"Body": mock_body}
    mock_boto.head_object.return_value = {"ContentLength": 24}
    
    s3_storage = S3StorageService(
        bucket_name="standbharat-prod-bucket",
        endpoint_url="https://s3.us-east-1.amazonaws.com",
        region_name="us-east-1",
        access_key_id="TESTKEY",
        secret_access_key="TESTSECRET",
        client=mock_boto
    )
    
    key = "workspaces/w1/brands/b1/documents/doc_1.pdf"
    
    # 1. Upload
    content = b"PDF data stream for S3 test"
    stream = io.BytesIO(content)
    bytes_written = s3_storage.upload_file(key, stream, max_size_bytes=1024 * 1024)
    assert bytes_written == len(content)
    mock_boto.put_object.assert_called_once_with(
        Bucket="standbharat-prod-bucket",
        Key=key,
        Body=content
    )
    
    # 2. Read
    read_data = s3_storage.read_file(key)
    assert read_data == b"S3 document data content"
    mock_boto.get_object.assert_called_once_with(
        Bucket="standbharat-prod-bucket",
        Key=key
    )
    
    # 3. Exists
    assert s3_storage.exists(key) is True
    
    # 4. Delete
    assert s3_storage.delete_file(key) is True
    mock_boto.delete_object.assert_called_once_with(
        Bucket="standbharat-prod-bucket",
        Key=key
    )

def test_api_upload_document_size_limit_413():
    client, ws_id, brand_id, token = setup_user_and_workspace()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": str(ws_id),
        "X-Brand-Id": str(brand_id)
    }
    
    # Patch max size to 500 bytes for testing
    with patch.object(settings, "STORAGE_MAX_UPLOAD_SIZE_BYTES", 500):
        oversized_content = b"Z" * 1000
        res = client.post(
            "/api/brand-brain/documents",
            headers=headers,
            files={"file": ("large_doc.txt", oversized_content, "text/plain")},
            data={"category": "Oversized"}
        )
        assert res.status_code == 413
        assert "maximum allowed upload size" in res.json()["detail"].lower()

def test_api_upload_and_worker_processing_e2e():
    client, ws_id, brand_id, token = setup_user_and_workspace()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": str(ws_id),
        "X-Brand-Id": str(brand_id)
    }
    
    text_content = b"Mission: StandBharat accelerates brand growth with unified AI intelligence."
    res = client.post(
        "/api/brand-brain/documents",
        headers=headers,
        files={"file": ("mission.txt", text_content, "text/plain")},
        data={"category": "Brand Identity"}
    )
    assert res.status_code == 200
    doc_data = res.json()
    doc_id = doc_data["id"]
    
    # Ensure file_path is an abstract storage key, not a local absolute host path
    storage_key = doc_data["file_path"]
    assert storage_key.startswith(f"workspaces/{ws_id}/brands/{brand_id}/documents/")
    assert ":" not in storage_key # No drive letter
    
    # Run worker processing on document
    db = SessionLocal()
    try:
        process_document(db, str(doc_id))
        
        # Verify processed state in DB
        processed_doc = db.query(BrandDocument).filter(BrandDocument.id == doc_id).first()
        assert processed_doc is not None
        assert processed_doc.processing_status == "READY"
        assert "StandBharat accelerates brand growth" in processed_doc.extracted_text
        assert processed_doc.metadata_json.get("word_count", 0) > 0
    finally:
        db.close()
    
    # Cleanup via API
    del_res = client.delete(f"/api/brand-brain/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 200

def test_database_connection_pool_configuration():
    """Validates that SQLAlchemy engine is configured with pool_pre_ping and pooling parameters."""
    assert engine.pool is not None
    # Verify pool_pre_ping
    assert getattr(engine.pool, "_pre_ping", False) is True
    # Verify pool recycle is configured to 1800s (or positive integer)
    assert engine.pool._recycle == settings.DB_POOL_RECYCLE
    assert settings.DB_POOL_RECYCLE == 1800
    assert settings.DB_POOL_SIZE == 10
    assert settings.DB_MAX_OVERFLOW == 10

def test_database_publication_attempts_index_metadata():
    """Validates that PublicationAttempt.publication_id column is indexed."""
    col = PublicationAttempt.__table__.c.publication_id
    assert col.index is True or any(
        col.name in idx.columns.keys() for idx in PublicationAttempt.__table__.indexes
    )
