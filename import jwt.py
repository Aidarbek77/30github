import jwt
import datetime
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()
secret = "your-256-bit-secret-keep-it-safe"

def create_token(user: str):
    return jwt.encode({
        "sub": user,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "iat": datetime.datetime.utcnow()
    }, secret, algorithm="HS256")

def validate_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, secret, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def refresh_token(old_token: str):
    try:
        jwt.decode(old_token, secret, algorithms=["HS256"], options={"verify_exp": False})
        return create_token(jwt.decode(old_token, secret, algorithms=["HS256"], options={"verify_exp": False})["sub"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")