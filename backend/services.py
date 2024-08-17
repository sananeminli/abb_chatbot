import  crud 
from db import get_db , DATABASE_URL
from fastapi import  Depends
from sqlalchemy.orm import Session
from langchain_community.chat_message_histories import SQLChatMessageHistory




def get_chat( chat_id   ):
    chat_message_history = SQLChatMessageHistory(chat_id, connection_string=DATABASE_URL, table_name='messages')
    print(chat_message_history.get_messages())
    return  chat_message_history.get_messages()

def create_message_record(  chat_id: str, message: str , author:str, token_count : int ,user_id :int ,  db: Session = Depends(get_db)):
    crud.create_message_data( db,chat_id , message , author , token_count  , user_id) 



def create_convo(db: Session, chat_id, user_id , header ):
    crud.create_chat(db  , chat_id= chat_id , user_id= user_id , header= header)


def get_chats( user_id , db ):
    return crud.get_all_chat( db, user_id=user_id)



#Analytics

def get_average_token_count(db: Session):
    average_tokens = crud.get_average_token_count(db)
    return {"average_tokens": average_tokens}

def get_chats_per_day_dict(db: Session):
    results = crud.get_chats_per_day(db)
    return {
        day: {"session_count": session_count}
        for day, session_count in results
    }

def get_questions_per_day_dict(db: Session):
    results = crud.get_questions_per_day(db)
    return {
        day: {"question_count": question_count}
        for day, question_count in results
    }

def get_token_usage_per_day_combined_dict(db: Session):
    results = crud.get_chats_and_token_usage_per_day_combined(db)
    return {
        day: {"token_usage": token_usage}
        for day, token_usage in results
    }

def get_token_usage_per_day_human(db: Session):
    results = crud.get_chats_and_token_usage_per_day_human(db)
    return {
        day: {"token_usage": token_usage}
        for day, token_usage in results
    }

def get_token_usage_per_day_bot(db: Session):
    results = crud.get_token_usage_per_day_bot(db)
    return {
        day: {"token_usage": token_usage}
        for day, token_usage in results
    }
    
    
def get_questions_count_today_yesterday_dict(db: Session):
    today_count = crud.get_questions_count_today(db)
    yesterday_count = crud.get_questions_count_yesterday(db)
    
    return {
        "today": today_count,
        "yesterday": yesterday_count
    }
    
def get_cost(db:Session):
    count = crud.get_all_token_count(db)
    cost  = count * 15 / 1000000
    
    return {'cost':cost}


def get_user_count(db: Session):
    total_distinct_users = crud.get_total_users_count(db)
    
    return {
        
        "users_count": total_distinct_users
    }
    
def get_avg_question_per_user(db:Session):
    avg_queustion = crud.get_average_questions_per_user(db)
    return {'average_question_user' : avg_queustion}


def get_avg_question_per_chat(db:Session):
    avg_queustion = crud.get_average_questions_per_chat(db)
    return {'average_question_chat' : avg_queustion}