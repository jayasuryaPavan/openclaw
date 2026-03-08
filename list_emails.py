import sqlite3
db_path = r"C:\Workspace\Classyy\Backend\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT email FROM users_user LIMIT 5;")
print(cursor.fetchall())
conn.close()
