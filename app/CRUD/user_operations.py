from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, utils


def read_user(user_id: int, db: Session):
    answer = db.query(models.User).filter(models.User.user_id == user_id).first()
    if answer == None:
        raise HTTPException(status_code=404, detail=f'User {user_id} does not exist')
    return answer

def check_username(username: str, db: Session):
    answer = db.query(models.User).filter(models.User.username == username).first()
    if answer == None:
        return False
    return answer

def authenticate_user(username: str, password: str, db: Session):
    exception_handle = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password!",
        headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = check_username(username, db)
    if not user:
        raise exception_handle
    
    if not utils.verify_password(plain_password=password, hashed_password=user.password):
        raise exception_handle
    
    return user


def create_user(user: dict, db: Session):
    if check_username(user['username'],db):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'username {user["username"]} is reserved')
    
    new_user = models.User(**user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user