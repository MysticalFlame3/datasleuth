import os
import psycopg2
import json
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Postgres Analyst Server")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datasleuth")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@mcp.tool()
def get_database_schema() -> str:
    """Returns the schema of the database including tables and their columns."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        
        rows = cursor.fetchall()
        schema = {}
        for table, column, dtype in rows:
            if table not in schema:
                schema[table] = []
            schema[table].append(f"{column} ({dtype})")
            
        result = "Database Schema:\n"
        for table, columns in schema.items():
            result += f"Table: {table}\n"
            for col in columns:
                result += f"  - {col}\n"
        
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return f"Error fetching schema: {str(e)}"

@mcp.tool()
def execute_sql(sql_query: str) -> str:
    """Executes a SQL query against the postgres database and returns JSON results."""
    is_mutation = any(keyword in sql_query.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE'])
    
    try:
        conn = get_connection()
        # If not a mutation, set readonly for safety. Otherwise, allow mutations!
        if not is_mutation:
            conn.set_session(readonly=True)
        else:
            conn.autocommit = True
            
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        if is_mutation:
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()
            return json.dumps([{"status": f"Success: {rows_affected} rows affected."}])
            
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description] if cursor.description else []
        cursor.close()
        conn.close()
        
        if not rows:
            return json.dumps([])
            
        result_list = []
        for row in rows[:50]:
            row_dict = {col_names[i]: str(row[i]) if not isinstance(row[i], (int, float, bool, type(None))) else row[i] for i in range(len(col_names))}
            result_list.append(row_dict)
            
        return json.dumps(result_list)
    except Exception as e:
        return json.dumps({"error": f"SQL Error: {str(e)}"})

if __name__ == "__main__":
    mcp.run(transport="stdio")
