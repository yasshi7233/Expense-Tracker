from datetime import datetime, timezone
from app.extensions import db

CATEGORIES = ['Food', 'Transport', 'Rent', 'Salary', 'Entertainment', 'Health', 'Other']

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    date = db.Column(db.String(10), nullable=False, index=True) # YYYY-MM-DD
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    note = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.CheckConstraint("type IN ('income', 'expense')", name='check_valid_type'),
        db.CheckConstraint("amount > 0", name='check_positive_amount'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date,
            'type': self.type,
            'category': self.category,
            'amount': float(self.amount),
            'note': self.note
        }
