"""
demo_seed.py - Safe, idempotent demonstration data seeder for Smart Spend.

Usage:
    python demo_seed.py

Demo Credentials:
    Email: demo@test.com
    Password: demo123

Security & Safety:
    - Never seeds production databases (refuses FLASK_CONFIG=production or remote PostgreSQL unless explicitly overridden).
    - Idempotent: Never duplicates data on repeated runs.
    - Safe: Never deletes existing transactions or resets existing user passwords.
"""

import os
import sys
from datetime import date
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Transaction, CATEGORIES

DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "demo123"
DEMO_NAME = "Demo User"

# Deterministic, realistic seed data covering 4 distinct months
# (date, type, category, amount, note)
DETERMINISTIC_TRANSACTIONS = [
    # Month 1: 2026-07
    ("2026-07-01", "income",  "Salary",        "28000.00", "Monthly salary credit"),
    ("2026-07-02", "expense", "Rent",          "8500.00",  "Apartment rent July"),
    ("2026-07-04", "expense", "Food",          "650.00",   "Grocery store essentials"),
    ("2026-07-07", "expense", "Transport",     "220.00",   "Metro smart card recharge"),
    ("2026-07-10", "expense", "Entertainment", "450.00",   "Weekend cinema ticket"),
    ("2026-07-14", "expense", "Food",          "380.00",   "Dinner at food court"),
    ("2026-07-18", "expense", "Health",        "350.00",   "Pharmacy vitamins"),
    ("2026-07-22", "income",  "Other",         "1500.00",  "Freelance consulting"),
    ("2026-07-25", "expense", "Food",          "520.00",   "Supermarket groceries"),
    ("2026-07-28", "expense", "Transport",     "180.00",   "Cab fare to station"),

    # Month 2: 2026-08
    ("2026-08-01", "income",  "Salary",        "28000.00", "Monthly salary credit"),
    ("2026-08-02", "expense", "Rent",          "8500.00",  "Apartment rent August"),
    ("2026-08-05", "expense", "Food",          "720.00",   "Weekly groceries & vegetables"),
    ("2026-08-08", "expense", "Transport",     "300.00",   "Fuel refill for bike"),
    ("2026-08-12", "expense", "Entertainment", "699.00",   "Streaming services annual renewal"),
    ("2026-08-15", "expense", "Food",          "410.00",   "Independence Day lunch outing"),
    ("2026-08-19", "expense", "Health",        "500.00",   "Dental checkup"),
    ("2026-08-23", "income",  "Other",         "2200.00",  "Sold unused electronics"),
    ("2026-08-26", "expense", "Food",          "610.00",   "Fresh fruits and provisions"),
    ("2026-08-29", "expense", "Transport",     "150.00",   "Auto rickshaw fares"),

    # Month 3: 2026-09
    ("2026-09-01", "income",  "Salary",        "28000.00", "Monthly salary credit"),
    ("2026-09-02", "expense", "Rent",          "8500.00",  "Apartment rent September"),
    ("2026-09-05", "expense", "Food",          "800.00",   "Department store grocery haul"),
    ("2026-09-09", "expense", "Transport",     "250.00",   "Metro commute pass"),
    ("2026-09-13", "expense", "Entertainment", "550.00",   "Concert ticket with colleagues"),
    ("2026-09-17", "expense", "Food",          "480.00",   "Team weekend lunch"),
    ("2026-09-20", "expense", "Health",        "280.00",   "First aid kit & medicines"),
    ("2026-09-24", "expense", "Food",          "640.00",   "Weekly food essentials"),
    ("2026-09-27", "income",  "Other",         "1800.00",  "Quarterly dividend payout"),
    ("2026-09-30", "expense", "Transport",     "210.00",   "Intercity bus ticket"),

    # Month 4: 2026-10
    ("2026-10-01", "income",  "Salary",        "28000.00", "Monthly salary credit"),
    ("2026-10-02", "expense", "Rent",          "8500.00",  "Apartment rent October"),
    ("2026-10-04", "expense", "Food",          "750.00",   "Festival grocery shopping"),
    ("2026-10-07", "expense", "Transport",     "240.00",   "Metro travel recharge"),
    ("2026-10-10", "expense", "Entertainment", "600.00",   "Book purchase & cafe coffee"),
    ("2026-10-14", "expense", "Food",          "510.00",   "Dinner takeaway"),
    ("2026-10-17", "expense", "Health",        "420.00",   "Health supplement & clinic visit"),
    ("2026-10-20", "expense", "Food",          "680.00",   "Vegetables & organic dairy"),
    ("2026-10-22", "income",  "Other",         "2500.00",  "Freelance project milestone"),
    ("2026-10-25", "expense", "Transport",     "190.00",   "City travel taxi"),
]

