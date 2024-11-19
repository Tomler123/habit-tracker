import sqlite3

DATABASE = 'habits.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Check if 'start_date' column exists
cursor.execute("PRAGMA table_info(habits)")
columns = [column[1] for column in cursor.fetchall()]

if 'start_date' not in columns:
    cursor.execute('ALTER TABLE habits ADD COLUMN start_date TEXT')
    print("Added 'start_date' column.")

if 'dates_completed' not in columns:
    cursor.execute('ALTER TABLE habits ADD COLUMN dates_completed TEXT')
    print("Added 'dates_completed' column.")

conn.commit()
conn.close()

print("Database schema updated!")
