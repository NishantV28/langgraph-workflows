import streamlit as st
from backend_sqllite import chatbot, get_all_threads
from langchain_core.messages import BaseMessage, HumanMessage
import uuid #help to generate unique thread_id for each conversation

#************************************utility functions********************************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_conversation():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    #load conversation history from checkpointer
    return chatbot.get_state(config = {'configurable': {'thread_id': thread_id}}).values['messages']


#*************************************session setup*******************************************

#st.session_state ->dict do not get updated when we press enter 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = get_all_threads()  # Load existing threads from the database
add_thread(st.session_state['thread_id'])

#************************************sidebar setup********************************************
st.sidebar.title("Conversation")
if st.sidebar.button("New Chat"):
    reset_conversation()

st.sidebar.header("History")

for thread_id in st.session_state['chat_thread'][::-1]:  # Display threads in reverse order (most recent first)
   if st.sidebar.button(str(thread_id)):
       st.session_state['thread_id'] = thread_id
       messages = load_conversation(st.session_state['thread_id'])

       temp_messages = []
       for message in messages:
           if isinstance(message, HumanMessage):
               temp_messages.append({"role": "user", "content": message.content})
           else:
               temp_messages.append({"role": "assistant", "content": message.content})

       st.session_state['message_history'] = temp_messages
        
#*********************************Main UI******************************************************

st.header("Your known Chatbot")
#loading conversation history from checkpointer
message_history = []
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here...")


if user_input:

    #add message to session state
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    #streaming response from langgraph chatbot
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]}, 
                config = {'configurable': {'thread_id': st.session_state['thread_id']}},  
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})