import sqlite3
db_path = r"C:\Workspace\Classyy\Backend\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT email, first_name, last_name FROM users_user;")
print(cursor.fetchall())
conn.close()
