import pytest
import os
from uuid import uuid4
from fastapi.testclient import TestClient
from tests.test_isolation_business_overview import setup_user_and_workspace

def test_document_upload_and_isolation():
    client, ws_id, brand_id, token = setup_user_and_workspace()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": str(ws_id),
        "X-Brand-Id": str(brand_id)
    }
    
    # 1. Test upload invalid file
    res = client.post(
        "/api/brand-brain/documents",
        headers=headers,
        files={"file": ("test.exe", b"fake exe data", "application/x-msdownload")}
    )
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]
    
    # 2. Test upload valid file (TXT)
    test_content = b"This is a test document content."
    res = client.post(
        "/api/brand-brain/documents",
        headers=headers,
        files={"file": ("test_doc.txt", test_content, "text/plain")},
        data={"category": "Marketing Strategy"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "test_doc.txt"
    assert data["category"] == "Marketing Strategy"
    assert data["processing_status"] in ["UPLOADED", "PROCESSING", "READY"]
    assert data["retrieval_status"] == "NOT_CONFIGURED"
    assert data["file_size"] == len(test_content)
    
    doc_id = data["id"]
    
    # 3. Test Get Documents
    res = client.get("/api/brand-brain/documents", headers=headers)
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) == 1
    assert docs[0]["id"] == doc_id
    
    # 4. Test Isolation
    fake_brand_id = uuid4()
    headers["X-Brand-Id"] = str(fake_brand_id)
    res = client.get("/api/brand-brain/documents", headers=headers)
    assert res.status_code in [403, 404]
    
    headers["X-Brand-Id"] = str(brand_id)
    
    # 5. Test Delete Document
    res = client.delete(f"/api/brand-brain/documents/{doc_id}", headers=headers)
    assert res.status_code == 200
    
    res = client.get("/api/brand-brain/documents", headers=headers)
    assert len(res.json()) == 0
