import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
import services
import tiktoken
from dotenv import load_dotenv

from langchain_community.chat_message_histories import SQLChatMessageHistory






chat_history = []

load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPENAI_API_KEY')

os.environ['OPENAI_API_KEY'] = OPEN_AI_API_KEY

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

#Using the tokenizer to calculate the token sizes for both the user and the bot
tokenizer = tiktoken.get_encoding("cl100k_base")

    
def count_tokens(text):
    return len(tokenizer.encode(text))

# Load FAISS index from disk

db = FAISS.load_local(
    "./shared_data/faiss_splitted_index", embeddings, allow_dangerous_deserialization=True
)

# Create the prompt template for the LLM to respond to queries
prompt = ChatPromptTemplate([( "system" ,"Your name is  <ABB Komekci>, you are a helpful AI bot for the ABB bank's customers. All data from ABB bank's official site. Be polite. Given the following information :<context> {context} </context>, answer the question, ONLY use context for information and never made up something that not in the context. Never ask the question and only answer in Azerbaijani.") , MessagesPlaceholder("chat_history"), ("ai" , "Salam men AI Abb komekcisi size nece komek edebilerem?") , ("human" ,"{input}"  )])


contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


# Initialize the OpenAI LLM
llm = ChatOpenAI(openai_api_key = OPEN_AI_API_KEY , model='gpt-4-turbo')

document_chain = create_stuff_documents_chain(llm, prompt)

retriever = db.as_retriever(search_type="similarity", k=3)
          

history_aware_retriever = create_history_aware_retriever(llm, retriever, prompt= contextualize_q_prompt)

chain = create_retrieval_chain(history_aware_retriever, document_chain ) 


# Function to query the chain
#This is not returning response as stream
def query_chain(question):
    result = chain.invoke({"input": question , "chat_history":chat_history} )
    print(result)
    bot_answer = result["answer"]
    chat_history.extend(
    [
        HumanMessage(content=question),
        AIMessage(content=bot_answer),
    ]
)
    return bot_answer





    
#Saving both human and assistant answers for analytics, and also counting the tokens for analytics 
# Function to query the chain

def query_chain_stream(question , chat_id , user_id,  db):
    count = count_tokens(question)
    services.create_message_record(db=db , message = question ,chat_id=chat_id , author= 'human' , token_count=  count , user_id = user_id)
    chat_message_history = SQLChatMessageHistory(session_id=chat_id, connection_string="sqlite:///./abb.db" , table_name='messages')
    chat_history = chat_message_history.get_messages()
    print(chat_id) 
    bot_answer = '' 
    chat_message_history.add_user_message(question )
    for chunk in chain.stream({"input": question , "chat_history": chat_history}):
        if answer_chunk := chunk.get("answer"):
            bot_answer += answer_chunk
            yield answer_chunk
    
    chat_message_history.add_ai_message(bot_answer)
    services.create_message_record(message=bot_answer , chat_id=chat_id , author= 'bot' , token_count= count_tokens(bot_answer) , db=db , user_id = user_id )

    
    
    
#For interacting with documents

    
# Promt with document data input
document_prompt = ChatPromptTemplate([
    ("system", "Your name is <ABB Komekci>, you are a helpful AI bot. You should use data in <document> {document_data} </document>  for  answer the question.  Retrieved context  {context} is about ABB Bank's data. Therefore if user asks about ABB bank check information inside context. Never ask a question and only answer in Azerbaijani."),
    MessagesPlaceholder("chat_history"),
    ("ai", "Salam, mən AI ABB köməkçisiyəm. Sizə necə kömək edə bilərəm?"),
    ("human", "{input}")
])

user_document_chain = create_stuff_documents_chain(llm, document_prompt)

doc_retriever = db.as_retriever(search_type="similarity", k=2)
          

doc_history_aware_retriever = create_history_aware_retriever(llm, doc_retriever, prompt= contextualize_q_prompt)

doc_chain = create_retrieval_chain(doc_history_aware_retriever, user_document_chain ) 

#Saving both human and assistant answers for analytics, and also counting the tokens for analytics 
# Function to query the chain with document

def doc_query_chain_stream(question , doc_data,  chat_id , user_id,  db):
    count = count_tokens(question)
    print(doc_history_aware_retriever.get_prompts())
    services.create_message_record(db=db , message = question ,chat_id=chat_id , author= 'human' , token_count=  count , user_id = user_id)
    chat_message_history = SQLChatMessageHistory(chat_id, connection_string="sqlite:///./abb.db" , table_name='messages')
    chat_history = chat_message_history.get_messages()
    bot_answer = '' 
    chat_message_history.add_user_message(question )
    for chunk in doc_chain.stream({"input": question , "document_data":doc_data , "chat_history": chat_history}):
        if answer_chunk := chunk.get("answer"):
            bot_answer += answer_chunk
            yield answer_chunk
    
    chat_message_history.add_ai_message(bot_answer)
    services.create_message_record(message=bot_answer , chat_id=chat_id , author= 'bot' , token_count= count_tokens(bot_answer) , db=db , user_id = user_id )


