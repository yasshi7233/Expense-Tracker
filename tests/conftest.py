import pytest
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import User, Transaction

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_a(app):
    user = User(name='User A', email='user_a@test.com', emergency_fund_target=Decimal('2000.00'))
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def user_b(app):
    user = User(name='User B', email='user_b@test.com', emergency_fund_target=Decimal('0.00'))
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user
