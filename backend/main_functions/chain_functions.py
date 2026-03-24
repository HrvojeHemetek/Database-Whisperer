from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough


from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from ..main_functions.database_functions import extract_table_names, extract_table_keys

## This store manages links between sessions and history.
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Retrieves or creates a chat message history for a given session ID.

    Args:
        session_id (str): The unique identifier for the session.

    Returns:
        BaseChatMessageHistory: The chat message history object.
    """
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


## Function for testing without history
def create_no_history_chain(retriever_docs, typeDB):
    """
    Creates a LangChain chain for basic SQL query generation without history.

    Args:
        retriever_docs: The vector store retriever for documentation.
        typeDB (str): The database type.

    Returns:
        Chain: The configured LangChain chain.
    """
    model = ChatOpenAI(model="gpt-4", temperature=0)  
    template = "You are working with "+typeDB +""" database .Transform this request into SQL prompt for the database given in the following context. With your question,
    you will be given table names you NEED to execute this task. They are extremely important! 
   
    If there is no such SQL prompt for given database, say that the prompt is invalid.

    Also, name your chain of thoughts, meaning your understanding of data tables and corelations. Column and table names you use MUST exist in the database.

    Also, since you are a precise and kind assistant, have a section of reply for your user.

    It is extremely important that you form your reply in content as a JSON: "chainOfThoughts": "...", "SQL": ...","replyToUser":....! I repeat, names must exist in the database description from the context.

    If there is no SQL, give value None. Otherwise, write your SQL without unnecessary signs (no new lines etc)!!

    When making joins with the Employeebranch table, ensure you filter on date columns.
    For example, use:
        -> accounts.opening_date BETWEEN eb.date_from AND eb.date_to
        -> loan.approval_date BETWEEN eb.date_from AND eb.date_to
    This ensures accurate records of employee assignments to branches based on specific dates.
    Apply these date filters in your SQL queries when joining with the Employeebranch table. This is CRUCIAL!

    {question}

    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"question": RunnablePassthrough()}
        | prompt
        | model
    )
    return chain

def create_history_chain(retriever_docs,type):
    """
    Creates a complex RAG chain that is history-aware for SQL query generation.

    Args:
        retriever_docs: The vector store retriever for documentation and schema.
        type (str): The database type.

    Returns:
        RunnableWithMessageHistory: The configured history-aware RAG chain.
    """
    model = ChatOpenAI(model="gpt-4", temperature=0)  

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
    history_aware_retriever = create_history_aware_retriever(
        model, retriever_docs, contextualize_q_prompt
    )

    template = "You are working with "+type +""" database .Transform this request into SQL prompt for the database given in the following context. 
   
    If there is no such SQL prompt for given database, say that the prompt is invalid.

    Also, name your chain of thoughts, meaning your understanding of data tables and corelations. Column and table names you use MUST exist in the database.

    Also, since you are a precise and kind assistant, have a section of reply for your user.

    It is extremely important that you form your reply in content as a JSON: "chainOfThoughts": "...", "SQL": ...","replyToUser":....! I repeat, names must exist in the database description from the context.

    If there is no SQL, give value None.

    {context}

    Question: {question}

    """

    # prompt = ChatPromptTemplate.from_template(template)
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    chain = (
        {"context": retriever_docs}
        | qa_prompt
        | model
    )

    question_answer_chain = create_stuff_documents_chain(model, qa_prompt, output_parser=None)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    chain_with_message_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return chain_with_message_history


def create_chain_1(type):
    """
    Creates a chain dedicated to identifying relevant tables from a user question.

    Args:
        type (str): The database type.

    Returns:
        Chain: The configured LangChain chain for table identification.
    """
    table_names = extract_table_names(type)
    model = ChatOpenAI(model="gpt-4o", temperature=0)  
    template = """ You are a query assistant. You need to look into given question, understand it, and
    see which tables you could use based on given context to resolve the question.

    Names of tables may not directly be specified in the question, but DO try to understand and name it as well.

    1. **Identify Implicit Information**: Not all tables or entities will be explicitly mentioned in the question. Use your understanding to infer relevant entities from the question and context. For example, if the question mentions a person or an action, try to determine which table might correspond to that entity or action.

    2. **Refer to Table Names in Context**: Focus on the names of the tables provided in the context and use them to identify which tables are necessary to answer the question.

    3. **Format Your Answer**: Present the names of the relevant tables in a list format. If no relevant tables can be determined, return `None`.

    Rely heavily on the names of tables given in the context.
    
    Format the answer like this example:

    Example 1)
    Q: Rank branches based on the number of transactions.
    ['branches', 'transactions']

    Example 2)
    Q: How much money did Hana Pana pay in all her transactions?
    ['users', 'transactions']
    
    If there is no table, give value None.

    Context: """ + table_names + """ Question: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"question": RunnablePassthrough()}
        | prompt
        | model
    )
    return chain
 
def create_chain_2(type):
    """
    Creates a chain dedicated to finding indirect relationships between tables using keys.

    Args:
        type (str): The database type.

    Returns:
        Chain: The configured LangChain chain for relationship path identification.
    """
    table_keys = extract_table_keys(type)
    model = ChatOpenAI(model="gpt-4o", temperature=0)  
    template = """Given the following tables and their primary and foreign keys,
    please find all the indirect relationships between each pair of tables by specifying 
    the intermediate tables in the order they are connected by foreign keys. For example, 
    for the relationship from 'branches' to 'credithistories', list the sequence of tables 
    and foreign key connections leading from 'branches' to 'credithistories'. 

    Your final answer is a list of all tables from the realtionships you found. Do not repeat the same table twice.

    Rely heavily on given context! Response should contain chain of thoughts and final answer
    in format given in the example.

    It is extremely important that you form your reply in content as a JSON: "chainOfThoughts": "...", "answer": [....]!

    The "answer" filed MUST include ONLY and EXCLUSIVELY final table names! Do not describe relations of tables. Rely heavily on given example:
    
    Example 1)
    Q: ['branches', 'credithistories']
    "chainOfThoughts": ...,
    "answer": ['branches', 'employeebranch', 'loans', 'credithistories']
    
    If there is no table, give value None.

    Context: """ + table_keys + "\nQuestion: {question}"
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"question": RunnablePassthrough()}
        | prompt
        | model
    )
    return chain
