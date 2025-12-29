import duckdb
import sys
import os

def get_duckdb_schema(db_path: str):
    """
    Connects to a DuckDB database and prints the schema (columns and types) for all tables in all schemas.
    """
    if not os.path.exists(db_path):
        print(f"Error: DuckDB file not found at {db_path}", file=sys.stderr)
        return

    try:
        con = duckdb.connect(db_path, read_only=True)
        
        tables = con.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        """).fetchall()
        
        if not tables:
            print(f"No tables found in {db_path}")
            con.close()
            return

        print(f"--- Schema for tables in {db_path} ---")
        for schema_name, table_name in tables:
            qualified_table_name = f'"{schema_name}"."{table_name}"'
            print(f'\n--- Schema: {schema_name}, Table: {table_name} ---')
            schema_df = con.execute(f'DESCRIBE {qualified_table_name}').fetchdf()
            print('Schema:')
            print(schema_df.to_string())
        
        con.close()

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_duckdb_schema.py <path_to_duckdb_file>", file=sys.stderr)
        sys.exit(1)
    
    db_file_path = sys.argv[1]
    get_duckdb_schema(db_file_path)
