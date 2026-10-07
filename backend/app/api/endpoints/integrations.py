from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

@router.get("/", response_model=List[Dict])
def list_integrations():
    return [
        {"id": "ga4", "provider": "Google Analytics", "status": "Not connected"},
        {"id": "github", "provider": "GitHub", "status": "Not connected"},
    ]
