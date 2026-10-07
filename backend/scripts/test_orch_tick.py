import requests, uuid, time, sys

BASE = "http://localhost:8000"
s = requests.Session()
email = f"orch_{uuid.uuid4()}@test.com"
s.post(f"{BASE}/api/auth/signup", json={"email": email, "password": "test1234", "name": "Orch Test"})
s.post(f"{BASE}/api/auth/login", json={"email": email, "password": "test1234"})
ws = s.post(f"{BASE}/api/workspaces/", json={"name": "Orch WS", "domain": f"orch-{uuid.uuid4()}.com"})
ws_id = ws.json()["id"]
brand = s.post(f"{BASE}/api/brands/", json={"name": "Orch Brand", "workspace_id": ws_id}, headers={"X-Workspace-ID": ws_id})
brand_id = brand.json()["id"]
headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}

print(f"Workspace: {ws_id}")
print(f"Brand:     {brand_id}")

# Set AUTONOMOUS
r = s.patch(f"{BASE}/api/orchestrator/status", json={"mode": "AUTONOMOUS"}, headers=headers)
mode = r.json()["mode"]
print(f"Mode set: {mode}")
assert mode == "AUTONOMOUS"

# Trigger tick
tick = s.post(f"{BASE}/api/orchestrator/tick", headers=headers)
tick_result = tick.json()
print(f"Tick result: {tick_result}")
assert tick_result.get("status") == "success"

time.sleep(2)

# Check orchestration run audit records
runs = s.get(f"{BASE}/api/orchestrator/runs", headers=headers).json()
print(f"OrchestrationRun records created: {len(runs)}")
for run in runs:
    print(f"  agent={run['agent_id']} decision={run['decision']} reason={run['reason'][:70]}")

assert len(runs) >= 3, f"Expected at least 3 orchestration runs, got {len(runs)}"
print("\nOrchestrator tick: PASS")
