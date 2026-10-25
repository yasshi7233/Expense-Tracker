from datetime import datetime, date
import csv
import io as stdlib_io
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Transaction, CATEGORIES
from app.transactions.forms import TransactionForm
from app.core.security import sanitize_csv_cell

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
@login_required
def index():
    # Filtering and pagination
    search_query = request.args.get('q', '').strip()
    selected_type = request.args.get('type', '').strip()
    selected_category = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'date')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = Transaction.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter((Transaction.note.ilike(f'%{search_query}%')) | (Transaction.category.ilike(f'%{search_query}%')))
    if selected_type in ('income', 'expense'):
        query = query.filter_by(type=selected_type)
    if selected_category and selected_category in CATEGORIES:
        query = query.filter_by(category=selected_category)

    if sort_by == 'amount':
        query = query.order_by(Transaction.amount.desc() if order == 'desc' else Transaction.amount.asc())
    elif sort_by == 'category':
        query = query.order_by(Transaction.category.desc() if order == 'desc' else Transaction.category.asc())
    else:
        query = query.order_by(Transaction.date.desc() if order == 'desc' else Transaction.date.asc(), Transaction.id.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('transactions/index.html',
                           transactions=pagination.items,
                           pagination=pagination,
                           search_query=search_query,
                           selected_type=selected_type,
                           selected_category=selected_category,
                           sort_by=sort_by,
                           order=order,
                           categories=CATEGORIES)

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = TransactionForm()
    if request.method == 'GET' and not form.date.data:
        form.date.data = date.today()

    if form.validate_on_submit():
        txn = Transaction(
            user_id=current_user.id,
            date=form.date.data.strftime('%Y-%m-%d'),
            type=form.type.data,
            category=form.category.data,
            amount=Decimal(str(form.amount.data)),
            note=(form.note.data or '').strip()
        )
        db.session.add(txn)
        db.session.commit()
        flash(f'Successfully added {txn.type} of Rs. {txn.amount:.2f}!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/add.html', form=form, categories=CATEGORIES)

@transactions_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    txn = db.get_or_404(Transaction, id)
    # Authorization check
    if txn.user_id != current_user.id:
        abort(403)

    form = TransactionForm()
    if form.validate_on_submit():
        txn.date = form.date.data.strftime('%Y-%m-%d')
        txn.type = form.type.data
        txn.category = form.category.data
        txn.amount = Decimal(str(form.amount.data))
        txn.note = (form.note.data or '').strip()
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.index'))
    elif request.method == 'GET':
        form.date.data = datetime.strptime(txn.date, '%Y-%m-%d').date()
        form.type.data = txn.type
        form.category.data = txn.category
        form.amount.data = float(txn.amount)
        form.note.data = txn.note

    return render_template('transactions/edit.html', form=form, transaction=txn, categories=CATEGORIES)

@transactions_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    txn = db.get_or_404(Transaction, id)
    # Strict Authorization check
    if txn.user_id != current_user.id:
        abort(403)


    db.session.delete(txn)
    db.session.commit()
    flash('Transaction deleted successfully.', 'info')
    return redirect(url_for('transactions.index'))

@transactions_bp.route('/export')
@login_required
def export():
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()

    query = Transaction.query.filter_by(user_id=current_user.id)

    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date <= end)

    query = query.order_by(Transaction.date.desc())
    rows = query.all()

    output = stdlib_io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Type', 'Category', 'Amount', 'Note'])

    for r in rows:
        writer.writerow([
            r.id,
            sanitize_csv_cell(r.date),
            sanitize_csv_cell(r.type),
            sanitize_csv_cell(r.category),
            f"{r.amount:.2f}",
            sanitize_csv_cell(r.note or '')
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=transactions_{datetime.now().strftime("%Y%m%d")}.csv'
    return response

@transactions_bp.route('/claim-legacy', methods=['GET', 'POST'])
@login_required
def claim_legacy():
    """Allows claiming legacy unassigned transactions (from pre-auth database) into this user account."""
    unassigned = Transaction.query.filter_by(user_id=None).all()
    count = len(unassigned)
    if count == 0:
        flash('No unassigned legacy transactions found to claim.', 'info')
    else:
        for t in unassigned:
            t.user_id = current_user.id
        db.session.commit()
        flash(f'Successfully claimed {count} legacy transactions into your account!', 'success')
    return redirect(url_for('dashboard.index'))
