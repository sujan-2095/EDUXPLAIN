"""Database configuration and models using SQLAlchemy."""
from __future__ import annotations

import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app: Flask) -> None:
    """Initialize database connection for Flask app."""
    # Get database URL from environment variable (Render PostgreSQL)
    # Falls back to SQLite for local development
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Render provides postgresql:// which is correct for SQLAlchemy
        # Some providers use postgres://, convert to postgresql://
        if database_url.startswith("postgresql://"):
            # Already correct format
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        elif database_url.startswith("postgres://"):
            # Some providers use postgres://, convert to postgresql://
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace("postgres://", "postgresql://", 1)
        else:
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Local development: use SQLite
        from pathlib import Path
        db_path = Path(__file__).resolve().parent.parent / "data" / "eduxplain.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()


class User(db.Model):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to predictions
    predictions = db.relationship("Prediction", backref="user", lazy=True)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Prediction(db.Model):
    """Prediction model for storing student predictions."""
    __tablename__ = "predictions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    student_payload = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(255), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    reasons = db.Column(db.Text, nullable=False)  # JSON string
    recommendation = db.Column(db.Text, nullable=False)
    counterfactual = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

