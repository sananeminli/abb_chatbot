from fastapi import FastAPI, Request , Depends
from fastapi.responses import StreamingResponse
import abb_chatbot as bot
from sqlalchemy.orm import Session
import services
from db import get_db
from starlette.middleware.cors import CORSMiddleware




app = FastAPI()


# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.post("/query")
async def query(request: Request ,db: Session = Depends(get_db) ):
    data = await request.json()
    question = data.get("query")
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    return StreamingResponse(bot.query_chain_stream(question , chat_id  ,user_id , db), media_type="text/plain")

    # Streaming the response from query_chain_stream
    
    
@app.post("/document-query")
async def query(request: Request ,db: Session = Depends(get_db) ):
    data = await request.json()
    question = data.get("query")
    document_data = data.get("document_data")
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    return StreamingResponse(bot.doc_query_chain_stream(question ,document_data, chat_id  ,user_id , db), media_type="text/plain")





@app.post("/savechat")
async def create_new_chat(request: Request , db: Session = Depends(get_db)):
    data = await request.json()
    user_id  = data.get("user_id")
    chat_id  = data.get("chat_id")
    header = data.get("header")
    services.create_convo(db , chat_id , user_id ,  header)
    
    
@app.get("/getchat/{user_id}")
async def get_convos(user_id : int , db: Session = Depends(get_db)):
    return services.get_chats(user_id=user_id , db = db)

@app.get("/chat/{chat_id}")
async def get_convos(chat_id : str ):
    return services.get_chat(chat_id=chat_id)


@app.get("/analytics/average-token-count",)
def get_average_token_count(db: Session = Depends(get_db)):
    return services.get_average_token_count()(db)

@app.get("/analytics/chats-per-day")
def get_chats_per_day(db: Session = Depends(get_db)):
    return services.get_chats_per_day_dict(db)

@app.get("/analytics/questions-per-day")
def get_questions_per_day(db: Session = Depends(get_db)):
    return services.get_questions_per_day_dict(db)

@app.get("/analytics/token-usage-per-day-combined")
def get_token_usage_per_day_combined(db: Session = Depends(get_db)):
    return services.get_token_usage_per_day_combined_dict(db)

@app.get("/analytics/token-usage-per-day-human")
def get_token_usage_per_day_human(db: Session = Depends(get_db)):
    return services.get_token_usage_per_day_human(db)

@app.get("/analytics/token-usage-per-day-bot")
def get_token_usage_per_day_bot(db: Session = Depends(get_db)):
    return services.get_token_usage_per_day_bot(db)

@app.get("/analytics/average-token-usage")
def get_token_usage_per_day_bot(db: Session = Depends(get_db)):
    return services.get_average_token_count(db)

@app.get("/analytics/questions-count-today-yesterday")
def questions_count_today_yesterday(db: Session = Depends(get_db)):
    return services.get_questions_count_today_yesterday_dict(db)


@app.get("/analytics/cost")
def questions_count_today_yesterday(db: Session = Depends(get_db)):
    return services.get_cost(db)

@app.get("/analytics/users-count")
def users_count(db: Session = Depends(get_db)):
    return services.get_user_count(db)

@app.get("/analytics/average-question-user")
def users_count(db: Session = Depends(get_db)):
    return services.get_avg_question_per_user(db)


@app.get("/analytics/average-question-chat")
def users_count(db: Session = Depends(get_db)):
    return services.get_avg_question_per_chat(db)