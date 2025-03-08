import os
import jwt
import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    # Only for development, log a warning
    import logging
    logging.warning("JWT_SECRET not set! Using a random key for this session only.")
    SECRET_KEY = os.urandom(32).hex()
    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ISSUER = os.getenv("JWT_ISSUER", "your-app")
AUDIENCE = os.getenv("JWT_AUDIENCE", "your-audience")

app = FastAPI(title="Secure API", description="API with JWT Authentication")

# Models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class RefreshRequest(BaseModel):
    refresh_token: str

class MessageResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

# Custom JWTBearer class for token validation
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Invalid authentication scheme"
                )
            return credentials.credentials
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid authorization header"
        )

security = JWTBearer()

# JWT Functions
def create_access_token(user_id: str) -> str:
    """Create an access token with short expiration time"""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create a refresh token with longer expiration time"""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM], 
            audience=AUDIENCE, 
            issuer=ISSUER,
            options={"verify_exp": verify_exp}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid token: {str(e)}"
        )

def get_current_user(token: str = Depends(security)) -> str:
    """Dependency to get current authenticated user from access token"""
    payload = decode_token(token)
    
    # Verify this is an access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token type"
        )
        
    return payload.get("sub")

# Routes
@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """
    Authenticate user and generate access and refresh tokens
    
    In a real application, you would validate credentials against a database
    """
    # Simulate user authentication - replace with actual authentication
    # For example: if not authenticate_user(user_data.username, user_data.password):
    #    raise HTTPException(401, "Invalid credentials")
    
    # For demo purposes, we'll just use the username as the user ID
    user_id = user_data.username
    
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    """Generate new access token using a valid refresh token"""
    payload = decode_token(request.refresh_token)
    
    # Verify this is a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }

@app.get("/protected", response_model=MessageResponse)
async def protected_route(user_id: str = Depends(get_current_user)):
    """Protected endpoint requiring valid JWT token"""
    return {
        "message": "Access granted",
        "data": {"user_id": user_id}
    }

@app.get("/health")
async def health_check():
    """Public endpoint for health checks"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)