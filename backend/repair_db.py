import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import engine, Base
from app.models import *

def create_missing_tables():
    print("--- Checking and creating missing tables ---")
    try:
        # This will create all tables that don't exist yet
        Base.metadata.create_all(bind=engine)
        print("Success: Database schema synchronized.")
    except Exception as e:
        print(f"Error during synchronization: {e}")

if __name__ == "__main__":
    create_missing_tables()
