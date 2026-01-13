"""Authentication service with bcrypt and JWT."""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.streak import UserStreak

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


class AuthService:
    """Authentication service for user management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def create_jwt_token(user_id: uuid.UUID) -> str:
        """Create a JWT token with 24-hour expiry."""
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt_token(token: str) -> Optional[uuid.UUID]:
        """Verify a JWT token and return the user_id."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return uuid.UUID(user_id)
        except JWTError:
            return None

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get a user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @classmethod
    async def register(
        cls, db: AsyncSession, email: str, password: str, name: str
    ) -> tuple[User, str]:
        """Register a new user and return user with JWT token."""
        # Check if email already exists
        existing = await cls.get_user_by_email(db, email)
        if existing:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            email=email,
            name=name,
            password_hash=cls.hash_password(password),
        )
        db.add(user)
        await db.flush()

        # Create initial streak record
        streak = UserStreak(
            user_id=user.id,
            current_streak=0,
            longest_streak=0,
            total_xp=0,
        )
        db.add(streak)
        await db.commit()
        await db.refresh(user)

        # Generate token
        token = cls.create_jwt_token(user.id)
        return user, token

    @classmethod
    async def login(
        cls, db: AsyncSession, email: str, password: str
    ) -> tuple[User, str]:
        """Login a user and return user with JWT token."""
        user = await cls.get_user_by_email(db, email)
        if not user:
            raise ValueError("Invalid email or password")

        if not cls.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        # Generate token
        token = cls.create_jwt_token(user.id)
        return user, token
