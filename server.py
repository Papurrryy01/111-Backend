from flask import Flask, jsonify, request
import sqlite3
from datetime import date


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

    #expenses table
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Add missing columns for existing databases
    cursor.execute('PRAGMA table_info(expenses)')
    columns = [row[1] for row in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute('ALTER TABLE expenses ADD COLUMN category TEXT')

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


#get all users
# http://localhost:5000/api/users
@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users') 
    rows= cursor.fetchall() # retrieves all rows of a query result
    print(rows)
    conn.close() 

    users = []
    for row in rows:
        user = {"id": row[0], "username": row[1]}
        users.append(user)


    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
        }), 200


@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404

    user = {"id": row[0], "username": row[1]}

    return jsonify({
        "success": True,
        "message": "User retrieved successfully",
        "data": user
        }), 200



#Delete a user
@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

#create a condition to add a validation if the user id does not exist
    
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
            }), 404

    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": "User deleted successfully"
        }), 200



@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET username = ?, password = ? WHERE id = ?', (username, password, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "User updated successfully"}), 200



# expenses endpoints would go here
# http://localhost:5000/api/expenses
@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date_str = date.today().isoformat()  # Convert date to ISO format
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO expenses (title, description, amount, date, category, user_id) VALUES (?, ?, ?, ?, ?, ?)',
        (title, description, amount, date_str, category, user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense created successfully"
        }), 201

# http://localhost:5000/api/expenses
@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, amount, date, category, user_id FROM expenses')
    rows = cursor.fetchall()
    conn.close()

    expenses = []
    for row in rows:
        expense = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "amount": row[3],
            "date": row[4],
            "category": row[5],
            "user_id": row[6]
        }
        expenses.append(expense)

    return jsonify({
        "success": True,
        "message": "Expenses retrieved successfully",
        "data": expenses
    }), 200

# http://localhost:5000/api/expenses/1
@app.get("/api/expenses/<int:expense_id>")
def get_expense(expense_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, description, amount, date, category, user_id FROM expenses WHERE id = ?',
        (expense_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({
            "success": False,
            "error": "Expense not found"
        }), 404

    expense = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "amount": row[3],
            "date": row[4],
            "category": row[5],
            "user_id": row[6],
    }

    return jsonify({
        "success": True,
        "message": "Expense retrieved successfully",
        "data": expense
    }), 200

# http://localhost:5000/api/expenses/1
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": "Expense deleted successfully"
    }), 200

# http://localhost:5000/api/expenses/1
@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    data = request.get_json()
    title = data.get("title")
    user_id = data.get("user_id")
    amount = data.get("amount")
    description = data.get("description")
    category = data.get("category")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE expenses SET title = ?, user_id = ?, amount = ?, description = ?, category = ? WHERE id = ?',
        (title, user_id, amount, description, category, expense_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense updated successfully"
        }), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
