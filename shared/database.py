# shared/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json
import boto3

# Cache for database URL (fetched once per Lambda container)
_database_url_cache = None
_engine = None
_SessionLocal = None

def get_database_url():
    """Get database URL from environment or Secrets Manager (cached)"""
    global _database_url_cache
    
    # Return cached value if available
    if _database_url_cache:
        return _database_url_cache
    
    # Check if running in Lambda with Secrets Manager
    db_secret_arn = os.getenv("DB_SECRET_ARN")
    
    if db_secret_arn:
        # Fetch credentials from Secrets Manager (only once per container)
        client = boto3.client('secretsmanager')
        
        try:
            response = client.get_secret_value(SecretId=db_secret_arn)
            secret = json.loads(response['SecretString'])
            
            _database_url_cache = f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:{secret.get('port', 5432)}/{secret['dbname']}"
            return _database_url_cache
        except Exception as e:
            print(f"Error fetching secret: {e}")
            raise
    
    # Default to environment variable or SQLite for local/testing
    _database_url_cache = os.getenv("DATABASE_URL", "sqlite:///./metrics.db")
    return _database_url_cache

def get_engine():
    """Get SQLAlchemy engine (lazy initialization, cached per container)"""
    global _engine
    if _engine is None:
        database_url = get_database_url()
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
        )
    return _engine

def get_session_local():
    """Get SessionLocal (lazy initialization, cached per container)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

# Module-level variables for backwards compatibility
engine = get_engine()
SessionLocal = get_session_local()
Base = declarative_base()

def get_db():
    """Dependency to get DB session for FastAPI"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()