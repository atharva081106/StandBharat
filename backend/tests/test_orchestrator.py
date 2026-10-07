import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from app.models.all_models import OrchestratorConfig, OrchestrationRun

from tests.test_specialized_agents import setup_user_and_workspace
from app.db.session import SessionLocal

def test_orchestrator_status_and_update():
    client, ws_id, brand_id = setup_user_and_workspace()
    db_session = SessionLocal()
    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    
    # 1. Get status (should default to OFF)
    res = client.get("/api/orchestrator/status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "OFF"
    
    # 2. Update to AUTONOMOUS
    res = client.patch("/api/orchestrator/status", json={"mode": "AUTONOMOUS"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["mode"] == "AUTONOMOUS"
    
    # 3. Check DB
    config = db_session.query(OrchestratorConfig).filter(OrchestratorConfig.brand_id == brand_id).first()
    assert config.mode == "AUTONOMOUS"

def test_orchestrator_tick():
    client, ws_id, brand_id = setup_user_and_workspace()
    db_session = SessionLocal()
    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    
    # Ensure AUTONOMOUS mode
    client.patch("/api/orchestrator/status", json={"mode": "AUTONOMOUS"}, headers=headers)
    
    # 1. Manual tick
    res = client.post("/api/orchestrator/tick", headers=headers)
    assert res.status_code == 200
    
    # 2. Check orchestrator runs
    res = client.get("/api/orchestrator/runs", headers=headers)
    assert res.status_code == 200
    runs = res.json()
    assert len(runs) > 0
    # Should have tried to schedule analytics, competitor, growth
    
def test_orchestrator_assisted_mode():
    client, ws_id, brand_id = setup_user_and_workspace()
    db_session = SessionLocal()
    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    
    client.patch("/api/orchestrator/status", json={"mode": "ASSISTED"}, headers=headers)
    client.post("/api/orchestrator/tick", headers=headers)
    
    res = client.get("/api/orchestrator/runs", headers=headers)
    assert res.status_code == 200
    
    # In ASSISTED, it should decide to SKIP but give a reason that it was blocked by ASSISTED mode
    found_assisted_skip = False
    for r in res.json():
        if "Blocked by ASSISTED mode" in r["reason"]:
            found_assisted_skip = True
            break
            
    assert found_assisted_skip, "Expected at least one ASSISTED mode skip"
