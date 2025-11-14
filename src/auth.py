"""User authentication and management using SQLAlchemy."""
from __future__ import annotations

import hashlib
from typing import Optional, Tuple

from src.database import User, db


def _hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if not username or not email or not password:
        return False, "All fields are required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    password_hash = _hash_password(password)
    
    try:
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username.strip()) | (User.email == email.strip().lower())
        ).first()
        
        if existing_user:
            return False, "Username or email already exists"
        
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
        )
        db.session.add(user)
        db.session.commit()
        return True, "Registration successful"
    except Exception as e:
        db.session.rollback()
        return False, f"Registration failed: {str(e)}"


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user. Returns user dict if successful, None otherwise."""
    password_hash = _hash_password(password)
    
    user = User.query.filter(
        (User.username == username.strip()) | (User.email == username.strip().lower())
    ).filter(User.password_hash == password_hash).first()
    
    if user:
        return user.to_dict()
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID."""
    user = User.query.get(user_id)
    if user:
        return user.to_dict()
    return None
