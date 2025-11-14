"""Script to reset the local SQLite database (for development only)."""
from pathlib import Path
import os

# Delete the SQLite database file
db_path = Path(__file__).parent / "data" / "eduxplain.db"
if db_path.exists():
    db_path.unlink()
    print(f"✅ Deleted database file: {db_path}")
    print("The database will be recreated automatically on next app startup.")
else:
    print(f"ℹ️  Database file not found: {db_path}")

