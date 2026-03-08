import sqlite3
db_path = r"C:\Workspace\Classyy\Backend\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users_user);")
print([c[1] for c in cursor.fetchall()])
cursor.execute("SELECT email, instagram_username, instagram_followers, youtube_channel_name FROM users_user WHERE instagram_username IS NOT NULL OR youtube_channel_name IS NOT NULL LIMIT 5;")
print(cursor.fetchall())
conn.close()
