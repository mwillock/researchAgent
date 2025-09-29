from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

import os

#Build the DB URL from env variables
DB_USER = os.getenv("DB_USER","user")
DB_PASS = os.getenv("DB_PASS", "pass")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT","5432")
DB_NAME = os.getenv("DB_NAME", "research_db")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

#Engine is the core interface to the DB
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
#SessionLocal is a factory for DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#Base is inherited by all your ORM models
Base = declarative_base()

#Dependency for FastAPI routes
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    