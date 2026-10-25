import os
import sys
from datetime import date, timedelta
import random
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Transaction

transactions_seed = [
    ('income',  'Salary',        (20000, 25000), 'Monthly salary stipend'),
    ('expense', 'Rent',          (8000,  8000),  'Hostel / Flat rent'),
    ('expense', 'Food',          (150,   700),   'Mess / Canteen / Swiggy'),
    ('expense', 'Transport',     (50,    250),   'Metro / Auto recharge'),
    ('expense', 'Entertainment', (100,   500),   'Weekend movie / steam game'),
    ('expense', 'Health',        (200,   1200),  'Medicine / clinic visit'),
    ('income',  'Other',         (500,   2500),  'Freelance project / family allowance'),
]

def seed_dev_data(email="demo@student.edu", password="Password123!"):
    app = create_app('development')
    with app.app_context():
        # Safeguard: Prevent wiping production PostgreSQL databases accidentally
        db_uri = str(db.engine.url)
        if 'postgresql' in db_uri and not os.environ.get('ALLOW_PROD_SEED', '').lower() == 'true':
            print("Aborted: Seeding is blocked on non-local database for safety. Set ALLOW_PROD_SEED=true to override.")
            return

        db.create_all()

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name="Alex Sharma", email=email, emergency_fund_target=Decimal('5000.00'))
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Created demo student account: {email} (Password: {password})")
        else:
            print(f"Using existing user: {email}")

        # Add transactions across last 3 months
        today = date.today()
        inserted = 0
        for month_offset in range(3):
            # Compute month base date
            first_of_month = (today.replace(day=1) - timedelta(days=month_offset * 30))

            # Monthly stipend on the 1st
            txn_date = first_of_month.replace(day=1)
            t_sal = Transaction(user_id=user.id, date=str(txn_date), type='income', category='Salary', amount=Decimal('22000.00'), note='Monthly internship stipend')
            db.session.add(t_sal)
            inserted += 1

            for _ in range(random.randint(6, 10)):
                t_type, category, (lo, hi), note = random.choice(transactions_seed)
                day_offset = random.randint(1, 27)
                txn_date = first_of_month.replace(day=day_offset)
                amount = Decimal(str(round(random.uniform(lo, hi) / 10) * 10))

                t = Transaction(user_id=user.id, date=str(txn_date), type=t_type, category=category, amount=amount, note=note)
                db.session.add(t)
                inserted += 1

        db.session.commit()
        print(f"Seeding completed successfully! Inserted {inserted} transactions.")

if __name__ == '__main__':
    seed_dev_data()
