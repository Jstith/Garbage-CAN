import os, random
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_session import Session
from sqlalchemy import insert,delete

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


    def __init__(self, _primary_key:int,_message_desc:str,_can_interface:str,_arb_id:str,_data_string:str):
        self.primary_key=_primary_key
        self.message_desc=_message_desc
        self.can_interface =_can_interface
        self.arb_id=_arb_id
        self.data_string=_data_string

    @staticmethod
    def insert(_primary_key,_message_desc,_can_interface,_arb_id,_data_string):

        newInfo = info(_primary_key,_message_desc,_can_interface,_arb_id,_data_string)
        db.session.add(newInfo)
        db.session.commit()

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
                filter_type = request.args.get('filter')
                if(filter_type == "message_desc" or not filter_type):
                    print("Here")
                    data = info.query.order_by(info.message_desc).all()
                elif(filter_type == "can_interface"):
                    data = info.query.order_by(info.can_interface.desc()).all()
                elif(filter_type == "arb_id"):
                    data = info.query.order_by(info.arb_id.desc()).all()
                elif(filter_type == "data_string"):
                    data = info.query.order_by(info.data_string.desc()).all()
                elif(filter_type == "id"):
                    data = info.query.order_by(info.can_interface.desc()).all()
                      

                return render_template('table.html', data=data, search_string='')
        else:
            # limit search results
            search_string = request.form['search_string']
            filter_type = request.form['filter_type']

            data = info.query.filter(or_(
                info.message_desc.contains(search_string),
                info.can_interface.contains(search_string),
                info.arb_id.contains(search_string),
                info.data_string.contains(search_string)
            )).order_by(info.message_desc).all()

            return render_template('table.html', data=data, search_string=search_string)
    else:
        return redirect(url_for('login'))

@app.route('/add',methods=['POST'])
def addToTable():

    _primary_key = info.query.count()
    _message_desc = request.form['message_desc']
    _can_interface = request.form['can_interface']
    _arb_id = request.form['arb_id']
    _data_string = request.form['data_string']
    if(_primary_key and _message_desc and _can_interface and _arb_id and _message_desc):
        info.insert(_primary_key,_message_desc,_can_interface,_arb_id,_data_string)
    else:
        return redirect(url_for('table'))


    return redirect(url_for('table'))

@app.route('/delete',methods=['POST'])
def deleteFromTable():

    _primary_key = request.form['primary_key'] 
    print(_primary_key)
    # info.query.filter(info.id == _primary_key).delete()
    obj = info.query.filter_by(id = _primary_key).one()
    db.session.delete(obj)
    db.session.commit()

    return redirect(url_for('table'))


@app.route('/update',methods=['POST'])
def modifyEntry():

    _primary_key = request.form['primary_key']
    _message_desc = request.form['message_desc']
    _can_interface = request.form['can_interface']
    _arb_id = request.form['arb_id']
    _data_string = request.form['data_string']

    entry = info.query.filter_by(id = _primary_key).one()

    if(_message_desc):
        entry.message_desc = _message_desc
    if(_can_interface):
        entry.can_interface = _can_interface
    if(_arb_id):
        entry.arb_id = _arb_id
    if(_data_string):
        entry.data_string = _data_string

    db.session.commit()

    return redirect(url_for('table'))

if(__name__ == '__main__'):
    app.run(debug=True)