"""Authentication API endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPAuthorizationCredentials as OptionalHTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.config import get_db
from services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


# Request/Response models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Extract and validate user from JWT token."""
    token = credentials.credentials
    user_id = AuthService.verify_jwt_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Optional dependency for getting current user (returns None if not authenticated)
async def get_optional_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Extract and validate user from JWT token, return None if not authenticated."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        
        user_id = AuthService.verify_jwt_token(token)
        if user_id is None:
            return None
        
        user = await AuthService.get_user_by_id(db, user_id)
        return user
    except Exception:
        # Swallow any parsing errors and treat as anonymous
        return None


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    try:
        user, token = await AuthService.register(
            db, request.email, request.password, request.name
        )
        return AuthResponse(
            token=token,
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login an existing user."""
    try:
        user, token = await AuthService.login(db, request.email, request.password)
        return AuthResponse(
            token=token,
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
    )
