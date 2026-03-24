import os
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv, find_dotenv

import os
from dotenv import load_dotenv, find_dotenv

from .database_functions import *
from .message_functions import *
from .vector_db_functions import *
from .chain_functions import *

conns = dict()

def check_connection(type):
    """
    Checks if a connection to the specified database type exists,
    creates one if it doesn't, and starts a chat session.

    Args:
        type (str): The database type ('postgres' or 'oracle').
    """
    global conns
    if type not in {'postgres','oracle'}:
        raise NameError
    print(conns.keys())
    if type not in conns.keys():
        create_new_db_connection(type)
    start_chat(type)

def create_new_db_connection(type:str):
    """
    Creates a new database connection and initializes the vector database if necessary.

    Args:
        type (str): The database type.

    Returns:
        connection: The established database connection.
    """
    global conns
    structure_same = True
    if type not in conns.keys():
        conn, structure_same = connect_to_database(type)
        conns[type]=conn
    if not (os.path.exists(f"./backend/vector_info/{type}") and os.path.isdir(f"./backend/vector_info/{type}")) or not structure_same:
        create_and_store_vector_db(type)
    conn = conns[type]
    start_chat(type) 
    return conn


def start_chat(type:str):
    """
    Starts a chat session by initializing the LangChain chains and vector store retriever.

    Args:
        type (str): The database type.

    Returns:
        str: "ok" if successful.
    """
    global conns
    _ = load_dotenv(find_dotenv())
    retriever_docs = get_vector_db(type)
    try:
        conn = conns[type]
    except:
        print(conns.keys())
        raise KeyError("Connection does not exist")

    chain_with_message_history = create_history_chain(retriever_docs, type)
    #chain_with_message_history = create_no_history_chain(retriever_docs, type)
    chain1= create_chain_1(type)
    chain2=create_chain_2(type)
    chat_with_user(chain_with_message_history, conn,chain1,chain2, type)
    return "ok"

