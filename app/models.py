from sqlalchemy import CheckConstraint, Column,Integer,String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.sql import text
from .database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key = True, autoincrement=True)
    username = Column(String, unique=True,nullable=False)
    password = Column(String, nullable=False)

class Chats(Base):
    __tablename__ = 'chats'
    chat_id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))

class PrivateChats(Base):
    __tablename__ = 'private_chats'
    user1_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user1_id', 'user2_id'),
        UniqueConstraint('user1_id','chat_id',name='unique_user1_chat'),
        UniqueConstraint('user2_id','chat_id',name='unique_user2_chat'),
        CheckConstraint('user1_id <= user2_id', name='check_user_order')
        # CheckConstraint('user1_id != user2_id', name='check_user_ids_not_equal') apply this check if you want users doesnt have chat with themself
    )

class PublicChats(Base):
    __tablename__ = 'public_chats'
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'chat_id'),
    )

class Messages(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key = True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=False)
    message = Column(String, nullable=False)
    sent_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))

