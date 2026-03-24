# Database Whisperer
Database Whisperer is a full-stack web application featuring a Django REST Framework backend and a React frontend, designed as an advanced AI-powered assistant for interacting with enterprise databases like PostgreSQL and Oracle using natural language. At its core, it leverages RAG (Retrieval-Augmented Generation) by utilizing LangChain and OpenAI embeddings to convert database schemas and documentation into vector formats, stored securely in a local FAISS database. This allows the system to intelligently retrieve the most relevant table structures needed to answer a user's question. To generate precise SQL queries from natural language, the application relies heavily on advanced prompt engineering with OpenAI's GPT models. Furthermore, the system is designed for a seamless conversational user experience by maintaining message history via LangChain, and it even supports audio input processing using SpeechRecognition and MoviePy.

## 1. Mandatory installations
These should be all additional installations needed to run this project.

```bash
    pip install django
    pip install djangorestframework
    pip install python-dotenv
    pip install psycopg2-binary
    pip install oracledb
    pip install langchain
    pip install langchain-openai
    pip install langchain-community
    pip install langchain-core
    pip install langchain-text-splitters
    pip install openai
    pip install faiss-cpu
    pip install SpeechRecognition
    pip install moviepy
    pip install networkx
    pip install pandas
```

Or install all at once:

```bash
    pip install -r install.txt
```

## 2. Set up the environment
In order to have functional OpenAI calls and database connections, you should set up the environment file appropriately (create a `.env` file). Adjust your own `OPENAI_API_KEY` and ensure that the database credentials for both Postgres and Oracle (such as `POSTGRES_USERNAME`, `POSTGRES_PSW`, `ORACLE_USERNAME`, etc.) are correctly set.

## 3. Make migrations
Once you are positioned in the project root directory, you need to set up the mandatory Django migrations. Run these commands in your terminal:

```bash
  python manage.py makemigrations
  python manage.py migrate
```

Bonus tip: If you encounter any additional errors related to db.sqlite3, run this command:

```bash
  python manage.py migrate  --run-syncdb
```

## 4. Run backend
In order to run the code, open your terminal, position yourself to project root and run the following command:

```bash
    python manage.py runserver
```

## 5. Run frontend
Open your terminal, position yourself to the "frontend" folder and run the following command in order to install node modules:

```bash
    npm install
```

Then run the following command in order to start the application:

```bash
    npm start
```