import jwt
from jwt.exceptions import InvalidTokenError
from datetime import timedelta, timezone,datetime
from .settings import get_settings
from fastapi import HTTPException,status
from . import schema
from .CRUD import user_operations
from sqlalchemy.orm import Session


secret_key = get_settings().secret_key
algorithm = get_settings().algorithm

def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire_delta = datetime.now(timezone.utc) + timedelta(minutes = 15)
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, secret_key, algorithm)
    return token

def user_from_token(token, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schema.TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    
    user = user_operations.read_user(user_id=token_data.user_id,db= db)
    if user is None:
        raise credentials_exception
    return user
