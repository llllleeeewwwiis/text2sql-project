# schema_loader.py
import sqlite3

def load_schema_from_sqlite(db_path):
    """
    Parse SQLite database schema:
    - Tables
    - Columns
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables_raw = cursor.fetchall()

    schema = {"db_id": db_path, "tables": []}

    for (tname,) in tables_raw:
        # skip SQLite internal meta tables
        if tname.startswith("sqlite_"):
            continue

        cursor.execute(f"PRAGMA table_info('{tname}')")
        cols_info = cursor.fetchall()

        # cols_info: (cid, name, type, notnull, dflt_value, pk)
        columns = [row[1] for row in cols_info]
        types = [row[2] for row in cols_info]

        schema["tables"].append({
            "table_name": tname,
            "columns": columns,
            "types": types
        })

    conn.close()
    return schema


if __name__ == "__main__":
    schema = load_schema_from_sqlite("spider_data/database/academic/academic.sqlite")
    print(schema)

