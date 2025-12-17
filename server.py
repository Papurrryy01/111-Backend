from flask import Flask, jsonify, request
import sqlite3


app = Flask(__name__)

DATABASE = "budget.management.db"

def init_db():
    conn = sqlite3.connect(DATABASE) # open a connection to the database
    cursor = conn.cursor() # create a cursor/tool that lets us send commands (SELECT, INSERT,.....) to the database
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit() #save changes
    conn.close() # close the connection to the database

    # with GET dont need to commit or close the connection

@app.get("/api/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

# create a new user
@app.post("/api/register")
def create_user():
    data = request.get_json()
    print(data) 
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)', 
        (username, password)
        ) # executes an SQL statement
    conn.commit() # save changes
    conn.close() # close the connection to the database

    return jsonify({"message": "User registration endpoint"}), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True)