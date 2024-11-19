import sqlite3
from datetime import datetime, timedelta

DATABASE = 'habits.db'

# Connect to the database
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Clear existing data (optional)
cursor.execute('DELETE FROM habits')

# Define sample habits
habits = [
    {
        "name": "Workout",
        "description": "Daily exercise routine",
        "start_date": (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
        "dates_completed": ','.join([
            (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)
        ])  # All 10 days completed
    },
    {
        "name": "Read Books",
        "description": "Read 10 pages daily",
        "start_date": (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
        "dates_completed": ','.join([
            (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15) if i % 2 == 0
        ])  # Completed every other day
    },
    {
        "name": "Meditation",
        "description": "10 minutes of meditation",
        "start_date": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        "dates_completed": ','.join([
            (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15) if i % 2 == 0
        ])
    },
    {
        "name": "Drink Water",
        "description": "Drink 2 liters of water",
        "start_date": (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
        "dates_completed": ','.join([
            (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 15)
        ])  # Completed only for 5 days starting 10 days ago
    },
]

# Insert sample habits into the database
for habit in habits:
    cursor.execute('''
        INSERT INTO habits (name, description, start_date, dates_completed)
        VALUES (?, ?, ?, ?)
    ''', (habit["name"], habit["description"], habit["start_date"], habit["dates_completed"]))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database populated successfully!")
