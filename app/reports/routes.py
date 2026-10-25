from datetime import datetime
from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
from app.models import Transaction, CATEGORIES
from charts import make_pie_chart, make_bar_chart

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # Query scoped to current user
    txns = Transaction.query.filter_by(user_id=current_user.id).all()

    # Month specific totals
    month_income = sum(float(t.amount) for t in txns if t.type == 'income' and t.date.startswith(selected_month))
    month_expense = sum(float(t.amount) for t in txns if t.type == 'expense' and t.date.startswith(selected_month))
    balance = month_income - month_expense

    # Category breakdown for selected month
    cat_totals = {}
    for t in txns:
        if t.type == 'expense' and t.date.startswith(selected_month):
            cat_totals[t.category] = cat_totals.get(t.category, 0.0) + float(t.amount)

    sorted_cat = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
    categories = [c[0] for c in sorted_cat]
    amounts = [c[1] for c in sorted_cat]

    # Last 6 months trend
    months_dict = {}
    for t in txns:
        m = t.date[:7]
        if m not in months_dict:
            months_dict[m] = {'inc': 0.0, 'exp': 0.0}
        if t.type == 'income':
            months_dict[m]['inc'] += float(t.amount)
        else:
            months_dict[m]['exp'] += float(t.amount)

    sorted_months = sorted(months_dict.keys())[-6:]
    trend_months = sorted_months
    trend_incomes = [months_dict[m]['inc'] for m in sorted_months]
    trend_expenses = [months_dict[m]['exp'] for m in sorted_months]

    pie_chart = make_pie_chart(categories, amounts)
    bar_chart = make_bar_chart(trend_months, trend_incomes, trend_expenses)

    totals = {
        'total_income': month_income,
        'total_expense': month_expense
    }

    return render_template('reports/summary.html',
                           totals=totals,
                           selected_month=selected_month,
                           pie_chart=pie_chart,
                           bar_chart=bar_chart,
                           balance=balance,
                           total_income=month_income,
                           total_expense=month_expense,
                           categories=categories,
                           amounts=amounts)
