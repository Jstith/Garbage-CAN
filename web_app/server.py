# Imports
import os, random
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, cast
from flask_session import Session

import can
from can import Message
# Used for relative paths
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask Initialization
app = Flask(__name__)
app.secret_key = 'letsgooo'

# Database Initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../database.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Search filter statuses
search_state = {"message_desc":True,"can_interface":True,"arb_id":True,"data_string":True,"id":True}

# Dabatase Class
class info(db.Model): #maps to a table    
    #specify the columns
    id = db.Column(db.Integer,primary_key=True)
    message_desc = db.Column(db.String(50)) # db.String(<characters>)
    can_interface = db.Column(db.String(25))
    arb_id = db.Column(db.Integer) 
    data_string = db.Column(db.Integer)
    notes = db.Column(db.String(750))

    def __init__(self, _primary_key:int,_message_desc:str,_can_interface:str,_arb_id:int,_data_string:int,_notes:str):
        self.primary_key=_primary_key
        self.message_desc=_message_desc
        self.can_interface =_can_interface
        self.arb_id=_arb_id
        self.data_string=_data_string
        self.notes=_notes

    @staticmethod
    def insert(_primary_key,_message_desc,_can_interface,_arb_id,_data_string,_notes):
        newInfo = info(_primary_key,_message_desc,_can_interface,_arb_id,_data_string,_notes)
        db.session.add(newInfo)
        db.session.commit()


class interfaces(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50))
	bitrate = db.Column(db.Integer)
	data_bitrate = db.Column(db.Integer)
	can_type = db.Column(db.Boolean)
	# shtutadown = db.Column(db.Boolean)

# Random choice for login quips
random.seed(os.urandom(5))
login_lines = open(os.path.join(basedir, 'static/txt/login_sayings.txt')).readlines()

# Default route, redirects to login
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

# To view list of all messages
@app.route('/table', methods=['GET'])
def table():
    if("user" in session):
    
        search_string = request.args.get('search_string')
        filter_type = request.args.get('filter_type')


        if(search_string):
            print("search string")
            data = info.query.filter(or_(
            info.message_desc.contains(search_string),
            info.can_interface.contains(search_string),
            info.arb_id.contains(search_string),
            info.data_string.contains(search_string)
            ))
        else:
            print("no search string")
            search_string = ''
            data = info.query
        
        
        print(f'{type(filter_type)}')

        if(not filter_type or not filter_type in search_state):
            # filter_type doesn't exist or is invalid
            data = data.order_by(info.message_desc.asc()).all()
            return render_template('table.html', data=data, search_string=search_string, sort_col='message_desc', sort_direction=0)
        
        elif(filter_type == 'message_desc'):
            if(search_state['message_desc']):
                data = data.order_by(info.message_desc.asc()).all()
            else:
                data = data.order_by(info.message_desc.desc()).all()
            search_state['message_desc'] = not search_state['message_desc']

        elif(filter_type == 'can_interface'):
            if(search_state['can_interface']):
                data = data.order_by(info.can_interface.asc()).all()
            else:
                data = data.order_by(info.can_interface.desc()).all()
            search_state['can_interface'] = not search_state['can_interface']

        elif(filter_type == 'arb_id'):
            if(search_state['arb_id']):
                data = data.order_by(info.arb_id.asc()).all()
            else:
                data = data.order_by(info.arb_id.desc()).all()
            search_state['arb_id'] = not search_state['arb_id']

        elif(filter_type == 'data_string'):
            if(search_state['data_string']):
                data = data.order_by(info.data_string.asc()).all()
            else:
                data = data.order_by(info.data_string.desc()).all()
            search_state['data_string'] = not search_state['data_string']

        elif(filter_type == 'id'):
            if(search_state['id']):
                data = data.order_by(cast(info.id,db.Integer).asc()).all()
            else:
                data = data.order_by(cast(info.id,db.Integer).desc()).all()
            search_state['id'] = not search_state['id']

        return render_template('table.html', data=data, search_string=search_string, sort_col=filter_type, sort_direction=search_state[filter_type])

    else:
        return redirect(url_for('login'))

# To view and modify message
@app.route('/inspect/<id>', methods=['GET', 'POST'])
def inspect(id):
    if("user" in session):
        if(request.method == 'GET'):
            # Populate with data based on passed ID
            data = info.query.filter(info.id == id).first()
            if(not data):
                return redirect(url_for('table'))
            return render_template('inspect.html', data=data)
        else:
            # Update with POST Data
            return render_template('inspect.html')

