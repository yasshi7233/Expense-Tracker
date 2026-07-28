from flask import Flask,render_template,request,redirect,url_for
from database import get_db,init_db
from charts import make_pie_chart,make_bar_chart
from datetime import datetime
import csv
import io as stdlib_io
import os

app = Flask(__name__)
app.jinja_env.globals['zip'] = zip
CATEGORIES = ['Food','Transport','Rent','Salary','Entertainment','Health','Other']

@app.route('/')
def index():
    db = get_db()
    transactions = db.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    db.close()
    return render_template('index.html',transactions=transactions)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method =='POST':
        date = request.form['date']
        type_ = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        note = request.form.get('note','')
        db = get_db()
        db.execute('INSERT INTO transactions (date,type,category,amount,note) VALUES(?,?,?,?,?)',(date,type_,category,amount,note))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    
    return render_template('add.html',categories=CATEGORIES)

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    db = get_db()
    if request.method =='POST':
        date= request.form['date']
        type_ = request.form['type']
        category =request.form['category']
        amount =float(request.form['amount'])
        note =request.form.get('note','')
        db.execute('UPDATE transactions SET date=?, type=?,category=?,amount=?,note=? WHERE id=?',(date,type_,category,amount,note,id))

        db.commit()
        db.close()
        return redirect(url_for('index'))
    transaction =db.execute('SELECT * FROM transactions WHERE id=?',(id,)).fetchone()
    db.close()
    return render_template('edit.html',transaction = transaction,categories=CATEGORIES)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db=get_db()
    db.execute('DELETE FROM transactions WHERE id =?',(id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/summary')
def summary():
     selected_month = request.args.get(
          'month',datetime.now().strftime('%Y-%m') 
    )
     db = get_db()
     totals = db.execute('''
                         SELECT SUM(CASE WHEN type ='income' THEN amount ELSE 0  END) AS total_income,
                                SUM(CASE WHEN type ='expense' THEN amount ELSE 0  END) AS total_expense
                         FROM transactions
                         WHERE strftime('%Y-%m', date) = ?
                         ''', (selected_month,)).fetchone()
     cat_rows = db.execute('''
                           SELECT category, SUM(amount) AS total 
                           FROM transactions
                           WHERE type ='expense'
                            AND strftime('%Y-%m',date) =?
                           GROUP BY category 
                           ORDER BY total DESC
                           ''',(selected_month,)).fetchall()
     

     months_rows =db.execute('''
     SELECT strftime('%Y-%m',date) AS month,
          SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS inc,
          SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS exp
     FROM transactions
     GROUP BY month
     ORDER BY month DESC
     LIMIT 6 
    ''').fetchall()
     db.close()
    
     total_income = totals['total_income'] or 0
     total_expense = totals['total_expense'] or 0
     balance = total_income-total_expense

     categories=[r['category'] for r in cat_rows]
     amounts  = [r['total']    for r in cat_rows]
    
     months   = [r['month'] for r in reversed(months_rows)]
     incomes  = [r['inc'] for r in reversed(months_rows)]
     expenses = [r['exp'] for r in reversed(months_rows)]
	 
     pie_chart = make_pie_chart(categories, amounts)
     bar_chart = make_bar_chart(months, incomes, expenses)

     return render_template('summary.html', 
                            totals=totals, 
                            selected_month=selected_month,
                            pie_chart=pie_chart,
                            bar_chart=bar_chart,
                            balance=balance,
                            total_income=total_income,
                            total_expense=total_expense)

@app.route('/export')
def export():
     start = request.args.get('start', '')
     end = request.args.get('end', '')

     db =get_db()

     query ='SELECT * FROM transactions WHERE 1=1'
     params =[]

     if start:
          query += ' AND date >=?'
          params.append(start)

     if end:
          query += ' AND date <= ?'
          params.append(end)

     query += ' ORDER BY date DESC'

     rows = db.execute(query, params).fetchall()
     db.close()

     output = stdlib_io.StringIO()
     writer = csv.writer(output)

     writer.writerow(['ID', 'Date','Type', 'Category', 'Amount', 'Note'])

     for row in rows:
          writer.writerow([row['id'],
                           row['date'],
                           row['type'],
                           row['category'],
                           row['amount'],
                           row['note'] or ''])
          

     csv_data = output.getvalue()

     from flask import make_response
     response = make_response(csv_data)
     response.headers['Content-Type'] ='text/csv'
     response.headers['Content-Disposition'] ='attachment;filename=transactions.csv'
     return response






if __name__ =='__main__':
        init_db()
        app.run(
             host='0.0.0.0',
             port=int(os.environ.get("PORT",5000)),
             debug=False)
    
