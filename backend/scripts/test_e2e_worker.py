"""
Real end-to-end worker execution test for Phase 11 unblock verification.
Tests: Analytics, Competitor, Growth agents + Orchestrator tick
"""
import requests
import time
import uuid
import sys

BASE_URL = "http://localhost:8000"

def setup():
    """Create user, workspace, brand and return authenticated session."""
    s = requests.Session()
    email = f"e2e_{uuid.uuid4()}@test.com"
    
    s.post(f"{BASE_URL}/api/auth/signup", json={"email": email, "password": "test1234", "name": "E2E Test"})
    login = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": "test1234"})
    assert login.status_code == 200, f"Login failed: {login.text}"
    
    ws = s.post(f"{BASE_URL}/api/workspaces/", json={"name": "E2E Workspace", "domain": f"e2e-{uuid.uuid4()}.com"})
    assert ws.status_code == 200, f"Workspace failed: {ws.text}"
    ws_id = ws.json()["id"]
    
    brand = s.post(f"{BASE_URL}/api/brands/", json={"name": "E2E Brand", "workspace_id": ws_id}, headers={"X-Workspace-ID": ws_id})
    assert brand.status_code == 200, f"Brand failed: {brand.text}"
    brand_id = brand.json()["id"]
    
    return s, ws_id, brand_id

def run_agent_and_verify(session, ws_id, brand_id, agent_type, timeout=30):
    """Trigger an agent and poll until it completes or times out."""
    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    
    print(f"\n--- Testing {agent_type} Agent ---")
    run_resp = session.post(
        f"{BASE_URL}/api/agents/{agent_type}/run",
        json={"input_data": {}},
        headers=headers
    )
    assert run_resp.status_code == 200, f"Run failed: {run_resp.text}"
    run_id = run_resp.json()["run_id"]
    print(f"  Queued run_id: {run_id}")

    # Poll until completion
    start = time.time()
    while time.time() - start < timeout:
        status_resp = session.get(f"{BASE_URL}/api/agent-runs/{run_id}", headers=headers)
        assert status_resp.status_code == 200, f"Status check failed: {status_resp.text}"
        status = status_resp.json()["status"]
        print(f"  Status: {status}")
        if status in ["COMPLETED", "SUCCESS", "FAILED", "ERROR"]:
            output = status_resp.json()
            print(f"  Final status: {status}")
            if status in ["COMPLETED", "SUCCESS"]:
                print(f"  Output keys: {list((output.get('result_data') or {}).keys())}")
            assert status in ["COMPLETED", "SUCCESS"], f"{agent_type} agent run FAILED: {output.get('error_message')}"
            return run_id
        time.sleep(2)
    
    raise TimeoutError(f"{agent_type} agent did not complete within {timeout}s")

def test_orchestrator_tick(session, ws_id, brand_id):
    """Test the orchestrator tick creates OrchestrationRun records."""
    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    
    print("\n--- Testing Orchestrator Tick ---")
    # Set to AUTONOMOUS
    update = session.patch(f"{BASE_URL}/api/orchestrator/status", json={"mode": "AUTONOMOUS"}, headers=headers)
    assert update.status_code == 200, f"Mode update failed: {update.text}"
    print(f"  Mode set to: {update.json()['mode']}")
    
    # Trigger tick
    tick = session.post(f"{BASE_URL}/api/orchestrator/tick", headers=headers)
    assert tick.status_code == 200, f"Tick failed: {tick.text}"
    print(f"  Tick triggered: {tick.json()}")
    
    # Check runs were logged
    runs_resp = session.get(f"{BASE_URL}/api/orchestrator/runs", headers=headers)
    assert runs_resp.status_code == 200
    runs = runs_resp.json()
    print(f"  OrchestrationRun records created: {len(runs)}")
    for r in runs:
        print(f"  Agent={r['agent_id']} Decision={r['decision']} Reason={r['reason'][:60]}")
    
    assert len(runs) > 0, "No orchestration runs were created"
    return runs

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 11 — REAL WORKER E2E VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    try:
        # Health check
        health = requests.get(f"{BASE_URL}/health")
        assert health.status_code == 200
        print(f"\n✓ FastAPI health: {health.json()}")
        
        # Setup
        session, ws_id, brand_id = setup()
        print(f"\n✓ Test workspace: {ws_id}")
        print(f"✓ Test brand:     {brand_id}")
        
        # Run Analytics
        run_agent_and_verify(session, ws_id, brand_id, "analytics", timeout=45)
        results["analytics"] = "PASS"
        print("✓ Analytics Agent: PASS")
        
        # Run Competitor
        run_agent_and_verify(session, ws_id, brand_id, "competitor", timeout=45)
        results["competitor"] = "PASS"
        print("✓ Competitor Agent: PASS")
        
        # Run Growth (now analytics + competitor have run so deps satisfied)
        run_agent_and_verify(session, ws_id, brand_id, "growth", timeout=45)
        results["growth"] = "PASS"
        print("✓ Growth Agent: PASS")
        
        # Orchestrator tick
        runs = test_orchestrator_tick(session, ws_id, brand_id)
        results["orchestrator_tick"] = "PASS"
        print("✓ Orchestrator Tick: PASS")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for k, v in results.items():
        print(f"  {k:30s}: {v}")
    print("=" * 60)
