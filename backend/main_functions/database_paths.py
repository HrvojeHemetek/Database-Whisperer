import os
import networkx as nx

def fetch_schema(db_type):
    """
    Reads the database structure from a text file and parses it into a schema dictionary.

    Args:
        db_type (str): The type of the database (e.g., 'postgres', 'oracle').

    Returns:
        dict: A dictionary mapping table names to their foreign key information.
    """
    path_to_database = (os.path.dirname(os.path.dirname(__file__))) + f"\\db_info\\db_struct_{db_type}.txt"
    schema = {}
    
    with open(path_to_database, 'r') as file:
        data = file.read()

    tables = data.split("Table:")[1:]

    for table in tables:
        table = table.strip()
        table_name = table.split(' ', 1)[0].strip()

        foreign_keys = table.split('Foreign Keys:')[1].strip()
        if foreign_keys != "":
            foreign_keys = foreign_keys.split("\n")
            for i in range(len(foreign_keys)):
                fk = foreign_keys[i]
                referred_table = fk.split("References:")[1].strip()
                referred_table = referred_table[:referred_table.index("(")]
                fk = {"referred_table": referred_table}
                foreign_keys[i] = fk

        schema[table_name] = {
            'foreign_keys': foreign_keys
        }

    return schema

def build_graph(schema):
    """
    Builds a directed graph representing the database schema where edges represent foreign key relationships.

    Args:
        schema (dict): The database schema dictionary.

    Returns:
        nx.DiGraph: A NetworkX directed graph.
    """
    graph = nx.DiGraph()
    
    for table, details in schema.items():
        graph.add_node(table)
        for fk in details['foreign_keys']:
            graph.add_edge(fk['referred_table'], table)
    
    return graph

def find_all_paths(graph, start_node):
    """
    Finds all possible paths starting from a given node in the graph using Depth First Search.

    Args:
        graph (nx.DiGraph): The directed graph.
        start_node (str): The node to start the search from.

    Returns:
        list: A list of all identified paths (each path is a list of nodes).
    """
    paths = []
    
    def dfs(current_path):
        current_node = current_path[-1]
        neighbors = list(graph.successors(current_node))
        if not neighbors:
            paths.append(current_path)
            return
        
        for neighbor in neighbors:
            if neighbor not in current_path:  # To avoid cycles
                dfs(current_path + [neighbor])
            else:
                paths.append(current_path)
    
    dfs([start_node])
    return paths

def generate_all_paths(schema):
    """
    Generates all possible paths in the database schema graph.

    Args:
        schema (dict): The database schema dictionary.

    Returns:
        list: A list of all possible paths in the schema.
    """
    graph = build_graph(schema)
    all_paths = []
    
    for node in graph.nodes():
        paths_from_node = find_all_paths(graph, node)
        all_paths.extend(paths_from_node)
    
    return all_paths

def main():
    """
    Main function to demonstrate schema fetching and path generation.
    """
    schema = fetch_schema('postgres')
    paths = generate_all_paths(schema)

    for path in paths:
        print(path)
    
    print("Number of paths:", len(paths))

if __name__ == '__main__':
    main()