import requests
import time
import uuid
import json

BASE_URL = "http://localhost:8000/api"

print("Waiting for backend to be ready...")
for _ in range(10):
    try:
        if requests.get("http://localhost:8000/health").status_code == 200:
            break
    except requests.exceptions.ConnectionError:
        time.sleep(1)

def test_api():
    session = requests.Session()
    results = {}
    
    # 1. Signup / Login / Session persistence
    email = f"test_{uuid.uuid4()}@example.com"
    try:
        res = session.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": "password", "name": "Audit User"})
        results["signup"] = res.status_code
        
        res = session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "password"})
        token = session.cookies.get("access_token")
        if not token and "access_token" in res.cookies:
            token = res.cookies.get("access_token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
            
        results["login"] = {"status": res.status_code, "token": bool(token)}
    except Exception as e:
        results["auth_error"] = str(e)
        
    # Check CORS
    try:
        cors = requests.options(f"{BASE_URL}/auth/login", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
        results["cors"] = cors.headers.get("Access-Control-Allow-Origin")
    except Exception as e:
        results["cors_error"] = str(e)

    # 2. Workspace and Brand
    ws_id = None
    brand_id = None
    try:
        res = session.post(f"{BASE_URL}/workspaces/", json={"name": "Audit Workspace", "domain": "audit.com"})
        results["workspace_create"] = res.status_code
        if res.status_code == 200:
            ws_id = res.json().get("id")
            res = session.post(f"{BASE_URL}/brands/", json={"name": "Audit Brand", "workspace_id": ws_id, "website_url": "https://example.com"}, headers={"X-Workspace-ID": ws_id})
            results["brand_create"] = {"status": res.status_code, "text": res.text}
            if res.status_code == 200:
                brand_id = res.json().get("id")
    except Exception as e:
        results["workspace_brand_error"] = str(e)

    headers = {}
    if ws_id and brand_id:
        headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
        
        # 3. Onboarding and website analysis
        try:
            res = session.post(f"{BASE_URL}/brands/{brand_id}/website-analysis", headers=headers)
            results["website_analysis"] = res.status_code
        except Exception as e:
            results["website_analysis_error"] = str(e)
            
        # 4. Brand Brain & Strategy
        try:
            res = session.get(f"{BASE_URL}/brand-brain/", headers=headers)
            results["brand_brain_get"] = res.status_code
        except Exception as e:
            results["brand_brain_error"] = str(e)

        # 5. AI CMO
        try:
            res = session.post(f"{BASE_URL}/ai/cmo/chat", json={"message": "Hello"}, headers=headers)
            results["ai_cmo"] = {"status": res.status_code, "response": res.text[:100]}
        except Exception as e:
            results["ai_cmo_error"] = str(e)

        # 6. Content Creation
        try:
            res = session.post(f"{BASE_URL}/content/projects", json={
                "brand_id": brand_id, "title": "Test Project", "content_type": "BLOG_POST", "status": "DRAFT"
            }, headers=headers)
            results["content_project"] = res.status_code
        except Exception as e:
            results["content_project_error"] = str(e)
            
        # 7. Notifications
        try:
            res = session.get(f"{BASE_URL}/notifications", headers=headers)
            results["notifications_get"] = res.status_code
        except Exception as e:
            results["notifications_error"] = str(e)
            
        # 8. Command Center (Performance/Analytics)
        try:
            res = session.get(f"{BASE_URL}/dashboard/command-center", headers=headers)
            results["command_center_get"] = res.status_code
        except Exception as e:
            pass

        # 9. Agents and Orchestrator
        try:
            res = session.get(f"{BASE_URL}/agents", headers=headers)
            results["agents_get"] = res.status_code
        except Exception as e:
            pass
            
        try:
            res = session.get(f"{BASE_URL}/opportunities", headers=headers)
            results["opportunities_get"] = res.status_code
        except Exception as e:
            pass
            
        try:
            res = session.get(f"{BASE_URL}/orchestrator/status", headers=headers)
            results["orchestrator_status_get"] = res.status_code
        except Exception as e:
            pass

    # Logout
    try:
        res = session.post(f"{BASE_URL}/auth/logout")
        results["logout"] = res.status_code
    except Exception as e:
        pass

    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(json.dumps(results, indent=2))

test_api()
