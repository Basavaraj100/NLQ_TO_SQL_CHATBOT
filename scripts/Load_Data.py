import sqlite3
import pandas as pd
from typing import Optional, List


class DataLoader:
    def __init__(self,  db_path: str = "data/databases/sqlite/Data.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

    def load_data(self,uploaded_csv_files: list):
        """Load CSV files into the SQLite database."""
        for uploaded_file in uploaded_csv_files:
            table_name = uploaded_file.split("/")[-1].split(".")[0]
            data = pd.read_csv(uploaded_file)
            data.to_sql(table_name, self.conn, if_exists='replace', index=False)
            
    def create_indexes(self, index_statements: Optional[List[str]] = None):
        """Create indexes in the SQLite database.

        If `index_statements` is None or empty, the method does nothing.

        Example:
            # Single index
            loader.create_indexes([
                "CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)"
            ])

            # Multiple indexes
            loader.create_indexes([
                "CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)",
                "CREATE INDEX IF NOT EXISTS idx_courses_title ON courses(title)"
            ])

        Notes:
            - Prefer `IF NOT EXISTS` to avoid errors if an index already exists.
            - Each list element should be a single SQL statement string.
        """
        if not index_statements:
            return

        cursor = self.conn.cursor()
        try:
            for index_statement in index_statements:
                cursor.execute(index_statement)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cursor.close()