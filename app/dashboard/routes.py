from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Transaction, CATEGORIES
from charts import make_pie_chart, make_bar_chart

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('dashboard/landing.html')

    today = date.today()
    selected_month = request.args.get('month', today.strftime('%Y-%m'))
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    txns = Transaction.query.filter_by(user_id=current_user.id).all()

    # Filter transactions based on selection: explicit date range or month
    if start_date and end_date:
        period_txns = [t for t in txns if start_date <= t.date <= end_date]
        period_label = f"{start_date} to {end_date}"
    elif start_date:
        period_txns = [t for t in txns if t.date >= start_date]
        period_label = f"From {start_date}"
    elif end_date:
        period_txns = [t for t in txns if t.date <= end_date]
        period_label = f"Up to {end_date}"
    else:
        period_txns = [t for t in txns if t.date.startswith(selected_month)]
        period_label = selected_month

    total_income = sum(float(t.amount) for t in period_txns if t.type == 'income')
    total_expense = sum(float(t.amount) for t in period_txns if t.type == 'expense')
    net_savings = total_income - total_expense

    # Category breakdown for the filtered period
    cat_totals = {}
    for t in period_txns:
        if t.type == 'expense':
            cat_totals[t.category] = cat_totals.get(t.category, 0.0) + float(t.amount)

    sorted_categories = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
    cat_names = [c[0] for c in sorted_categories]
    cat_amounts = [c[1] for c in sorted_categories]

    # Monthly trends (past 6 months) from user's full transaction history
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

    # Generate charts
    pie_chart = make_pie_chart(cat_names, cat_amounts)
    bar_chart = make_bar_chart(trend_months, trend_incomes, trend_expenses)

    # Recent Transactions (last 6)
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(
        Transaction.date.desc(), Transaction.id.desc()
    ).limit(6).all()

    # Legacy unassigned transactions indicator
    has_unclaimed = Transaction.query.filter_by(user_id=None).count() > 0

    return render_template('dashboard/index.html',
                           selected_month=selected_month,
                           start_date=start_date,
                           end_date=end_date,
                           period_label=period_label,
                           total_income=total_income,
                           total_expense=total_expense,
                           net_savings=net_savings,
                           pie_chart=pie_chart,
                           bar_chart=bar_chart,
                           categories=cat_names,
                           amounts=cat_amounts,
                           recent_transactions=recent_transactions,
                           has_unclaimed=has_unclaimed)
