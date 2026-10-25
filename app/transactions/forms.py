from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional, Length
from app.models.transaction import CATEGORIES

CATEGORY_CHOICES = [(c, c) for c in CATEGORIES]

class TransactionForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    type = SelectField('Type', choices=[('expense', 'Expense'), ('income', 'Income')], validators=[DataRequired()])
    category = SelectField('Category', choices=CATEGORY_CHOICES, validators=[DataRequired()])
    amount = DecimalField('Amount (Rs.)', validators=[InputRequired(message='Amount is required.'), NumberRange(min=0.01, message='Amount must be greater than zero.')])
    note = StringField('Note (optional)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Transaction')

