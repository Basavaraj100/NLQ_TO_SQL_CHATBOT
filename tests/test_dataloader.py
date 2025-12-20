import os
import sqlite3
import tempfile
import pytest

from scripts.Load_Data import DataLoader


def create_sample_table(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("CREATE TABLE students(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    cur.execute("INSERT INTO students(name, age) VALUES ('Alice', 23), ('Bob', 24)")
    conn.commit()


def test_create_indexes_none_does_nothing(tmp_path):
    # create a temporary sqlite file
    db_file = tmp_path / "test.db"
    loader = DataLoader(str(db_file))

    # create a sample table
    create_sample_table(loader.conn)

    # calling create_indexes with None should not raise and should not create any indexes
    loader.create_indexes(None)

    cur = loader.conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = cur.fetchall()
    # no indexes created
    assert indexes == []


def test_create_indexes_creates_index(tmp_path):
    db_file = tmp_path / "test2.db"
    loader = DataLoader(str(db_file))
    create_sample_table(loader.conn)

    # create an index using the method
    idx_stmt = "CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)"
    loader.create_indexes([idx_stmt])

    cur = loader.conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_students_name'")
    indexes = cur.fetchall()
    assert len(indexes) == 1


if __name__ == '__main__':
    pytest.main([os.path.dirname(__file__)])
