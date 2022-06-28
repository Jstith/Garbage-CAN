import os, random
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_session import Session


basedir = os.path.abspath(os.path.dirname(__file__))
#print(f'basedir is {basedir}')

app = Flask(__name__)
app.secret_key = 'letsgooo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../database.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class info(db.Model): #maps to a table    
    #specify the columns
    id = db.Column(db.Integer,primary_key=True)
    message_desc = db.Column(db.String(50)) # db.String(<characters>)
    can_interface = db.Column(db.String(25))
    arb_id = db.Column(db.String(25)) 
    data_string = db.Column(db.String(20))

random.seed(os.urandom(5))
login_lines = open(os.path.join(basedir, 'static/txt/login_sayings.txt')).readlines()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if(request.form['username'] != 'admin' or request.form['password'] != 'password'):
            flash('Invalid Credentials. Garbage-CAN is too stronk for you.')
        else:
            session["user"] = request.form['username']
            return redirect(url_for('table'))
        return render_template('login.html')
    flash(login_lines[random.randint(0,len(login_lines)-1)])
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash('You have been logged out. Happy hacking!')
    return redirect(url_for('login'))

@app.route('/table', methods=['GET', 'POST'])
def table():
    if("user" in session):
        if(request.method == 'GET'):
            data = info.query.order_by(info.message_desc).all()
            return render_template('table.html', data=data, search_string='')
        else:
            # limit search results
            search_string = request.form['search_string']

            data = info.query.filter(or_(
                info.message_desc.contains(search_string),
                info.can_interface.contains(search_string),
                info.arb_id.contains(search_string),
                info.data_string.contains(search_string)
            )).order_by(info.message_desc).all()

            return render_template('table.html', data=data, search_string=search_string)
    else:
        return redirect(url_for('login'))

if(__name__ == '__main__'):
    app.run(debug=True)