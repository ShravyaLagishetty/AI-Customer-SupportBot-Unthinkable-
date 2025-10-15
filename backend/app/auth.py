from fastapi import Header, HTTPException
import os

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "admin-secret-key")

def require_admin(x_api_key: str | None = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing admin API key")
    return True
