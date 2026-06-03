import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'lyrics.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute('ALTER TABLE track_lyrics ADD COLUMN play_count INTEGER DEFAULT 0;')
    conn.commit()
    print("Column added successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
