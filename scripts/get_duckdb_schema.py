import duckdb
import sys
import os

def get_duckdb_schema(db_path: str):
    """
    Connects to a DuckDB database and prints the schema (columns and types) for all tables.
    """
    if not os.path.exists(db_path):
        print(f"Error: DuckDB file not found at {db_path}", file=sys.stderr)
        return

    try:
        con = duckdb.connect(db_path, read_only=True)
        
        tables = con.execute('SHOW TABLES').fetchall()
        table_names = [t[0] for t in tables]
        
        if not table_names:
            print(f"No tables found in {db_path}")
            con.close()
            return

        print(f"--- Schema for tables in {db_path} ---")
        for table_name in table_names:
            print(f'\n--- Table: {table_name} ---')
            schema = con.execute(f'DESCRIBE {table_name}').fetchdf()
            print('Schema:')
            print(schema.to_string())
        
        con.close()

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_duckdb_schema.py <path_to_duckdb_file>", file=sys.stderr)
        sys.exit(1)
    
    db_file_path = sys.argv[1]
    get_duckdb_schema(db_file_path)
