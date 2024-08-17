


import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv


load_dotenv()


BASE_URL =   os.getenv('BACKEND_URL') + "/analytics"  # Change to your actual base URL


# Function to fetch data from FastAPI

def fetch_data(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}")
    return response.json()

if 'chats_per_day' not in st.session_state:
    st.session_state.chats_per_day = fetch_data("chats-per-day")
    
if 'questions_per_day' not in st.session_state:
    st.session_state.questions_per_day = fetch_data("questions-per-day")
    
if 'token_usage_per_day_combined' not in st.session_state:
    st.session_state.token_usage_per_day_combined = fetch_data("token-usage-per-day-combined")
    
if 'token_usage_per_day_human' not in st.session_state:
    st.session_state.token_usage_per_day_human = fetch_data("token-usage-per-day-human")
    
if 'token_usage_per_day_bot' not in st.session_state:
    st.session_state.token_usage_per_day_bot = fetch_data("token-usage-per-day-bot")
    
if 'average_token_usage' not in st.session_state:
    st.session_state.average_token_usage = fetch_data("average-token-usage")["average_tokens"]
    
if 'question_count' not in st.session_state:
    st.session_state.question_count = fetch_data("questions-count-today-yesterday")
    

if 'users_count' not in st.session_state:
    st.session_state.users_count = fetch_data("users-count")['users_count']
    
    
if 'cost' not in st.session_state:
    st.session_state.cost = fetch_data("cost")['cost'] 
    
if 'question_per_user' not in st.session_state:
    st.session_state.question_per_user = fetch_data("average-question-user")['average_question_user']
    
if 'question_per_chat' not in st.session_state:
    st.session_state.question_per_chat = fetch_data("average-question-chat")['average_question_chat']

# Function to convert data to DataFrame with dates on x-axis
def convert_to_dataframe(data):
    if data:  
        
        df = pd.DataFrame.from_dict(data, orient='index')
        
        # Ensure index is in datetime format
        df.index = pd.to_datetime(df.index).date  
        
        # Sort by date
        df.sort_index(inplace=True)
        return df
    return pd.DataFrame()  # Return an empty DataFrame if data is empty



st.title('Analytics Dashboard')

st.divider()

st.header('Metrics')
col1, col2, col3 = st.columns(3)

col1.metric('Cost' ,str(st.session_state.cost) + '$' , st.session_state.cost  )
col2.metric('Average Token Usage' , round(st.session_state.average_token_usage , 2) ,round(st.session_state.average_token_usage , 2) )
col3.metric('Asked Questions Today' , st.session_state.question_count['today'] ,st.session_state.question_count['today'] -st.session_state.question_count['yesterday']  )


col4 , col5 , col6  = st.columns(3)
col4.metric('Total Users Count', st.session_state.users_count ,st.session_state.users_count- 0)
col5.metric('Average questions count per user' , st.session_state.question_per_user)
col6.metric('Average questions count per chat' , st.session_state.question_per_chat)
st.divider()

# Select box for choosing which chart to display
chart_option = st.selectbox(
    "Select the chart you want to view:",
    (
        "Chats per Day",
        "Questions per Day",
        "Token Usage per Day (Combined)",
        "Token Usage per Day (Human)",
        "Token Usage per Day (Bot)"
    )
)

# Display the selected chart
if chart_option == "Chats per Day":
    st.header('Chats per Day')
    df_chats = convert_to_dataframe(st.session_state.chats_per_day)
    if not df_chats.empty:
        st.bar_chart(df_chats, use_container_width=True )
    else:
        st.write("No data available for chats per Day.")

elif chart_option == "Questions per Day":
    st.header('Questions per Day')
    df_questions = convert_to_dataframe(st.session_state.questions_per_day)
    if not df_questions.empty:
        st.bar_chart(df_questions, use_container_width=True)
    else:
        st.write("No data available for Questions per Day.")

elif chart_option == "Token Usage per Day (Combined)":
    st.header('Token Usage per Day (Combined)')
    df_token_usage_combined = convert_to_dataframe(st.session_state.token_usage_per_day_combined)
    if not df_token_usage_combined.empty:
        st.bar_chart(df_token_usage_combined, use_container_width=True)
    else:
        st.write("No data available for Token Usage per Day (Combined).")

elif chart_option == "Token Usage per Day (Human)":
    st.header('Token Usage per Day (Human)')
    df_token_usage_human = convert_to_dataframe(st.session_state.token_usage_per_day_human)
    if not df_token_usage_human.empty:
        st.bar_chart(df_token_usage_human, use_container_width=True)
    else:
        st.write("No data available for Token Usage per Day (Human).")

elif chart_option == "Token Usage per Day (Bot)":
    st.header('Token Usage per Day (Bot)')
    df_token_usage_bot = convert_to_dataframe(st.session_state.token_usage_per_day_bot)
    if not df_token_usage_bot.empty:
        st.bar_chart(df_token_usage_bot, use_container_width=True)
    else:
        st.write("No data available for Token Usage per Day (Bot).")