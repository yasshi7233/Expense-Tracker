from datetime import date
from decimal import Decimal
from app.extensions import db
from app.models import Transaction

def test_dashboard_period_filtering_and_net_savings(client, user_a):
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)

    # Oct 2026: Income 20,000, Expense 5,000 -> Net 15,000
    # Sep 2026: Income 10,000, Expense 8,000 -> Net 2,000
    t1 = Transaction(user_id=user_a.id, date='2026-10-05', type='income', category='Salary', amount=Decimal('20000.00'), note='Oct Salary')
    t2 = Transaction(user_id=user_a.id, date='2026-10-10', type='expense', category='Food', amount=Decimal('5000.00'), note='Oct Food')
    t3 = Transaction(user_id=user_a.id, date='2026-09-05', type='income', category='Salary', amount=Decimal('10000.00'), note='Sep Salary')
    t4 = Transaction(user_id=user_a.id, date='2026-09-20', type='expense', category='Rent', amount=Decimal('8000.00'), note='Sep Rent')
    db.session.add_all([t1, t2, t3, t4])
    db.session.commit()

    # 1. Filter by October 2026
    res_oct = client.get('/?month=2026-10')
    assert res_oct.status_code == 200
    assert b'20000.00' in res_oct.data
    assert b'5000.00' in res_oct.data
    assert b'15000.00' in res_oct.data

    # 2. Filter by custom date range: 2026-09-01 to 2026-09-30
    res_sep = client.get('/?start_date=2026-09-01&end_date=2026-09-30')
    assert res_sep.status_code == 200
    assert b'10000.00' in res_sep.data
    assert b'8000.00' in res_sep.data
    assert b'2000.00' in res_sep.data

    # 3. Analytics page test
    res_analytics = client.get('/reports/?month=2026-10')
    assert res_analytics.status_code == 200
    assert b'Total Income' in res_analytics.data
    assert b'Total Expense' in res_analytics.data
    assert b'Net Savings' in res_analytics.data

def test_empty_dashboard_renders_cleanly(client, user_b):
    # user_b has zero transactions
    client.post('/auth/login', data={'email': user_b.email, 'password': 'Password123!'}, follow_redirects=True)
    res = client.get('/')
    assert res.status_code == 200
    assert b'No expense data recorded' in res.data
    assert b'No transactions recorded yet' in res.data
    assert b'0.00' in res.data
