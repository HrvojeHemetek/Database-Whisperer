import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
import oracledb
import shutil


postgres_commands = ["SELECT current_schema()", 
                     "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = 'BASE TABLE';",
                     "db_struct_postgres_temp.txt",
                     "SELECT column_name, data_type FROM information_schema.columns WHERE table_name= %s AND table_schema = %s",
                     "SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = %s::regclass AND i.indisprimary",  # Get primary keys
                    "SELECT kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name FROM information_schema.key_column_usage kcu JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = kcu.constraint_name WHERE kcu.table_name = %s AND kcu.table_schema = %s AND kcu.position_in_unique_constraint IS NOT NULL"  # Get foreign keys
] #[postgres_schema,
oracle_commands = ["SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL",
                    "SELECT table_name FROM all_tables WHERE owner = :schema_name",
                    "db_struct_oracle_temp.txt",
                    "SELECT column_name, data_type FROM all_tab_columns WHERE table_name = :table_name AND owner = :schema_name",
                    "SELECT cols.column_name FROM all_cons_columns cols JOIN all_constraints cons ON cols.constraint_name = cons.constraint_name WHERE cons.constraint_type = 'P' AND cols.table_name = :1 AND cols.owner = :2",  # Get primary keys
    "SELECT a.column_name, c_pk.table_name r_table_name, b.column_name r_column_name FROM all_cons_columns a JOIN all_constraints c ON a.owner = c.owner AND a.constraint_name = c.constraint_name JOIN all_constraints c_pk ON c.r_owner = c_pk.owner AND c.r_constraint_name = c_pk.constraint_name JOIN all_cons_columns b ON c_pk.owner = b.owner AND c_pk.constraint_name = b.constraint_name AND b.position = a.position WHERE c.constraint_type = 'R' AND a.table_name = :1 AND a.owner = :2"  # Get foreign keys
] #


def connect_to_centralDB():
    """
    Connects to the central database using Oracle instant client and environment variables.

    Returns:
        oracledb.Connection: The established Oracle database connection.
    """

    oracledb.init_oracle_client(config_dir=os.environ["INSTANT_CLIENT_LOCATION_CENTRALDB"])

    dsn = "centraldb_high"   # one of the network aliases from tnsnames.ora
    params = oracledb.ConnectParams(config_dir=os.environ["CENTRALDB_CONFIG_DIR"],
                                    wallet_location=os.environ["CENTRALDB_CONFIG_DIR"])
    params.parse_connect_string(dsn)
    dsn = params.get_connect_string()
    connection = oracledb.connect(user=os.environ["CENTRALDB_USERNAME"],
                                password=os.environ["CENTRALDB_PSW"], 
                                dsn=dsn)

    if connection.is_healthy():
        print("Healthy connection to CentralDB!")
    else:
        print("Unusable connection to CentralDB. Please check the database and network settings.")
    
    return connection


def connect_with_oracle():
    """
    Establishes a connection to an Oracle database using environment variables.

    Returns:
        oracledb.Connection: The Oracle database connection.
    """
    _ = load_dotenv(find_dotenv())

    user = os.environ["ORACLE_USERNAME"]
    psw = os.environ["ORACLE_PSW"]
    config = os.environ["ORACLE_CONFIG_DIR"]
    dsn = os.environ["ORACLE_DSN"]
    wallet_loc = os.environ["ORACLE_WALLET_LOCATION"]
    inst_client = os.environ["INSTANT_CLIENT_LOCATION"]
    
    oracledb.init_oracle_client(lib_dir=inst_client)

    conn = oracledb.connect(
        config_dir=config,
        dsn=dsn,
        user=user,
        password=psw,   
        wallet_location=wallet_loc    
        
    )
    return conn

