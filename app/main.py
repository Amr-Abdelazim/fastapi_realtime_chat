from fastapi import FastAPI, Depends, Request, HTTPException, status
from . import database
from sqlalchemy.orm import Session
from . import schema, utils
from .CRUD import user_operations, chat_operations
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from .settings import get_settings
from . import oauth2
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware


database.apply_changes()

oauth2scheme = OAuth2PasswordBearer(tokenUrl='token')

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Rate limit exceeded, please try again later."},
    )


@app.get("/api/")
def root():
    return {"message":"hello world!!!"}

@app.post("/api/token")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()], db:Session = Depends(database.get_db))-> schema.Token:
    user = user_operations.authenticate_user(username=form_data.username, password=form_data.password, db=db)
    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    token = oauth2.create_access_token(data={"sub":user.user_id}, expire_delta=access_token_expires)
    return schema.Token(access_token=token,token_type='bearer')


@app.post("/api/add_user",response_model=schema.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minutes")
async def add_user(user:schema.User, request: Request, db:Session = Depends(database.get_db)):
    print(request)
    user.password = utils.get_password_hash(user.password)
    new_user = user_operations.create_user(user.model_dump(),db= db)
    
    return new_user

@app.get("/api/user/{user_id}", response_model = schema.UserResponse)
def read_user(user_id: int, db:Session = Depends(database.get_db)):
    curren_user = user_operations.read_user(user_id,db=db)
    return curren_user



@app.post("/api/send_message",status_code=status.HTTP_201_CREATED)
def send_message(message: schema.Message, db:Session = Depends(database.get_db), token: str = Depends(oauth2scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = oauth2.user_from_token(token=token,db=db)
    if user.user_id != message.user1_id:
        raise credentials_exception
    
    new_message = chat_operations.create_private_message(message.model_dump(),db= db)
    return new_message

@app.get("/api/read_chat/{chat_id}")
def read_chat(chat_id: int, db:Session = Depends(database.get_db), token: str = Depends(oauth2scheme)):
    exception_handle = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User doesnt belong to this chat !",
        headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = oauth2.user_from_token(token=token,db=db)
    if not user_operations.check_user_chats(user_id=user.user_id,chat_id=chat_id,db=db):
        raise exception_handle

    chat_messages = chat_operations.read_chat_messages(chat_id, db)
    return chat_messages

