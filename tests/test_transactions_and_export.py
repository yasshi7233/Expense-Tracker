import io
from datetime import date
from decimal import Decimal
from app.extensions import db
from app.models import Transaction

def test_transactions_add_and_list(client, user_a):
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)
    
    # Add income
    res = client.post('/transactions/add', data={
        'date': '2026-10-01',
        'type': 'income',
        'category': 'Salary',
        'amount': '15000.00',
        'note': 'Test Stipend'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Test Stipend' in res.data

    # Add expense
    res = client.post('/transactions/add', data={
        'date': '2026-10-02',
        'type': 'expense',
        'category': 'Food',
        'amount': '350.00',
        'note': 'Canteen lunch'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Canteen lunch' in res.data

def test_csv_export_format_and_security(client, user_a):
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)
    
    # Injection test note: =cmd|' /C calc'!A0
    client.post('/transactions/add', data={
        'date': '2026-10-03',
        'type': 'expense',
        'category': 'Other',
        'amount': '100.00',
        'note': '=1+2'
    }, follow_redirects=True)

    res = client.get('/transactions/export')
    assert res.status_code == 200
    assert res.headers['Content-Type'].startswith('text/csv')
    csv_text = res.data.decode('utf-8')
    assert 'ID,Date,Type,Category,Amount,Note' in csv_text
    # Cell sanitization check: formula should be prefixed with single quote
    assert "'=1+2" in csv_text

def test_csv_export_user_data_isolation(client, user_a, user_b):
    # Add transaction for User A
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)
    client.post('/transactions/add', data={
        'date': '2026-10-03',
        'type': 'expense',
        'category': 'Food',
        'amount': '750.00',
        'note': 'Secret User A Dinner'
    }, follow_redirects=True)
    client.post('/auth/logout', follow_redirects=True)

    # Log in as User B and export CSV
    client.post('/auth/login', data={'email': user_b.email, 'password': 'Password123!'}, follow_redirects=True)
    res_b = client.get('/transactions/export')
    assert res_b.status_code == 200
    csv_b = res_b.data.decode('utf-8')
    # Must NOT include User A's transaction
    assert 'Secret User A Dinner' not in csv_b
    assert '750.00' not in csv_b

def test_transactions_edit_and_delete(client, user_a):
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)

    # 1. Add
    client.post('/transactions/add', data={
        'date': '2026-10-04',
        'type': 'expense',
        'category': 'Food',
        'amount': '200.00',
        'note': 'Snacks'
    }, follow_redirects=True)

    txn = Transaction.query.filter_by(user_id=user_a.id, note='Snacks').first()
    assert txn is not None

    # 2. Edit
    res_edit = client.post(f'/transactions/edit/{txn.id}', data={
        'date': '2026-10-04',
        'type': 'expense',
        'category': 'Food',
        'amount': '250.00',
        'note': 'Snacks and juice'
    }, follow_redirects=True)
    assert res_edit.status_code == 200
    db.session.refresh(txn)
    assert txn.amount == Decimal('250.00')
    assert txn.note == 'Snacks and juice'

    # 3. Delete
    res_del = client.post(f'/transactions/delete/{txn.id}', follow_redirects=True)
    assert res_del.status_code == 200
    deleted_txn = db.session.get(Transaction, txn.id)
    assert deleted_txn is None
