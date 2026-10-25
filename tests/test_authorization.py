import pytest
from decimal import Decimal
from app.extensions import db
from app.models import Transaction

def test_data_isolation_between_users(client, user_a, user_b):
    # Log in as user A and add a transaction
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)
    res = client.post('/transactions/add', data={
        'date': '2026-10-15',
        'type': 'expense',
        'category': 'Food',
        'amount': '450.00',
        'note': 'Private dinner'
    }, follow_redirects=True)
    assert res.status_code == 200

    txn_a = Transaction.query.filter_by(user_id=user_a.id).first()
    assert txn_a is not None
    assert float(txn_a.amount) == 450.00

    # Log out user A and log in as user B
    client.get('/auth/logout', follow_redirects=True)
    client.post('/auth/login', data={'email': user_b.email, 'password': 'Password123!'}, follow_redirects=True)

    # User B views transaction list -> must not see User A's transaction
    res = client.get('/transactions/')
    assert b'Private dinner' not in res.data

    # User B attempts to edit User A's transaction directly by ID -> must receive 403 Forbidden
    res_edit = client.post(f'/transactions/edit/{txn_a.id}', data={
        'date': '2026-10-15',
        'type': 'expense',
        'category': 'Food',
        'amount': '999.00',
        'note': 'Tampered'
    })
    assert res_edit.status_code == 403

    # User B attempts to delete User A's transaction -> must receive 403 Forbidden
    res_del = client.post(f'/transactions/delete/{txn_a.id}')
    assert res_del.status_code == 403

    # Transaction must remain unchanged in DB
    refreshed = db.session.get(Transaction, txn_a.id)
    assert refreshed.note == 'Private dinner'
    assert float(refreshed.amount) == 450.00

