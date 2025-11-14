"""Database configuration and models using SQLAlchemy."""
from __future__ import annotations

import logging
import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()

logger = logging.getLogger(__name__)


def _migrate_sqlite_schema() -> None:
    """Migrate existing SQLite schema to match current models."""
    try:
        # Check if predictions table exists and has user_id column
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if "predictions" in tables:
            columns = [col["name"] for col in inspector.get_columns("predictions")]
            if "user_id" not in columns:
                # Add user_id column to existing predictions table
                logger.info("Migrating predictions table: adding user_id column")
                with db.engine.begin() as conn:
                    conn.execute(text("ALTER TABLE predictions ADD COLUMN user_id INTEGER"))
                logger.info("Migration completed successfully")
    except Exception as e:
        # If migration fails, log but don't crash
        logger.warning(f"Schema migration warning: {e}")


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
    
    # Create tables and handle migrations
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Handle migration for existing SQLite databases
        if not database_url or database_url.startswith("sqlite"):
            _migrate_sqlite_schema()


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

