from db import User, DATABASE_FILE

user = User(DATABASE_FILE)
user.create_table()
