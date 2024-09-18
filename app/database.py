from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from .settings import get_settings

Base = declarative_base()
engine = create_engine(get_settings().db_url)
SessionLocal = sessionmaker(bind = engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
    finally:
        db.close()


def apply_changes():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    apply_changes()


