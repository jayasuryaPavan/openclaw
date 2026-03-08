import sqlite3
import os

db_path = r"c:\Work Space\Classyy\Backend\db.sqlite3"
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for influencer analytics table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%influenceranalytics%';")
        table = cursor.fetchone()
        if table:
            table_name = table[0]
            cursor.execute(f"SELECT ig_followers, yt_subscribers, last_synced_at FROM {table_name} ORDER BY last_synced_at DESC LIMIT 5;")
            rows = cursor.fetchall()
            for r in rows:
                print(f"IG: {r[0]}, YT: {r[1]}, Synced: {r[2]}")
        else:
            print("Analytics table not found")
        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")
else:
    print("DB not found")
