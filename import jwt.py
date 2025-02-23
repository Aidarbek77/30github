import jwt
import datetime
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()
SECRET_KEY = "your-256-bit-secret-keep-it-safe"

def create_token(user: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    payload = {
        "sub": user,
        "exp": expiration,
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validate_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def refresh_token(old_token: str):
    try:
        payload = jwt.decode(old_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        user = payload.get("sub")
        return create_token(user)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")