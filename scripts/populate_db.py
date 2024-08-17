from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import website_scraper  as scraper
import os
from dotenv import load_dotenv

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')


#Getting web site data

texts = scraper.get_splitted_content()



embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

#Saving vectors in FAISS vector db


db   = FAISS.from_texts(texts=texts , embedding=embeddings)


db.save_local("./shared_data/faiss_splitted_index")