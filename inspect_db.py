import sqlite3
import os

db_path = r"C:\Workspace\Classyy\Backend\db.sqlite3"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Check for anything analytics related
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%influencer%' OR name LIKE '%analytics%');")
    analytics_tables = cursor.fetchall()
    for table in analytics_tables:
        table_name = table[0]
        print(f"Content of {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        print(f"Columns: {[c[1] for c in cursor.fetchall()]}")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        print(cursor.fetchall())
    conn.close()
except Exception as e:
    print(f"Error: {e}")
