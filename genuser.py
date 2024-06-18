import sqlite3
from werkzeug.security import generate_password_hash

# Create a connection to the database
conn = sqlite3.connect("cache/database.db")
cursor = conn.cursor()

# Hash the password
password = "user"
hashed_password = generate_password_hash(password)

# Insert the user into the database
cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
               ("user", hashed_password, "user"))

# Commit the changes and close the connection
conn.commit()
conn.close()
