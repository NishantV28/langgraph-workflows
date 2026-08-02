from langgraph.graph import StateGraph,START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict, Annotated 
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages  
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()  

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
def chat_node(State: ChatState):
    messages =State['messages']
    response = model.invoke(messages)
    return {'messages': [response]} 

# Create the database file if it doesn't exist
#sql by default ek hi thread pr work krta h, agar multiple thread pr kaam krna h to check_same_thread=False
conn=sqlite3.connect(database='chatbot.db', check_same_thread=False) 
checkpointer = SqliteSaver(conn=conn) 
graph = StateGraph(ChatState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def get_all_threads():
    all_threads = set()  # to find all the threads in the database, we can use this set to store unique thread_ids
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
