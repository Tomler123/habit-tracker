from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import logging
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE = 'habits.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    return render_template('index.html', habits=habits)

@app.route('/add-habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        try:
            conn = get_db_connection()
            conn.execute('''
                        INSERT INTO habits (name, description, start_date, dates_completed)
                        VALUES (?, ?, ?, ?)
                    ''', (name, description, datetime.now().strftime('%Y-%m-%d'),
                        ','.join([(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 15)
        ])))
            conn.commit()
        except sqlite3.Error as e:
            # print(f"Database error: {e}")
            logging.error(f"Database error: {e}")

        finally:
            conn.close()
        
        return redirect(url_for('home'))
    
    return render_template('add_habit.html')

@app.route('/delete-habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
    return jsonify({'message': 'Habit deleted successfully!'})

@app.route('/habit/<int:habit_id>')
def habit_details(habit_id):
    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')

    conn = get_db_connection()
    habit = conn.execute('SELECT * FROM habits WHERE id = ?', (habit_id,)).fetchone()

    if not habit:
        conn.close()
        return "Habit not found!", 404

    # Parse dates_completed
    dates_completed = habit['dates_completed'] or ''
    dates_completed_list = dates_completed.split(',') if dates_completed else []

    # Find the last recorded day
    last_date = datetime.strptime(dates_completed_list[-1], '%Y-%m-%d') if dates_completed_list else None

    # Fill in skipped days
    if last_date:
        current_date = last_date + timedelta(days=1)
    else:
        current_date = datetime.strptime(habit['start_date'], '%Y-%m-%d')

    while current_date < today:
        dates_completed_list.append(current_date.strftime('%Y-%m-%d'))  # Mark as missed
        current_date += timedelta(days=1)

    # Update database with missed days
    conn.execute(
        'UPDATE habits SET dates_completed = ? WHERE id = ?',
        (','.join(dates_completed_list), habit_id)
    )
    conn.commit()
    conn.close()

    # Calculate streak representation and current streak
    streak_representation, current_streak = calculate_streak(
        habit['start_date'],
        ','.join(dates_completed_list)
    )

    return render_template(
        'habit.html',
        habit=habit,
        streak_representation=streak_representation,
        current_streak=current_streak
    )



def calculate_streak(start_date, dates_completed):
    """
    Calculate streak representation and current streak.
    Returns:
      - streak_representation: List of booleans (True for completed, False for skipped)
      - current_streak: Count of consecutive completed days up to today
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    today = datetime.today()
    dates_completed = set(datetime.strptime(date, '%Y-%m-%d') for date in dates_completed.split(','))

    streak_representation = []
    current_streak = 0

    # Generate streak representation from start_date to today
    current_date = start_date
    while current_date <= today:
        if current_date in dates_completed:
            streak_representation.append(True)  # Completed day
        else:
            streak_representation.append(False)  # Skipped day
        current_date += timedelta(days=1)

    # Calculate the current streak (last consecutive completed days)
    for completed in reversed(streak_representation):
        if completed:
            current_streak += 1
        else:
            break  # Stop counting if a skipped day is encountered

    return streak_representation, current_streak




@app.route('/complete-habit/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    today = datetime.today().strftime('%Y-%m-%d')

    conn = get_db_connection()
    habit = conn.execute('SELECT * FROM habits WHERE id = ?', (habit_id,)).fetchone()

    if not habit:
        conn.close()
        return jsonify({'message': 'Habit not found!'}), 404

    # Update `dates_completed`
    dates_completed = habit['dates_completed'] or ''
    dates_completed_list = dates_completed.split(',')
    if today not in dates_completed_list:
        dates_completed_list.append(today)

    conn.execute(
        'UPDATE habits SET dates_completed = ? WHERE id = ?',
        (','.join(dates_completed_list), habit_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Habit marked as completed!'})


@app.route('/mark-today/<int:habit_id>', methods=['POST'])
def mark_today(habit_id):
    today = datetime.today().strftime('%Y-%m-%d')

    conn = get_db_connection()
    habit = conn.execute('SELECT * FROM habits WHERE id = ?', (habit_id,)).fetchone()

    if not habit:
        conn.close()
        return jsonify({'message': 'Habit not found!'}), 404

    # Update `dates_completed`
    dates_completed = habit['dates_completed'] or ''
    dates_completed_list = dates_completed.split(',') if dates_completed else []

    if today not in dates_completed_list:
        dates_completed_list.append(today)

    conn.execute(
        'UPDATE habits SET dates_completed = ? WHERE id = ?',
        (','.join(dates_completed_list), habit_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Habit marked for today!'})




if __name__ == '__main__':
    app.run(debug=True)