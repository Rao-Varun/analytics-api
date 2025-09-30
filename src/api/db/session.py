import sqlmodel
import timescaledb
from .config import DATABASE_URL
from sqlmodel import Session, SQLModel


if DATABASE_URL == "":
    raise NotImplementedError("DATABASE_URL is not set")

engine = timescaledb.create_engine(DATABASE_URL, timezone="UTC")



def init_db():
    print("Initializing database...")
    try:
        print("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        print("creating hypertables...")
        timescaledb.metadata.create_all(engine)
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database tables: {e}")

def get_session():
    with Session(engine) as session:
        yield session