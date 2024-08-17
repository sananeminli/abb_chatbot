from sqlalchemy.orm import Session
from sqlalchemy import func,  Date,and_
import models  
from models import Messages
from datetime import date, timedelta

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str):
    db_user = models.User(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_message_data(db: Session, chat_id: str, message: str , author:str, token_count : int , user_id:int):
    db_data = models.Messages(message = message , chat_id = chat_id , author = author , token_count = token_count , user_id = user_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def get_chat(db: Session, chat_id: str):
    return db.query(models.Chat).filter(models.Chat.chat_id == chat_id).all()

def get_messages(db: Session, chat_id: str):
    return db.query(models.Messages).filter(models.Messages.chat_id == chat_id).all()



def get_all_chat(db: Session, user_id: int):
    return db.query(models.Chat).filter(models.Chat.user_id == user_id).all()


def create_chat(db: Session, chat_id: str, user_id: int , header : str):
    db_chat = models.Chat(chat_id=chat_id, user_id=user_id , header  = header)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

#Analytics


def get_total_users_count(db: Session):
    return (
        db.query(
            func.count(func.distinct(Messages.user_id)).label("total_distinct_user_count")
        )
        .filter(
            Messages.author == 'human'
        )
        .scalar()  
    )


def get_all_token_count(db: Session):
    return (
        db.query(
            func.sum(Messages.token_count).label("all_tokens")
        )
        .scalar()  
    )
    
def get_average_token_count(db: Session):
    return (
        db.query(
            func.avg(Messages.token_count).label("average_tokens")
        )
        .scalar()
    )

def get_chats_per_day(db: Session):
    day_expr = func.date(Messages.timestamp)
    
    return (
        db.query(
            day_expr.label("day"),
            func.count(func.distinct(Messages.chat_id)).label("session_count")
        )
        .group_by(day_expr)
        .all()
    )

def get_questions_per_day(db: Session):
    day_expr = func.date(Messages.timestamp)

    return (
        db.query(
            day_expr.label("day"),
            func.count(Messages.id).label("question_count")
        )
        .filter(Messages.author == "human")
        .group_by(day_expr)
        .all()
    )


def get_chats_and_token_usage_per_day_combined(db: Session):
    day_expr = func.date(Messages.timestamp)
    
    return (
        db.query(
            day_expr.label("day"),
            func.sum(Messages.token_count).label("token_usage")
        )
        .group_by(day_expr)
        .all()
    )

def get_chats_and_token_usage_per_day_human(db: Session):
    day_expr = func.date(Messages.timestamp)
    
    return (
        db.query(
            day_expr.label("day"),
            func.sum(Messages.token_count).label("token_usage")
        )
        .filter(Messages.author == "human")
        .group_by(day_expr)
        .all()
    )


def get_token_usage_per_day_bot(db: Session):
    day_expr = func.date(Messages.timestamp)
    
    return (
        db.query(
            day_expr.label("day"),
            func.sum(Messages.token_count).label("token_usage")
        )
        .filter(Messages.author == "bot")
        .group_by(day_expr)
        .all()
    )


def get_questions_count_today(db: Session):
    today = date.today()
    
    return (
        db.query(
            func.count(Messages.id).label("question_count")
        )
        .filter(
            Messages.author == 'human',
            func.date(Messages.timestamp) == today
        )
        .scalar()  
    )

def get_questions_count_yesterday(db: Session):
    yesterday = date.today() - timedelta(days=1)
    
    return (
        db.query(
            func.count(Messages.id).label("question_count")
        )
        .filter(
            Messages.author == 'human',
            func.date(Messages.timestamp) == yesterday
        )
        .scalar()  
    )
    
    
#Returns the average number of messages (questions) per user using user_id.

def get_average_questions_per_user(db: Session):
    
    subquery = db.query(
        Messages.user_id,
        func.count(Messages.id).label('question_count')
    ).group_by(Messages.user_id).subquery()
    
    avg_questions_per_user = db.query(func.avg(subquery.c.question_count)).scalar()
    return avg_questions_per_user

    
#Returns the average number of messages (questions) per chat using chat_id.

def get_average_questions_per_chat(db: Session):
    
    subquery = db.query(
        Messages.chat_id,
        func.count(Messages.id).label('question_count')
    ).group_by(Messages.chat_id).subquery()
    
    avg_questions_per_chat = db.query(func.avg(subquery.c.question_count)).scalar()
    return avg_questions_per_chat
