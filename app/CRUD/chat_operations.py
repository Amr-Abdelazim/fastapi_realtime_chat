from fastapi import HTTPException
from sqlalchemy.orm import Session
from .. import models
from .user_operations import read_user




def read_chat(chat_id: int, db: Session):
    answer = db.query(models.Chats).filter(models.Chats.chat_id == chat_id).first()
    if answer == None:
        raise HTTPException(status_code=404, detail=f'Chat {chat_id} does not exist')
    return answer

def create_chat(chat: dict, db: Session):
    new_chat = models.Chats(**chat)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat



def create_private_chat(user1_id: int, user2_id: int, chat_id: int, db: Session):
    if user1_id > user2_id:# ensure user1_id < user2_id
        user1_id, user2_id = user2_id, user1_id
    new_private_chat = models.PrivateChats(user1_id= user1_id, user2_id= user2_id,chat_id= chat_id)
    db.add(new_private_chat)
    db.commit()
    db.refresh(new_private_chat)
    return new_private_chat

def link_user_with_chat(user_id: int, chat_id: int, db: Session):
    answer = db.query(models.UserChats).filter(models.UserChats.user_id == user_id and models.UserChats.chat_id == chat_id).first()
    if answer is None:
        link = models.UserChats(user_id=user_id,chat_id=chat_id)
        db.add(link)
        db.commit()

def read_or_create_private_chat(user1_id: int, user2_id: int,db: Session):
    if user1_id > user2_id:# ensure user1_id < user2_id
        user1_id, user2_id = user2_id, user1_id

    answer = db.query(models.PrivateChats).filter(models.PrivateChats.user1_id == user1_id and models.PrivateChats.user2_id == user2_id).first()
    chat_id: int
    if answer is None:
        chat = create_chat({'name':f'{user1_id} : {user2_id}','type':'private'},db) 
        chat_id = int(chat.chat_id)
        create_private_chat(user1_id, user2_id, chat_id, db)
    else:
        chat_id = int(answer.chat_id)
    link_user_with_chat(user_id=user1_id,chat_id=chat_id,db=db)
    link_user_with_chat(user_id=user2_id,chat_id=chat_id,db=db)
    return chat_id



def create_private_message(message: dict,db: Session):# send message from user1_id to user2_id
    user1_id = int(message['user1_id'])
    user2_id = int(message['user2_id'])

    # Check if user1 exists
    user1 = read_user(user1_id, db)
    if user1 is None:
        raise HTTPException(status_code=404, detail=f'User {user1_id} does not exist')

    # Check if user2 exists
    user2 = read_user(user2_id, db)
    if user2 is None:
        raise HTTPException(status_code=404, detail=f'User {user2_id} does not exist')
    
    chat_id = read_or_create_private_chat(user1_id, user2_id, db)
    new_message = models.Messages(user_id= user1_id, chat_id= chat_id, message=message['message'])
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def read_chat_messages(chat_id: int, db: Session):
    chat = read_chat(chat_id, db)
    if chat is None:
        raise HTTPException(status_code=404, detail=f'Chat {chat_id} does not exist')
    return db.query(models.Messages).filter(models.Messages.chat_id == chat_id).all()