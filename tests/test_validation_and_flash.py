from decimal import Decimal
import pytest
from app.models import Transaction

def test_transaction_validation_errors(client, user_a):
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)
    
    # Missing/invalid amount
    res = client.post('/transactions/add', data={
        'date': '2026-10-01',
        'type': 'expense',
        'category': 'Food',
        'amount': '-50.00',
        'note': 'Invalid negative'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Amount must be greater than zero.' in res.data

    # Zero amount
    res_zero = client.post('/transactions/add', data={
        'date': '2026-10-01',
        'type': 'expense',
        'category': 'Food',
        'amount': '0',
        'note': 'Zero amount'
    }, follow_redirects=True)
    assert res_zero.status_code == 200
    assert b'Amount must be greater than zero.' in res_zero.data
