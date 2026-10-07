import time
import requests

def test_real_worker():
    base_url = "http://localhost:8000"
    
    # 1. Login
    res = requests.post(f"{base_url}/api/auth/login", json={"email": "demo@standbharat.com", "password": "password123"})
    if res.status_code != 200:
        print("Login failed")
        return
    token = res.cookies.get("access_token")
    headers = {"Cookie": f"access_token={token}"}
    
    # 2. Get Workspaces
    res = requests.get(f"{base_url}/api/workspaces/", headers=headers)
    ws_id = res.json()[0]["id"]
    headers["X-Workspace-ID"] = ws_id
    
    # 3. Get Brands
    res = requests.get(f"{base_url}/api/brands/?workspace_id={ws_id}", headers=headers)
    if res.status_code != 200 or not isinstance(res.json(), list) or len(res.json()) == 0:
        print("Failed to get brands", res.text)
        return
    brand_id = res.json()[0]["id"]
    headers["X-Brand-ID"] = brand_id
    
    print(f"Testing with workspace {ws_id} and brand {brand_id}")
    
    # 4. Trigger Analytics Agent
    print("Triggering Analytics Agent...")
    res = requests.post(f"{base_url}/api/agents/analytics/run", json={"input_data": {}}, headers=headers)
    if res.status_code != 200:
        print("Trigger failed", res.text)
        return
    run_id = res.json()["run_id"]
    print(f"Run ID: {run_id}")
    
    # 5. Poll for completion
    for _ in range(30):
        res = requests.get(f"{base_url}/api/agent-runs/{run_id}", headers=headers)
        if res.status_code == 200:
            data = res.json()
            status = data["status"]
            print(f"Status: {status}")
            if status in ["COMPLETED", "FAILED"]:
                print(f"Result data: {data['result_data']}")
                print(f"Error message: {data['error_message']}")
                break
        else:
            print("Failed to get status", res.text)
        time.sleep(2)
        
    print("Done")

if __name__ == "__main__":
    test_real_worker()
