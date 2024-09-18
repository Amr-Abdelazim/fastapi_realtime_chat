from fastapi import FastAPI, Depends
from . import database
from . import models
from sqlalchemy.orm import Session
from . import schema, crud

""" try:
    conn = psycopg2.connect(dbname="fastapi_chat",host="localhost",port="5432",password="h2Tnhvux}3]_k`1Xr'a=#cW4L$bb,6r)C<Q;6RsC3BEY-p\"=J*+498c",user="postgres")
except Exception as error:
    print("error :", error) """

database.apply_changes()

app = FastAPI()

@app.get("/")
def root():
    return {"message":"hello world!!!"}

@app.get("/user/{user_id}")
def read_user(user_id: int, db:Session = Depends(database.get_db)):
    return crud.read_user(user_id,db=db)


@app.post("/add_user")
def add_user(user:schema.User, db:Session = Depends(database.get_db)):
    new_user = crud.create_user(user.model_dump(),db= db)
    
    return new_user

@app.post("/add_chat")
def add_chat(chat:schema.Chat, db:Session = Depends(database.get_db)):
    new_chat = crud.create_chat(chat.model_dump(),db= db)
    
    return new_chat 

@app.post("/send_message")
def send_message(message: schema.Message, db:Session = Depends(database.get_db)):
    try:
        new_message = crud.create_private_message(message.model_dump(),db= db)
    except Exception as error:
        return error
    
    return new_message

@app.get("/read_chat/{chat_id}")
def read_chat(chat_id: int, db:Session = Depends(database.get_db)):
    try:
        chat_messages = crud.read_chat_messages(chat_id, db)
    except Exception as error:
        return error
    
    return chat_messages

