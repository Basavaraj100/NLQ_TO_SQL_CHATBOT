
import pandas as pd
import sqlite3
from src.utils.basic_utils import load_yaml_config

DB_PATH = load_yaml_config("configs/db_config.yaml")['db_path'].replace("sqlite:///", "")

#****************** TOOL TO EXECUTE SQL QUERIES AGAINST STUDENT ANALYTICS DB ******************

def execute_sql(query: str) -> str:
    """
    Safely execute validated SELECT queries against the student analytics database.

    Returns:
      - "SUCCESS:\n<csv>" on success with rows
      - "NO_DATA" if query returned zero rows
      - "ERROR: <msg>" on error
    """
    if not query or not query.strip():
        return "ERROR: Empty query"

    if not query.strip().upper().startswith('SELECT'):
        return "ERROR: Only SELECT queries allowed"

    try:
        # Use sqlite3 + pandas for reliable row counting and formatting
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return "NO_DATA"

        # Return CSV so downstream can format or parse easily
        # csv_out = df.to_csv(index=False)
        return f"SUCCESS:\n{str(df)}"
    except Exception as e:
        return f"ERROR: {str(e)}"
