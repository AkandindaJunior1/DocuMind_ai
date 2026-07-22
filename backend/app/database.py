import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
# We go up one directory ("../.env") because this file is inside the backend/ folder.
load_dotenv(dotenv_path="../.env")

# 2. Construct the database URL
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "supersecretpassword")
POSTGRES_DB = os.getenv("POSTGRES_DB", "documind")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")

# This is the string SQLAlchemy uses to connect to Postgres
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

# 3. Create the Engine
# The engine is the central object that manages the connection to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Create a Session factory
# When we want to talk to the database, we ask this factory to create a new "Session"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Create the Base class
# All our models (User, Document, etc.) will inherit from this class.
# It registers them with SQLAlchemy so it knows they exist.
Base = declarative_base()

# 6. Dependency for FastAPI
# Every time a user hits an endpoint that needs the database, we use this function
# to give them a fresh database session, and then close it when they are done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
