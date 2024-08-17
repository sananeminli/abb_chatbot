from sqlalchemy import Column, Integer, String,  DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
from db import DATABASE_URL



engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    # Relationships
    chats = relationship("Chat", back_populates="user")
    messages = relationship("Messages", back_populates="user")  
class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True, index=True)
    header = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="chats")

class Messages(Base):
    __tablename__ = "message_data"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    message = Column(String, index=True)
    author = Column(String, index=True)
    timestamp = Column(DateTime, default=func.now())
    token_count = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="messages")

# Create the database tables
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database and tables created.")
