import sqlite3
import os
from datetime import datetime, timezone

def upgrade_legacy_db(db_path='expense.db'):
    if not os.path.exists(db_path):
        print(f"No existing database at {db_path} to migrate.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check transactions columns
    cols = [c[1] for c in cursor.execute('PRAGMA table_info(transactions)').fetchall()]
    
    if 'user_id' not in cols:
        print("Migrating transactions table: adding user_id, created_at, updated_at...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("ALTER TABLE transactions ADD COLUMN created_at DATETIME")
        cursor.execute("ALTER TABLE transactions ADD COLUMN updated_at DATETIME")
        cursor.execute("UPDATE transactions SET created_at = ?, updated_at = ?", (now_str, now_str))
        print("transactions table upgraded.")

    conn.commit()
    conn.close()
    print("Database upgrade completed successfully.")

if __name__ == '__main__':
    upgrade_legacy_db()
