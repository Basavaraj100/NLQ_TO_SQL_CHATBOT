import sqlite3
import pandas as pd
from typing import Optional, List
from pathlib import Path


class DataLoader:
    def __init__(self,  db_path: str = "data/sqlite/Data.db"):
        self.db_path = db_path
        # Ensure parent folders exist so sqlite can create the DB file.
        db_path_obj = Path(db_path)
        try:
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            # If we cannot create directories, surface a clearer error.
            raise FileNotFoundError(f"Could not create parent directory for database path: {db_path_obj.parent}")

        try:
            self.conn = sqlite3.connect(str(db_path_obj))
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(f"Unable to open or create database file at {db_path_obj}: {e}")

    def load_data(self, folder_path: str):
        """Load all CSV files from a directory into the SQLite database.

        Each CSV file is written to a table named after the file (filename without
        extension). Example: `students.csv` -> table `students`.

        Args:
            folder_path: Path to a directory containing CSV files.

        Raises:
            FileNotFoundError: if `folder_path` does not exist or is not a directory.
        Returns:
            A list of table names created/updated.
        """
        p = Path(folder_path)
        if not p.exists() or not p.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        created_tables = []
        for csv_path in sorted(p.glob('*.csv')):
            try:
                table_name = csv_path.stem
                data = pd.read_csv(csv_path)
                data.to_sql(table_name, self.conn, if_exists='replace', index=False)
                created_tables.append(table_name)
            except Exception:
                # re-raise with file context for easier debugging
                raise

        return created_tables
            
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
            
            
if __name__ == "__main__":
    loader = DataLoader()
    created_tables = loader.load_data("data/csv")
    print(f"Loaded tables: {created_tables}")