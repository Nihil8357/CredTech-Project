# backend/database.py
import sqlite3

DATABASE_NAME = "credit_data.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create a table to store time-series data for various metrics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credit_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        ticker TEXT NOT NULL,
        metric_name TEXT NOT NULL,
        metric_value REAL NOT NULL
    )
    ''')
    
    # Create an index for faster lookups by ticker
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker ON credit_metrics (ticker, timestamp)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Run this function once manually to create the DB file
if __name__ == '__main__':
    init_db()