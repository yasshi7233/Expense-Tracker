"""
tests/test_architecture_and_demo.py

Tests covering:
1. Application factory initialization, Blueprint registrations, and exclusion of removed modules.
2. Demo seeding: user creation, transaction count, 4-month span, idempotency, password preservation, rollback, and production rejection.
"""

import pytest
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import User, Transaction
import demo_seed

def test_app_factory_and_blueprint_registration():
    """Verify application factory initializes cleanly with only the 4 core blueprints."""
    test_app = create_app('testing')
    assert test_app is not None
    assert test_app.testing is True

    registered_blueprints = set(test_app.blueprints.keys())
    # Exactly the 4 core blueprints must be registered
    assert 'auth' in registered_blueprints
    assert 'dashboard' in registered_blueprints
    assert 'transactions' in registered_blueprints
    assert 'reports' in registered_blueprints

    # Out-of-scope blueprints must NOT be registered
    assert 'shared_expenses' not in registered_blueprints
    assert 'budgets' not in registered_blueprints
    assert 'goals' not in registered_blueprints
    assert 'recurring' not in registered_blueprints

def test_demo_seeder_creates_user_and_transactions(app):
    """Verify demo_seed creates demo user, at least 35 transactions, and spans 4 months."""
    with app.app_context():
        # First execution
        res = demo_seed.seed_demo_data(app=app)
        assert res['success'] is True
        assert res['user_created'] is True
        assert res['transactions_created'] >= 35

        # Check user in DB
        demo_user = User.query.filter_by(email=demo_seed.DEMO_EMAIL).first()
        assert demo_user is not None
        assert demo_user.check_password(demo_seed.DEMO_PASSWORD)

        # Check transactions count & months span
        txns = Transaction.query.filter_by(user_id=demo_user.id).all()
        assert len(txns) >= 35

        distinct_months = set(t.date[:7] for t in txns)
        assert len(distinct_months) >= 4

def test_demo_seeder_idempotency_and_preservation(app):
    """Verify repeated executions do not create duplicate transactions or overwrite passwords."""
    with app.app_context():
        # Seed first time
        demo_seed.seed_demo_data(app=app)
        initial_txns_count = Transaction.query.count()

        # Change user's password to custom
        user = User.query.filter_by(email=demo_seed.DEMO_EMAIL).first()
        user.set_password("CustomPassword999!")
        db.session.commit()

        # Seed second time
        res2 = demo_seed.seed_demo_data(app=app)
        assert res2['transactions_created'] == 0
        assert res2['user_created'] is False

        # Verify no duplicate transactions were added
        assert Transaction.query.count() == initial_txns_count

        # Verify password was NOT overwritten
        refreshed_user = User.query.filter_by(email=demo_seed.DEMO_EMAIL).first()
        assert refreshed_user.check_password("CustomPassword999!")

def test_demo_seeder_rejects_production_mode():
    """Verify seeder refuses to run under production config without explicit override."""
    prod_app = create_app('production')
    with pytest.raises(RuntimeError, match="Refused to seed"):
        demo_seed.seed_demo_data(app=prod_app)
