import os, time
from fastapi import Header, HTTPException
import jwt

ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', 'admin-secret-key')
JWT_SECRET = os.environ.get('JWT_SECRET', 'change_this_secret')
JWT_ALG = 'HS256'
JWT_EXP_S = 60*60*24  # 1 day

def create_jwt(payload: dict):
    data = payload.copy()
    data['exp'] = int(time.time()) + JWT_EXP_S
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALG)
    return token

def require_admin_either(x_api_key: str | None = Header(None), authorization: str | None = Header(None)):
    # If x-api-key matches ADMIN_API_KEY, allow
    if x_api_key and x_api_key == ADMIN_API_KEY:
        return True
    # Otherwise check Bearer token
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ',1)[1]
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
            # optional: check role
            if data.get('role') == 'admin':
                return True
        except Exception as e:
            raise HTTPException(status_code=401, detail='invalid token: ' + str(e))
    raise HTTPException(status_code=401, detail='missing or invalid credentials')
