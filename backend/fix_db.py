import os
import sys

# Add the current directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import SessionLocal

def fix_database():
    db = SessionLocal()
    try:
        # Alter the embedding column to be 3072 dimensions instead of 768
        db.execute(text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(3072);"))
        db.commit()
        print("Database schema successfully updated to 3072 dimensions!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_database()