# To add a new message
@app.route('/add',methods=['POST'])
def addToTable():
    
    try:
        _primary_key = info.query.count()
        _message_desc = request.form['new_desc']
        _can_interface = request.form['new_can']
        _arb_id = int(request.form['new_arb'], 16)
        _data_string = int(request.form['new_data'], 16)
        _notes = 'notes'
        
        info.insert(_primary_key,_message_desc,_can_interface,_arb_id,_data_string, _notes)
        return redirect(url_for('table'))
    
    except:
        return redirect(url_for('table'))
    
# To update an existing message
@app.route('/update/<id>',methods=['POST'])
def modifyEntry(id):

    builder = '/inspect/' + str(id)
    entry = info.query.filter_by(id=id).one()

    try:
        entry.notes = request.form['notes']
        db.session.commit()
        flash('Notes updated')
        return redirect(url_for('inspect',id=id))
    except: ()
    
    if(len(request.form['message_desc']) == 0):
        flash('Missing or invalid message description')
        # flash that message
        return redirect(url_for('inspect',id=id))

    entry.message_desc = request.form['message_desc']

    if(len(request.form['can_interface']) == 0):
        flash('Missing or invalid CAN Interface')
        # flash that message
        return redirect(url_for('inspect',id=id))

    entry.can_interface = request.form['can_interface']

    try:
        # Check for valid hex value
        entry.arb_id = int(request.form['arb_id'], 16)
        # Convert to decimal for storage
        #_arb_id = int(_arb_id)
    except:
        flash('Missing or invalid Arb-ID')
        # flash that message
        return redirect(url_for('inspect',id=id))

    try:
        # Check for valid hex value
        entry.data_string = int(request.form['data_string'], 16)
        # Convert to decimal for storage
        #_data_string = int(request.form['data_string'], 16)
    except:
        flash('Missing or invalid data string')
        # flash that message
        return redirect(url_for('inspect',id=id))
    
    try:
        _notes = request.form['notes']

        if(_notes):
            entry.notes = _notes
    except: ()
 
    # If everything passes the checks
    db.session.commit()
    flash('nominally updated')

    return redirect(url_for('inspect',id=id))

# To delete an existing message
@app.route('/delete/<id>',methods=['POST'])
def deleteFromTable(id):

    _primary_key = id
    # info.query.filter(info.id == _primary_key).delete()
    obj = info.query.filter_by(id = _primary_key).one()
    db.session.delete(obj)
    db.session.commit()

    return redirect(url_for('table'))

# For future use
@app.route('/send', methods=['POST'])
def send(): 
    #assume already initalized?
    
    #Get FD Status
    _can_interface = request.form['interface_place']
    _arb_id = request.form['arb_place']
    _dataString = request.form['data_place']
    _data = bytes.fromhex(_dataString)

    _arb_id = int(_arb_id,16)

    try:
        obj = interfaces.query.filter(interfaces.name.contains(_can_interface)).first() #filter for interface
        _fd_msg = obj.can_type #gather pertinant data
        _bitrate = obj.bitrate
        _data_bitrate = obj.data_bitrate
        _name = obj.name
    except:
        print("Interface not included in table.")
        return redirect(url_for('table'))


    
    if(_fd_msg==1):
        _fd_msg = True
    else:
        _fd_msg = False
  
    try:
        with can.interface.Bus(_name, bustype="socketcan",bitrate=_bitrate,data_bitrate=_data_bitrate,fd = _fd_msg) as bus:
                print("message creation start")
                msg = can.Message(
                    arbitration_id=_arb_id, data=_data, is_extended_id=False
                )
                try:
                    bus.send(msg)
                    print("Message sent.")
                    flash("Message sent.")
                except can.CanError:
                    print("Message NOT sent")
                    flash("Message not sent :(")
    except:
        print("No such device")
        flash("No such device, choose an interface that's initialised and in the database.")

    
    return redirect(url_for('table'))

@app.route('/interface')
def interface():
    data=interfaces.query
    return render_template('interface.html',data=data)

# Run
if(__name__ == '__main__'):
    #os.system('initialize.sh')
    app.run(debug=True)