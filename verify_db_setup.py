"""Script to verify database setup and list tables."""
import os
from app import app
from src.database import db

with app.app_context():
    # Check database URI
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "Not set")
    print(f"Database URI: {db_uri[:80]}..." if len(db_uri) > 80 else f"Database URI: {db_uri}")
    print()
    
    # List all tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"Found {len(tables)} table(s):")
    for table in tables:
        print(f"  - {table}")
        columns = inspector.get_columns(table)
        print(f"    Columns: {', '.join([col['name'] for col in columns])}")
    print()
    
    # Verify models are registered
    print("Registered models:")
    for model_name in db.Model.registry._class_registry.keys():
        print(f"  - {model_name}")