def connect_with_postgres():
    """
    Establishes a connection to a PostgreSQL database using environment variables.

    Returns:
        psycopg2.connection: The PostgreSQL database connection.
    """
    user = os.environ["POSTGRES_USERNAME"]
    psw = os.environ["POSTGRES_PSW"]
    db = os.environ["POSTGRES_DATABASE"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    conn = psycopg2.connect(database=db, 
                            user=user, 
                            host=host,
                            password=psw,
                            port=port)
    return conn


def connect_to_database(type:str):
    """
    Connects to a specified database type (postgres or oracle) and updates the local schema structure.

    Args:
        type (str): The database type.

    Returns:
        tuple: A tuple containing (connection, same_as_old_schema_boolean).
    """
    _ = load_dotenv(find_dotenv())
    if type == 'postgres':
        conn = connect_with_postgres()
        get_db_struct(conn, 'postgres')
        print("Successfully connected to our postgres database")
    elif type == 'oracle':
        conn = connect_with_oracle()
        get_db_struct(conn, 'oracle')
        print("Successfully connected to our oracle database")
    else:
        raise NameError("Database type not defined!")
    
    old_path = f"./backend/db_info/db_struct_{type}.txt"
    new_path = f"./backend/db_info/db_struct_{type}_temp.txt"

    same = False

    # Programmatic solution for determining all trajectories goes here

    if os.path.exists(old_path):
        exising = open(old_path,"r").readlines()
        current = open(new_path, "r").readlines()

        same = exising == current
    if not same:
        shutil.copyfile(new_path, old_path)
    return conn, same
    

def get_db_struct(conn,type):
    """
    Fetches the database structure (tables, columns, types, keys) and writes it to a temporary file.

    Args:
        conn: The database connection.
        type (str): The database type.
    """
    if type == 'postgres':
        commands = postgres_commands
    elif type == 'oracle':
        commands = oracle_commands
    else:
        raise NameError("Database type not defined!")
    
    # create cursor to execute sql commands
    cur = conn.cursor()
    cur.execute(commands[0])
    schema_name = cur.fetchone()[0]

    # sql to fetch all tables from db
    cur.execute(commands[1], (schema_name,))
    tables = cur.fetchall()

    table_column = {}
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db_info', commands[2]))
    try:
       with open(file_path, 'w') as file:
           # get all columns for each table
           for table in tables:
               table_name = table[0]
               file.write(f"\n\nTable: {table_name}\n")
               
               # SQL to fetch columns and data type
               cur.execute(commands[3], (table_name, schema_name,))
               columns = cur.fetchall()

               # Write columns to file
               for column in columns:
                   file.write(f"  Column: {column[0]}, Type: {column[1]}\n")
                
               # SQL to fetch primary keys
               if type == 'postgres':
                   cur.execute(commands[4], (table_name,))
               else:
                   cur.execute(commands[4], (table_name, schema_name))
               primary_keys = cur.fetchall()
               file.write("  Primary Keys:\n")
               for pk in primary_keys:
                   file.write(f"    {pk[0]}\n")

               # SQL to fetch foreign keys
               cur.execute(commands[5], (table_name, schema_name,))
               foreign_keys = cur.fetchall()
               file.write("  Foreign Keys:\n")
               for fk in foreign_keys:
                   file.write(f"    Column: {fk[0]}, References: {fk[1]}({fk[2]})\n")

               file.write("\n")  # Add an empty line between tables
               table_column[table_name] = columns
           file.close()

    finally:
       cur.close()

    return

def extract_table_names(typeDB):
    """
    Extracts all table names from the saved database structure file.

    Args:
        typeDB (str): The database type.

    Returns:
        str: A comma-separated string of table names.
    """
    path_to_database = (os.path.dirname(os.path.dirname(__file__))) + f"\\db_info\\db_struct_{typeDB}.txt"
    table_names = list()
    with open(path_to_database, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if ('Table: ' in line):
            table_names.append(line.split('Table: ')[1].strip())

    return ', '.join(table_names)

def extract_table_keys(typeDB):
    """
    Extracts table names and their primary/foreign keys from the saved database structure file.

    Args:
        typeDB (str): The database type.

    Returns:
        str: A newline-separated string of tables and their keys.
    """
    path_to_database = (os.path.dirname(os.path.dirname(__file__))) + f"\\db_info\\db_struct_{typeDB}.txt"
    table_keys = list()
    with open(path_to_database, 'r') as file:
        lines = file.readlines()

    block_table_name_and_keys = ''
    check_primary_key = False
    check_foreign_key = False
    for line in lines:
        if ('Table: ' in line):
            block_table_name_and_keys += line
            continue
        if ('Primary Keys:' in line):
            block_table_name_and_keys += line
            check_primary_key = True
            continue
        if (check_primary_key and 'Foreign Keys:' not in line):
            block_table_name_and_keys += line
            continue
        if ('Foreign Keys:' in line):
            block_table_name_and_keys += line
            check_primary_key = False
            check_foreign_key = True
            continue
        if (not check_primary_key and line != '\n' and check_foreign_key):
            block_table_name_and_keys += line
            continue
        if (line == '\n'):
            table_keys.append(block_table_name_and_keys.strip())
            block_table_name_and_keys = ''
            check_foreign_key = False
            continue
        
    return '\n'.join(table_keys)


if __name__ == '__main__':
    print(extract_table_keys('postgres'))