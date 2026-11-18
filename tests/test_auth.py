import pytest
from app.models import User

def test_signup_and_login(client):
    # Signup
    res = client.post('/auth/signup', data={
        'name': 'Test User',
        'email': 'newuser@test.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Account created successfully' in res.data

    user = User.query.filter_by(email='newuser@test.com').first()
    assert user is not None
    assert user.check_password('SecurePassword123!')
    assert not user.check_password('WrongPassword')

def test_duplicate_email_rejected(client, user_a):
    res = client.post('/auth/signup', data={
        'name': 'Duplicate User',
        'email': 'user_a@test.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert b'already registered' in res.data

def test_unauthenticated_access_redirects(client):
    res = client.get('/transactions/', follow_redirects=False)
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']

def test_login_invalid_credentials(client, user_a):
    res = client.post('/auth/login', data={
        'email': user_a.email,
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Invalid email or password' in res.data

def test_logout(client, user_a):
    client.post('/auth/login', data={'email': user_a.email, 'password': 'Password123!'}, follow_redirects=True)
    res = client.post('/auth/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b'You have been securely logged out' in res.data

    get_res = client.get('/auth/logout')
    assert get_res.status_code == 405
