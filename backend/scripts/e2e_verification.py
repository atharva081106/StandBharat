import os
import sys
import uuid
import time
import requests

BASE_URL = "http://localhost:8001"

def print_step(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

def assert_eq(actual, expected, msg, res=None):
    if actual != expected:
        print(f"FAILED: {msg} (Expected {expected}, got {actual})")
        if res: print(res.text)
        sys.exit(1)

def run_e2e():
    print_step("Starting E2E Verification")
    
    # RULE 4: REAL ONBOARDING E2E
    user1_email = f"acme_{uuid.uuid4()}@example.com"
    user1_password = "password123"
    
    # 1. Signup user 1
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": user1_email,
        "password": user1_password,
        "name": "Acme Admin"
    })
    assert_eq(res.status_code, 200, "Signup user 1")
    
    # 2. Login user 1
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": user1_email,
        "password": user1_password
    })
    assert_eq(res.status_code, 200, "Login user 1")
    token1 = res.cookies.get("access_token")
    headers1 = {"Cookie": f"access_token={token1}"}
    
    # 3. Create Workspace
    res = requests.post(f"{BASE_URL}/api/workspaces/", json={
        "name": "Acme Analytics"
    }, headers=headers1)
    assert_eq(res.status_code, 200, "Create Workspace 1")
    ws1_id = res.json()["id"]
    headers1["X-Workspace-ID"] = ws1_id
    
    # 4. Create Brand
    res = requests.post(f"{BASE_URL}/api/brands/", json={
        "name": "Acme Analytics",
        "workspace_id": ws1_id,
        "website_url": "https://example.com",
        "description": "Analytics platform for growing businesses"
    }, headers=headers1)
    assert_eq(res.status_code, 200, "Create Brand 1")
    br1_id = res.json()["id"]
    headers1["X-Brand-ID"] = br1_id
    
    # 5. Complete Onboarding
    res = requests.post(f"{BASE_URL}/api/onboarding/complete", json={
        "businessName": "Acme Analytics",
        "website": "https://example.com",
        "description": "Analytics platform for growing businesses",
        "valueProposition": "Make marketing attribution simple",
        "brandVoice": ["Clear", "analytical", "confident"],
        "targetDemographic": "Startup founders",
        "customerPainPoints": "Poor marketing attribution",
        "primaryObjective": "Increase qualified leads",
        "targetRevenue": "100000",
        "competitors": ["HubSpot", "Mixpanel"]
    }, headers=headers1)
    assert_eq(res.status_code, 200, "Complete Onboarding 1")
    
    # Verify DB state directly via API (Brand Brain)
    res = requests.get(f"{BASE_URL}/api/brand-brain/", headers=headers1)
    assert_eq(res.status_code, 200, "Get Brand Brain Context 1")
    data = res.json()
    assert_eq(data["brand"]["name"], "Acme Analytics", "Brand name")
    assert_eq(data["positioning"]["unique_value_proposition"], "Make marketing attribution simple", "Value prop")
    assert "Startup founders" in [a["name"] for a in data["audiences"]], "Audience"
    assert "HubSpot" in [c["name"] for c in data["competitors"]], "Competitor HubSpot"
    assert "Clear, analytical, confident" in data["voice"]["tone"], "Brand voice"
    
    # RULE 7: SECOND TENANT
    user2_email = f"nova_{uuid.uuid4()}@example.com"
    user2_password = "password123"
    
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={"email": user2_email, "password": user2_password, "name": "Nova Admin"})
    res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": user2_email, "password": user2_password})
    token2 = res.cookies.get("access_token")
    headers2 = {"Cookie": f"access_token={token2}"}
    
    res = requests.post(f"{BASE_URL}/api/workspaces/", json={"name": "Nova Commerce"}, headers=headers2)
    ws2_id = res.json()["id"]
    headers2["X-Workspace-ID"] = ws2_id
    
    res = requests.post(f"{BASE_URL}/api/brands/", json={
        "name": "Nova Commerce", "workspace_id": ws2_id, "website_url": "https://nova.com", "description": "Simple commerce growth"
    }, headers=headers2)
    br2_id = res.json()["id"]
    headers2["X-Brand-ID"] = br2_id
    
    res = requests.post(f"{BASE_URL}/api/onboarding/complete", json={
        "businessName": "Nova Commerce",
        "website": "https://nova.com",
        "description": "Simple commerce growth",
        "valueProposition": "Simple commerce growth",
        "brandVoice": ["Friendly", "practical"],
        "targetDemographic": "Online retailers",
        "customerPainPoints": "Complex commerce",
        "primaryObjective": "Increase online sales",
        "targetRevenue": "50000",
        "competitors": ["Shopify", "WooCommerce"]
    }, headers=headers2)
    
    res = requests.get(f"{BASE_URL}/api/brand-brain/", headers=headers2)
    data2 = res.json()
    assert_eq(data2["brand"]["name"], "Nova Commerce", "Tenant 2 Brand name")
    assert "Shopify" in [c["name"] for c in data2["competitors"]], "Tenant 2 Competitor Shopify"
    
    # RULE 8: HARD TENANT ISOLATION
    print_step("Testing Hard Tenant Isolation")
    # User 1 tries to access User 2's brand
    headers1_malicious = headers1.copy()
    headers1_malicious["X-Workspace-ID"] = ws2_id
    headers1_malicious["X-Brand-ID"] = br2_id
    res = requests.get(f"{BASE_URL}/api/brand-brain/", headers=headers1_malicious)
    if res.status_code == 200:
        print("FAILED: Cross-tenant access succeeded!")
        sys.exit(1)
        
    # Wait for Celery Bootstrap (Rule 9)
    print_step("Waiting for Celery Bootstrap to finish...")
    time.sleep(10) # Give celery time to process
    
    res = requests.get(f"{BASE_URL}/api/brand-brain/", headers=headers1)
    data1 = res.json()
    
    print_step("Verifying Idempotency (Rule 10)")
    res_post = requests.post(f"{BASE_URL}/api/onboarding/complete", json={
        "businessName": "Acme Analytics",
        "website": "https://example.com",
        "description": "Analytics platform for growing businesses",
        "valueProposition": "Make marketing attribution simple",
        "brandVoice": ["Clear", "analytical", "confident"],
        "targetDemographic": "Startup founders",
        "customerPainPoints": "Poor marketing attribution",
        "primaryObjective": "Increase qualified leads",
        "targetRevenue": "100000",
        "competitors": ["HubSpot", "Mixpanel"]
    }, headers=headers1)
    assert_eq(res_post.status_code, 200, "Idempotency Complete Onboarding", res_post)
    time.sleep(5)
    res_get = requests.get(f"{BASE_URL}/api/brand-brain/", headers=headers1)
    assert_eq(res_get.status_code, 200, "Idempotency Get Context", res_get)
    data1_post = res_get.json()
    assert_eq(len(data1["competitors"]), len(data1_post["competitors"]), "Idempotency on competitors")
    
    print_step("All checks passed.")
    print("SUCCESS")

if __name__ == "__main__":
    run_e2e()
