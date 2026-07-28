import sqlite3
from datetime import date, timedelta
import random
 
DATABASE = 'expenses.db'
 
transactions = [
    ('income',  'Salary',        (15000, 20000), 'Monthly salary'),
    ('expense', 'Rent',          (8000,  8000),  'House rent'),
    ('expense', 'Food',          (200,   800),   'Groceries / dining'),
    ('expense', 'Transport',     (50,    300),   'Auto / bus / petrol'),
    ('expense', 'Shopping',      (300,   2000),  'Clothes / online order'),
    ('expense', 'Entertainment', (100,   500),   'Movies / games'),
    ('expense', 'Health',        (200,   1500),  'Medicine / doctor'),
    ('income',  'Other',         (500,   2000),  'Freelance / gift'),
]
 
def seed():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
 
    cursor.execute("DELETE FROM transactions")
 
    today = date.today()
    inserted = 0
 
    for month_offset in range(4):
        first_of_month = (today.replace(day=1) - timedelta(days=month_offset * 30))
 
        for _ in range(random.randint(6, 10)):
            t_type, category, (lo, hi), note = random.choice(transactions)
 
            day_offset = random.randint(0, 27)
            txn_date = first_of_month + timedelta(days=day_offset)
 
            amount = round(random.uniform(lo, hi) / 10) * 10
 
            cursor.execute(
                'INSERT INTO transactions (date, type, category, amount, note)'
                ' VALUES (?,?,?,?,?)',
                (str(txn_date), t_type, category, amount, note)
            )
            inserted += 1
 
    conn.commit()
    conn.close()
    print(f'Seeded {inserted} transactions across 4 months.')
 
 
if __name__ == '__main__':
    seed()
