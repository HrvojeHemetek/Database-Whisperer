from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

import os
import logging

import shutil


def create_and_store_vector_db(type):
    """
    Creates a vector database from database structure and documentation files,
    then stores it locally using FAISS.

    Args:
        type (str): The type or identifier for the database (e.g., 'postgres', 'oracle').
    """
    # Loading documents
    _ = load_dotenv(find_dotenv())

    struct = []
    ## read db_struct
    loader = TextLoader(f"./backend/db_info/db_struct_{type}.txt", encoding="utf-8")
    struct.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\nTable: "],
                                                   chunk_size=100, 
                                                   chunk_overlap=0)
    split_struct = text_splitter.split_documents(struct)


    ## read db_description
    documentation = []
    loader = TextLoader(f"./backend/db_info/dokumentacija_{type}.txt", encoding="utf-8")
    documentation.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(separators=["-#-# "],
                                                   chunk_size=200, 
                                                   chunk_overlap=0)
    split_documentation = text_splitter.split_documents(struct)

    
    chunks_of_documents = split_struct + split_documentation

    # Generating embeddings
    embeddings = OpenAIEmbeddings()

    vector_documents = FAISS.from_documents(chunks_of_documents, embeddings)
    vector_info_dir = f"./backend/vector_info/{type}"

    os.makedirs(vector_info_dir, exist_ok=True)

    # Check if an old database exists and delete it
    faiss_index_path = os.path.join(vector_info_dir, "faiss_index")
    if os.path.exists(faiss_index_path):
        shutil.rmtree(faiss_index_path)

    # Save new FAISS index
    
    vector_documents.save_local(os.path.join(vector_info_dir, "faiss_index"))


def get_vector_db(type):
    """
    Loads a FAISS vector database for a given database type and returns a retriever.

    Args:
        type (str): The type or identifier for the database.

    Returns:
        VectorStoreRetriever: A retriever object for the FAISS database.
    """
    # Loading embeddings from file in backend/vector_info/
    vector_info_dir = f"./backend/vector_info/{type}"
    embeddings = OpenAIEmbeddings()

    if not(os.path.exists(vector_info_dir) and os.path.isdir(vector_info_dir)):
        print(f"Directory '{vector_info_dir}' does not exist.")
        raise ImportError

    # Setting allow_dangerous_deserialization to True
    loaded_faiss = FAISS.load_local(os.path.join(vector_info_dir, "faiss_index"), embeddings,allow_dangerous_deserialization=True)

    retriever_docs = loaded_faiss.as_retriever(search_type='mmr', search_kwargs={'k':7})
    return retriever_docs
