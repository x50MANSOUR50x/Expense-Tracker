import sqlite3

connection = sqlite3.connect("expenses.db")

connection.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")

connection.commit()
connection.close()