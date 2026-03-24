def fetch_relevant_tables(type, table_names):
    """
    Fetches the structure of relevant tables from the database structure file.

    Args:
        type (str): The database type.
        table_names (list): A list of table names to fetch.

    Returns:
        str: A string containing the definitions of the requested tables.
    """
    result = []
    current_table = None
    is_reading_table = False

    file_path = f"./backend/db_info/db_struct_{type}.txt"
    
    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            
            if stripped_line.startswith("Table:"):
                # Store the read record if it is the requested table
                if is_reading_table and current_table in table_names:
                    result.append("".join(current_table_lines))
                
                # Read new table
                current_table = stripped_line.split(":")[1].strip()
                current_table_lines = [line] 
                is_reading_table = current_table in table_names
            elif is_reading_table:
                current_table_lines.append(line) 
        
        # Last table
        if is_reading_table and current_table in table_names:
            result.append("".join(current_table_lines))
    
    return "".join(result)

