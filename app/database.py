from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

db_url = os.getenv('DB_URL')

Base = declarative_base()
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind = engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def apply_changes():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    apply_changes()


