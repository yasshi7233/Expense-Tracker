import sqlite3

DATABASE = 'expense.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor =conn.cursor()
    cursor.execute('''
                   
        CREATE TABLE IF NOT EXISTS transactions (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT NOT NULL,
                   type TEXT NOT NULL,
                   category TEXT NOT NULL,
                   amount REAL NOT NULL,
                   note TEXT
         )
     ''')
    conn.commit()
    conn.close()
    print("Database ready")
    
if __name__ == '__main__':
    init_db()