"""
Migration script to add deleted_at column to emails table
"""
import sqlite3
from pathlib import Path

# Get database path
PROJECT_ROOT = Path(__file__).parent
db_path = PROJECT_ROOT / 'data' / 'email_scanner.db'

print(f"Migrating database: {db_path}")

if not db_path.exists():
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column already exists
cursor.execute("PRAGMA table_info(emails)")
columns = [row[1] for row in cursor.fetchall()]

if 'deleted_at' in columns:
    print("✓ Column 'deleted_at' already exists")
else:
    print("Adding 'deleted_at' column...")
    cursor.execute("ALTER TABLE emails ADD COLUMN deleted_at DATETIME")
    conn.commit()
    print("✓ Column 'deleted_at' added successfully")

conn.close()
print("\nMigration complete!")
