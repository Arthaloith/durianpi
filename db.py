import sqlite3
from datetime import datetime

# Database file path
DATABASE_FILE = "cache/database.db"

def create_connection():
    """Create a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables():
    """Create tables in the database if they don't exist."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Create pump log table
        cursor.execute('''CREATE TABLE IF NOT EXISTS pump_log (
                            id INTEGER PRIMARY KEY,
                            timestamp TEXT NOT NULL,
                            event TEXT NOT NULL,
                            duration TEXT NOT NULL)''')
        # Create service log table
        cursor.execute('''CREATE TABLE IF NOT EXISTS service_log (
                            id INTEGER PRIMARY KEY,
                            timestamp TEXT NOT NULL,
                            event TEXT NOT NULL,
                            duration TEXT NOT NULL)''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def log_pump_run(entry):
    """Log a pump run event to the database."""
    sql = '''INSERT INTO pump_log(timestamp, event, duration) VALUES(?,?,?)'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, entry)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def get_latest_pump_run():
    """Get the most recent pump run event from the database."""
    sql = '''SELECT * FROM pump_log WHERE event = 'Pump Run' ORDER BY id DESC LIMIT 1'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            # Convert the result tuple to a dictionary for compatibility with your existing code
            keys = ["id", "timestamp", "event", "duration"]
            return dict(zip(keys, result))
        else:
            return None
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
            
def get_pump_history():
    """Retrieve all pump run events from the database."""
    sql = '''SELECT * FROM pump_log ORDER BY id DESC'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            # Convert the list of tuples to a list of dictionaries for easier processing
            keys = ["id", "timestamp", "event", "duration"]
            return [dict(zip(keys, result)) for result in results]
        else:
            return []
    except sqlite3.Error as e:
        print(e)
        return []  # Return an empty list in case of error
    finally:
        if conn:
            conn.close()


def get_pump_history_only_5():
    """Retrieve the latest 5 pump run events from the database."""
    sql = '''SELECT * FROM pump_log ORDER BY id DESC LIMIT 5'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            # Convert the list of tuples to a list of dictionaries for easier processing
            keys = ["id", "timestamp", "event", "duration"]
            return [dict(zip(keys, result)) for result in results]
        else:
            return []
    except sqlite3.Error as e:
        print(e)
        return []  # Return an empty list in case of error
    finally:
        if conn:
            conn.close()

def clear_pump_history():
    """Clear all pump run events from the database."""
    sql = '''DELETE FROM pump_log'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print("Pump history cleared successfully.")
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
            
def create_tables_profile():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            soil_moisture_threshold INTEGER NOT NULL,
            is_active INTEGER DEFAULT 0
        )''')
    conn.commit()
    conn.close()

def add_or_update_profile(name, threshold):
    conn = create_connection()
    cursor = conn.cursor()
    # Check if the profile already exists
    cursor.execute("SELECT id FROM profiles WHERE name = ?", (name,))
    profile = cursor.fetchone()
    if profile is None:
        # If not, insert a new profile
        cursor.execute("INSERT INTO profiles (name, soil_moisture_threshold) VALUES (?, ?)", (name, threshold))
    else:
        # If it does, update the existing profile
        cursor.execute("UPDATE profiles SET soil_moisture_threshold = ? WHERE name = ?", (threshold, name))
    conn.commit()
    conn.close()


def get_all_profiles():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()
    conn.close()
    return [{'id': profile[0], 'name': profile[1], 'soil_moisture_threshold': profile[2], 'is_active': profile[3]} for profile in profiles]

def set_active_profile(profile_id):
    conn = create_connection()
    cursor = conn.cursor()
    # Set all profiles to inactive
    cursor.execute("UPDATE profiles SET is_active = 0")
    # Set the selected profile to active
    cursor.execute("UPDATE profiles SET is_active = 1 WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()

def get_active_profile():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE is_active = 1 LIMIT 1")
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return {'id': profile[0], 'name': profile[1], 'soil_moisture_threshold': profile[2]}
    return None