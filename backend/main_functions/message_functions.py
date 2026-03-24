import json
import pandas as pd
import ast

from .Message import *
from .data_struct_functions import fetch_relevant_tables


chain = None
conn = None
chain_tables = None
chain_paths = None
type = None

def chat_with_user(chain_Arg,conn_Arg, c1_Arg, c2_Arg, type_Arg):
    """
    Initializes global variables for chat and database connection.

    Args:
        chain_Arg: The LangChain chain for general chat.
        conn_Arg: The database connection object.
        c1_Arg: The chain for interpreting tables.
        c2_Arg: The chain for interpreting paths.
        type_Arg: The database type.
    """
    global chain, conn,chain_tables,chain_paths, type
    chain = chain_Arg
    conn = conn_Arg
    chain_tables = c1_Arg
    chain_paths= c2_Arg
    type = type_Arg

def invoke_interpret_tables(command:str):
    """
    Invokes the table interpretation chain to identify relevant tables from a user command.

    Args:
        command (str): The user's natural language command.

    Returns:
        list: A list of identified table names.
    """
    global chain_tables
    tables =chain_tables.invoke(command)
    #Try to format the output
    #If incompatible input or no answer, handled exception
    try:
        tables = tables.content
        tables_list = ast.literal_eval(tables)
        if not tables_list:
            tables_list = []
    except:
        tables_list = []
    return tables_list

def invoke_interpret_paths(tables:str):
    """
    Invokes the path interpretation chain to find relationships between identified tables.

    Args:
        tables (str): A string representation of the identified tables.

    Returns:
        list: A list representing the path or relationships between tables.
    """
    global chain_paths
    path = chain_paths.invoke(str(tables))
    try:
        path = path.content
        #for unpredicted generating HARDCODED 

        #TO DO REGEX ......................................
        if (path.startswith("```json")):
            path = path[7:-3].strip()
        path= json.loads(path)
        path = path["answer"]
        if not path:
            path = []
    except:
        path = []
    print(path)
    return path

def invoke_interpret_message(command:str, context:str):
    """
    Invokes the main message interpretation chain to generate SQL and a response.

    Args:
        command (str): The user's natural language command.
        context (str): The context (relevant table structures/descriptions).

    Returns:
        dict: A dictionary containing 'chainOfThoughts', 'SQL', and 'replyToUser'.
    """
    response = chain.invoke("Your context : "+ context + "Your question: "+ command)
    #Unpredicted formating error handle
    try:
        result_cont = response.content


        ###########TO DO REGEX...................
        if (result_cont.startswith("```json")):
            result_cont = result_cont[7:-3].strip()
    except:
        result = {"chainOfThoughts":'',"SQL":'',"replyToUser":'Oops, we are experiencing some unpredicted communication with OpenAi. Try again later.'}
    #Invalid prompt error handling
    try:
        result = json.loads(result_cont)
    except:
        result = {"chainOfThoughts":'',"SQL":'',"replyToUser":'Your request is not clear. Could you please provide more details?'}
    
    return result

# This is for testing with a chain without history
def interpret_message(command:str):
    """
    Interprets a user message by identifying tables, paths, and generating/executing SQL.

    Args:
        command (str): The user's natural language command.

    Returns:
        Message: A message object containing the result and query rows.
    """
    global chain, conn, type
    if not(chain and conn):
        return "Oops, you don't have an open connection to this database. Try to connect again or refresh the page."
    
    #Fetch table names from query
    tables_list = invoke_interpret_tables(command)
    if tables_list and len(tables_list)> 1:
        path = invoke_interpret_paths(tables_list)
    else:
        path = []
    path.extend(tables_list)
    print(path)
    #invoke SQL generator
    if len(path)>0:
        context = fetch_relevant_tables(type,path)
        result = invoke_interpret_message(command, context)
    else:
        result ={"chainOfThoughts":'',"SQL":'',"replyToUser":'Your request is not clear. Could you please provide more details?'}
    
    if not result["SQL"]:
        result["SQL"] = str(result["SQL"])
    if result['SQL'] not in {'None', ''} or 'SELECT' in result['SQL'].upper():
        try:
            row= pd.read_sql_query(result['SQL'], conn).to_dict()
        except:
            result["replyToUser"]= "The query failed in the database. Query: "+result["SQL"]
            result["SQL"] = ''
            row = ''
    else:
        row = ''
    to_send = Message(result, row).send()
    return to_send


def interpret_message_with_history(command:str):
    """
    Interprets a user message while maintaining conversation history.

    Args:
        command (str): The user's natural language command.

    Returns:
        Message: A message object containing the result and query rows.
    """
    global chain, conn
    if not(chain and conn):
        return "Oops, you don't have an open connection to this database. Try to connect again or refresh the page."
    response = chain.invoke(
         {"input": command},
         config={
             "configurable": {"session_id": 225552}
         },
         )
    try:
        result = json.loads(response["answer"])
    except:
        result = {"chainOfThoughts":'',"SQL":'',"replyToUser":'Your request is not clear. Could you please provide more details?'}
    if result['SQL'] not in {'None','', "null"}:
        try:
            row= pd.read_sql_query(result['SQL'], conn).to_dict()
        except:
            raise InterruptedError("The query failed in the database") 
    else:
        row = ''
    to_send = Message(result, row).send()
    return to_send

def interpret_message_FAKE(commnad:str):
    """
    Returns a fake message for testing purposes.

    Args:
        commnad (str): The user's natural language command.

    Returns:
        Message: A fake message object.
    """
    result = {"chainOfThoughts":'I cannot think.',"SQL":'SELECT * FROM YOUR_BAG',"replyToUser":'I do not feel intelligent today.'}
    to_send = Message(result, '').send()
    return to_send