def seed_demo_data(app=None):
    """
    Seeds demo user and deterministic transactions safely and idempotently.
    Returns a dict with summary results.
    """
    if app is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
        app = create_app(config_name)

    with app.app_context():
        # Safeguard 1: Block seeding in production
        config_name = os.environ.get('FLASK_CONFIG', 'development')
        if config_name == 'production' or app.config.get('TESTING') is False and app.config.get('DEBUG') is False:
            if not os.environ.get('ALLOW_PROD_SEED', '').lower() == 'true':
                raise RuntimeError("Refused to seed: Running in non-development/production mode. Set ALLOW_PROD_SEED=true to override.")

        # Safeguard 2: Check database URL for non-local PostgreSQL
        db_uri = str(db.engine.url)
        if 'postgresql' in db_uri and not os.environ.get('ALLOW_PROD_SEED', '').lower() == 'true':
            raise RuntimeError("Refused to seed: Remote/PostgreSQL database detected without ALLOW_PROD_SEED=true.")

        try:
            # Check or create demo user
            user = User.query.filter_by(email=DEMO_EMAIL).first()
            user_created = False
            if not user:
                user = User(name=DEMO_NAME, email=DEMO_EMAIL)
                user.set_password(DEMO_PASSWORD)
                db.session.add(user)
                db.session.flush()
                user_created = True
                user_status = "Created new demo user account"
            else:
                user_status = "Using existing demo user account (password preserved)"

            # Query existing demo user transactions to prevent duplicate records
            existing_txns = Transaction.query.filter_by(user_id=user.id).all()
            existing_signatures = set(
                (t.date, t.type, t.category, f"{float(t.amount):.2f}", (t.note or "").strip())
                for t in existing_txns
            )

            created_count = 0
            for date_str, txn_type, category, amount_str, note in DETERMINISTIC_TRANSACTIONS:
                # Validation checks
                if category not in CATEGORIES:
                    continue
                if txn_type not in ('income', 'expense'):
                    continue

                sig = (date_str, txn_type, category, f"{float(amount_str):.2f}", note.strip())
                if sig in existing_signatures:
                    continue  # Idempotent skip

                txn = Transaction(
                    user_id=user.id,
                    date=date_str,
                    type=txn_type,
                    category=category,
                    amount=Decimal(amount_str),
                    note=note
                )
                db.session.add(txn)
                existing_signatures.add(sig)
                created_count += 1

            db.session.commit()

            # Calculate date range
            dates = [t[0] for t in DETERMINISTIC_TRANSACTIONS]
            date_range = f"{min(dates)} to {max(dates)}"

            result = {
                "success": True,
                "user_created": user_created,
                "user_status": user_status,
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD,
                "transactions_created": created_count,
                "total_demo_transactions": len(DETERMINISTIC_TRANSACTIONS),
                "date_range": date_range
            }
            return result

        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Demo seeding failed with rollback: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("Smart Spend - Demo Data Seeder")
    print("=" * 60)
    try:
        res = seed_demo_data()
        print(f"Status:       {res['user_status']}")
        print(f"Demo Account: {res['email']} (Password: {res['password']})")
        print(f"New Records:  {res['transactions_created']} transactions created")
        print(f"Total Spec:   {res['total_demo_transactions']} transactions in specification")
        print(f"Date Span:    {res['date_range']} (4 distinct months)")
        print("\nHow to Log In:")
        print("  1. Start the app: python run.py")
        print("  2. Open http://127.0.0.1:5000/auth/login")
        print(f"  3. Sign in with {res['email']} / {res['password']}")
        print("\n[NOTE] This demo account is intended strictly for local development and interviews.")
        print("=" * 60)
    except Exception as err:
        print(f"ERROR: {err}")
        sys.exit(1)
