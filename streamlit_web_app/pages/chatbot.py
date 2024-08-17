import streamlit as st
import requests
import os
from dotenv import load_dotenv
import random




load_dotenv()
BASE_URL  =  os.getenv("BACKEND_URL")


querry_url  = BASE_URL +'/query'
document_url = BASE_URL +'/document-query'
new_chat_url  = BASE_URL + '/savechat'




# Login dialog box for getting user ID

@st.dialog("Put Your User ID")
def get_user_id():
    
    user_id = int(st.number_input("User ID"  , min_value=1 , step=1 ))
    if st.button("Login"):
        st.session_state.user_id = user_id
        st.rerun()

# Getting a response from the AI 
def stream_response(url, data):
    with requests.post(url, json=data, stream=True) as response:
        for chunk in response.iter_content(decode_unicode=True):
            if chunk:
                yield chunk

# Retrieving old messages from the API based on chat ID

def fetch_messages_from_api(chat_id:str):
    chat_history_url = BASE_URL+f"/chat/{chat_id}"
    response = requests.get(chat_history_url)
    if response.status_code == 200:
        messages = response.json()
        # Convert API response to the format used in session_state
        st.session_state.messages = []
        for msg in messages:
            role = "assistant" if msg['type'] == 'ai' else "user"
            st.session_state.messages.append({"role": role, "content": msg['content']})
    
    
# Clearing the session state without removing the user ID

def clear_history():
        if 'chat_id' in st.session_state:
            del st.session_state['chat_id']
        if 'header' in st.session_state:
            del st.session_state['header']
        if 'messages'  in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Salam men ABB komekci. Size ABB kreditleri haqqinda komek edebilerem. Buyurun sualiniz verin!"}]
        if 'chat_id' in st.session_state:
            del st.session_state['chat_id']  
        if 'selected_option'   in st.session_state:
              del st.session_state['selected_option']
        if 'old_chats'   in st.session_state:
              del st.session_state['old_chats']
        print(st.session_state)

        st.rerun()
        

st.title("🤖 ABB ChatBot")

if "user_id" not in st.session_state:
    st.session_state["user_id"] = 0
    get_user_id()
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Salam men ABB komekci. Size ABB kreditleri haqqinda komek edebilerem. Buyurun sualiniz verin!"}]

if "selected_option" not in st.session_state:
    st.session_state["selected_option"] = None
    
if "chat_id" not in st.session_state:
    st.session_state["chat_id"] =  random.randint(100000, 999999)
    

    
# If user logged in show the content
if st.session_state.user_id !=0:

    uploaded_file = st.sidebar.file_uploader("Choose a text file", type=["txt"])
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")
    
    #Getting previous chats of the user
    
    if "old_chats" not in st.session_state:
        chats_url  = BASE_URL + '/getchat/' + str(st.session_state.user_id)
        response = requests.get(chats_url)
        st.session_state["old_chats"] = {item['chat_id']: item['header'] for item in response.json()}

    
    selected_chat_id = st.sidebar.selectbox(
            "Select Previous  Chat",
            options=list(st.session_state.old_chats.keys()),  # Chat IDs
            format_func=lambda chat_id: st.session_state.old_chats.get(chat_id, ''),  
            index=None,
            placeholder='Select Previous  Chat'

        )
    
    
    # Log out button
    if st.sidebar.button('Log Out!') and 'user_id' in st.session_state:
        st.session_state.clear()
        st.rerun()
    



    #If user select one of the previous chats from selectbox update session states and remove some input fields
    
    if selected_chat_id != None:
        fetch_messages_from_api(selected_chat_id)
        st.header(st.session_state.old_chats[selected_chat_id])
        st.session_state.selected_option  = selected_chat_id
        st.session_state.chat_id   = selected_chat_id
        st.sidebar.warning('If you want to start a new chat, select  x from the dropdown menu.')



            
    else:
        header = st.text_input(label= 'Chat Name' , placeholder='Give name to this chat!' , value='New Chat') 
        if st.session_state.selected_option !=None or  st.sidebar.button('New Chat!'):
            clear_history()
        if st.sidebar.button('Save This Chat And Close!'):
            data = {'user_id': st.session_state.user_id  , 'chat_id' : st.session_state.chat_id  , 'header' : header }
            requests.post(new_chat_url , json=data)
            clear_history()
            selected_chat_id = None
            st.rerun()
    

    #Showing messages inside session state
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    
    
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        #If user uploaded a file use the url for document query
        if uploaded_file != None:
                with st.chat_message("assistant"):
                    data  = {'query':prompt , 'document_data' : content ,'chat_id' : st.session_state.chat_id  , 'user_id' :  st.session_state.user_id}
                    print(content)
                    response = st.write_stream(stream_response(document_url , data))
                    st.session_state.messages.append({"role": "assistant", "content": response})
        else:   
        
            with st.chat_message("assistant"):
                data  = {'query':prompt , 'chat_id' : st.session_state.chat_id  , 'user_id' :  st.session_state.user_id}
                
                response = st.write_stream(stream_response(querry_url , data))
                st.session_state.messages.append({"role": "assistant", "content": response})
