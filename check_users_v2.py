import sqlite3
db_path = r"C:\Workspace\Classyy\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users_user);")
print([c[1] for c in cursor.fetchall()])
conn.close()
