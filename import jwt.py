import os
import jwt
import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Secure Secret Key from Environment
SECRET_KEY = os.getenv("JWT_SECRET", os.urandom(32).hex())  
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 30
ISSUER = "your-app"
AUDIENCE = "your-audience"

app = FastAPI()

# Custom JWTBearer class for token validation
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme")
            return credentials.credentials
        raise HTTPException(status_code=403, detail="Invalid authorization header")

security = JWTBearer()

def create_token(user: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    payload = {
        "sub": user,
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
        "iss": ISSUER,
        "aud": AUDIENCE
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def validate_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER)
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def refresh_token(old_token: str):
    try:
        payload = jwt.decode(old_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        user = payload.get("sub")
        return create_token(user)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# FastAPI Routes
@app.post("/login")
async def login(user: str):
    return {"access_token": create_token(user)}

@app.get("/protected")
async def protected_route(user: str = Depends(validate_token)):
    return {"message": f"Hello, {user}. You have access!"}

@app.post("/refresh")
async def refresh_route(token: str):
    return {"access_token": refresh_token(token)}