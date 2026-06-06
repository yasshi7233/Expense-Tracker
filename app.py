from flask import Flask,render_template,request,redirect,url_for
from database import get_db,init_db

app = Flask(__name__)
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
        db.execute('UPDATE transactions SET date=?, type=?,category=?,amount=?,note=? WHERE id=?',(adte,type_,category,amount,note,id))

        db.commit()
        db.close()
        return redirect(url_for('index'))
        transaction =db.execute('SELECT * FROM transactions WHERE id=?',(id,)).fetchone()
        db.close()
        return render_template('edit.html',transactions = transaction,categories=CATEGORIES)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
        db=get_db()
        db.execute('DELETE FROM transactions WHERE id =?',(id,))
        db.commit()
        db.close()
        return redirect(url_for('index'))


if __name__ =='__main__':
        init_db()
        app.run(debug=True)
    
