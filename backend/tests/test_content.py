import pytest
from tests.test_specialized_agents import setup_user_and_workspace

def test_content_lifecycle():
    client, ws_id, brand_id = setup_user_and_workspace()
    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    
    # 1. Create project
    res = client.post("/api/content/projects", json={"title": "Test Project"}, headers=headers)
    assert res.status_code == 200
    proj_id = res.json()["id"]
    
    # 2. Create brief
    res = client.post(f"/api/content/projects/{proj_id}/brief", json={"title": "Test Brief"}, headers=headers)
    assert res.status_code == 200
    brief_id = res.json()["id"]
    
    # 3. Generate draft (starts celery task)
    res = client.post(f"/api/content/projects/{proj_id}/generate", headers=headers)
    assert res.status_code == 200
    assert "task_id" in res.json()
