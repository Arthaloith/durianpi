#========================================================================================================#
#                                                                                                        #
#                                               LIBRARY IMPORTS                                          #
#                                                                                                        #
#========================================================================================================#
import sqlite3
from datetime import datetime
from sqlite3 import Error
from werkzeug.security import generate_password_hash, check_password_hash
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                          USER DATABASE STUFF                                           #
#                                                                                                        #
#========================================================================================================# 
# Database file path
DATABASE_FILE = "cache/database.db"

class User:
    def __init__(self, db_file):
        self.db_file = db_file

    @property
    def conn(self):
        return sqlite3.connect(self.db_file)

    def create_table(self):
        try:
            with self.conn as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user')
                ''')
        except sqlite3.Error as e:
            print(e)

    def create_user(self, username, password, role='user'):
        password_hash = generate_password_hash(password)
        with self.conn as conn:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, password_hash, role))
        return self.get_user(username)

    def get_user(self, username):
        with self.conn as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=?", (username,))
            rows = cur.fetchall()
            if rows:
                return UserRow(rows[0])
            return None

    def get_user_by_id(self, user_id):
        with self.conn as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
            rows = cur.fetchall()
            if rows:
                return UserRow(rows[0])
            return None

    def get_all_users(self):
        with self.conn as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            return [UserRow(row) for row in rows]

    def update_user(self, id, username, role):
        with self.conn as conn:
            conn.execute("UPDATE users SET username=?, role=? WHERE id=?", (username, role, id))

    def delete_user(self, id):
        with self.conn as conn:
            conn.execute("DELETE FROM users WHERE id=?", (id,))

class UserRow:
    def __init__(self, row):
        self.id = row[0]
        self.username = row[1]
        self.password = row[2]
        self.role = row[3]

    def check_password(self, password):
        return check_password_hash(self.password, password)
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                            PUMP DATABASE STUFFS                                        #
#                                                                                                        #
#========================================================================================================#
# Create connection to db
def create_connection():
    """Create a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
    except sqlite3.Error as e:
        print(e)
    return conn

# Create pump log table
def create_tables():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS pump_log (
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

# Log a pump run event to the database
def log_pump_run(entry):
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

# Get latest pump run entry
def get_latest_pump_run():
    sql = '''SELECT * FROM pump_log WHERE event = 'Pump Run' ORDER BY id DESC LIMIT 1'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            keys = ["id", "timestamp", "event", "duration"]
            return dict(zip(keys, result))
        else:
            return None
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

# Get all pump history     
def get_pump_history():
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

# Get top 5 most recent pump history
def get_pump_history_only_5():
    sql = '''SELECT * FROM pump_log ORDER BY id DESC LIMIT 5'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            keys = ["id", "timestamp", "event", "duration"]
            return [dict(zip(keys, result)) for result in results]
        else:
            return []
    except sqlite3.Error as e:
        print(e)
        return []  
    finally:
        if conn:
            conn.close()
            
# Yeet pump history
def clear_pump_history():
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

#========================================================================================================#
#                                                                                                        #
#                                          PROFILE DATABASE STUFF                                        #
#                                                                                                        #
#========================================================================================================#     
# Create profiles table
def create_tables_profile():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            soil_moisture_threshold INTEGER NOT NULL,
            pump_duration INTEGER NOT NULL,
            is_active INTEGER DEFAULT 0
        )''')
    conn.commit()
    conn.close()

# Does what it says on the tin, add if doesnt exist, update if it does exists
def add_or_update_profile(name, threshold, pump_duration):
    conn = create_connection()
    cursor = conn.cursor()
    # Check if the profile already exists
    cursor.execute("SELECT id FROM profiles WHERE name = ?", (name,))
    profile = cursor.fetchone()
    if profile is None:
        # If not, insert a new profile
        cursor.execute("INSERT INTO profiles (name, soil_moisture_threshold, pump_duration) VALUES (?, ?, ?)", (name, threshold, pump_duration))
    else:
        # If it does, update the existing profile
        cursor.execute("UPDATE profiles SET soil_moisture_threshold = ?, pump_duration = ? WHERE name = ?", (threshold, pump_duration, name))
    conn.commit()
    conn.close()

# Get all profiles
def get_all_profiles():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, soil_moisture_threshold, pump_duration, is_active FROM profiles")
    profiles = cursor.fetchall()
    conn.close()
    return [{'id': profile[0], 'name': profile[1], 'soil_moisture_threshold': profile[2], 'pump_duration': profile[3], 'is_active': profile[4]} for profile in profiles]

# Set chosen profile active
def set_active_profile(profile_id):
    conn = create_connection()
    cursor = conn.cursor()
    # Set all profiles to inactive
    cursor.execute("UPDATE profiles SET is_active = 0")
    # Set the selected profile to active
    cursor.execute("UPDATE profiles SET is_active = 1 WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()

#Get active profile
def get_active_profile():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, soil_moisture_threshold, pump_duration FROM profiles WHERE is_active = 1 LIMIT 1")
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return {'id': profile[0], 'name': profile[1], 'soil_moisture_threshold': profile[2], 'pump_duration': profile[3]}
    return None

# Yeet profile
def delete_profile(profile_id):
    """Delete a profile from the database."""
    sql = '''DELETE FROM profiles WHERE id = ?'''
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (profile_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

#========================================================================================================#
#                                                                                                        #
#                                          ANALYTIC DATABASE STUFF                                       #
#                                                                                                        #
#========================================================================================================#  
def get_most_active_day():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m-%d', timestamp) AS date, COUNT(*) AS event_count
            FROM pump_log
            GROUP BY date
            ORDER BY event_count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        else:
            return None, None
    except sqlite3.Error as e:
        print(e)
        return None, None
    finally:
        if conn:
            conn.close()

def get_most_active_month():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m', timestamp) AS month, COUNT(*) AS event_count
            FROM pump_log
            GROUP BY month
            ORDER BY event_count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        else:
            return None, None
    except sqlite3.Error as e:
        print(e)
        return None, None
    finally:
        if conn:
            conn.close()

def get_least_active_day():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m-%d', timestamp) AS date, COUNT(*) AS event_count
            FROM pump_log
            GROUP BY date
            ORDER BY event_count ASC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        else:
            return None, None
    except sqlite3.Error as e:
        print(e)
        return None, None
    finally:
        if conn:
            conn.close()

def get_total_events():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) AS total_events
            FROM pump_log
        ''')
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(e)
        return None
    finally:
        if conn:
            conn.close()
#========================================================================================================#


