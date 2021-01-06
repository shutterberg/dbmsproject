from forms import  StatusForm, LoginForm, RegistrationForm, NewvDetails
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy, event
from sqlalchemy.engine import Engine
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo


app=Flask(__name__)
app.config["SECRET_KEY"] = "mysecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


#login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@event.listens_for(Engine,"connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor=dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()

class Vehicle_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(80), unique=False, nullable=False)
    chasis= db.Column(db.String(80), unique=False, nullable=False)
    color = db.Column(db.String(80), unique=False, nullable=False)
    car_num = db.Column(db.String(120), unique=True, nullable=False)                                                                    
    fuel = db.Column(db.String(120), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    
class Book_service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(), default = datetime.date, nullable=False)
    slot= db.Column(db.String(80), unique=False, nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))    
    veh_num=db.Column(db.String(80))
    bksrv=db.relationship('Status',backref='owner',lazy='select') 
    his=db.relationship('Historylog',backref='owner',lazy='select')

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  name=db.Column(db.String(64))
  number=db.Column(db.Integer, unique=True)
  email = db.Column(db.String(120), unique = True, index = True)
  password_hash = db.Column(db.String(128))
  joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)
  veh=db.relationship('Vehicle_details',backref='owner',lazy='select')
  ser=db.relationship('Book_service',backref='owner',lazy='select')
  

  def __repr__(self): 
    return '<User {}>'.format(self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password) 

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)   

class Historylog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(), default = datetime.date, nullable=False)
    slot= db.Column(db.String(80), unique=False, nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey('book_service.id'))    
    veh_num=db.Column(db.String(80))
    state=db.Column(db.String(80),default="booked")
    


class Status(db.Model):
  id = db.Column(db.Integer, primary_key=True) 
  booked=db.Column(db.String(64)) 
  started=db.Column(db.String(64)) 
  wash=db.Column(db.String(64))
  wheelcare=db.Column(db.String(64))  
  checkup=db.Column(db.String(64))
  bk_id=db.Column(db.Integer,db.ForeignKey('book_service.id'))
#uncomment if running on new machine for the first time only to create db
db.create_all()



@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/home')
def home():
    return render_template('homepage.html')  


@login_manager.user_loader
def load_user(user_id):
  return User.get(user_id)             

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm(csrf_enabled=False)
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data, name=form.name.data, number=form.number.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
  return render_template('register.html', title='Register', form=form)    

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# login route
@app.route('/login', methods=['GET','POST'])
def login():
  form = LoginForm(csrf_enabled=False)
  if form.validate_on_submit():
    # query User here:
    user = User.query.filter_by(email=form.email.data).first()
    # check if a user was found and the form password matches here:
    if user and user.check_password(form.password.data):
      # login user here:
      flash('login success')
      login_user(user, remember=form.remember.data)
      render_template('base.html',current_user=user)
      next_page = url_for('home')
      return redirect(next_page) if next_page else redirect(url_for('index', _external=True, _scheme='https'))
    else:
      return redirect(url_for('login',_external=True))
  return render_template('login.html', form=form)    


@app.route('/addvehicle',methods=['GET','POST'])
@login_required
def addvehicle():
  form = NewvDetails(csrf_enabled=False)
  if form.validate_on_submit():
    new_vehicle = Vehicle_details(company=form.company.data,chasis=form.chasis.data,color=form.color.data,car_num=form.car_num.data,fuel=form.fuel.data,owner=current_user)
    db.session.add(new_vehicle)
    db.session.commit() 
  return render_template('addnewvehicle.html', form=form)


@app.route('/bookservice',methods=['GET','POST'])
@login_required
def bookservice():
  details=Vehicle_details.query.filter_by(user_id=current_user.id).all()
  if request.method == 'POST':
    form=request.form
    new_booking = Book_service(date=form['date'],slot=form['slot'],veh_num=form['carnum'],owner=current_user)
    db.session.add(new_booking)
    db.session.commit()
    status=Status(booked=0, started=0, wash=0,wheelcare= 0, checkup=0, owner=new_booking) 
    db.session.add(status)
    db.session.commit()
    new_log = Historylog(date=form['date'],slot=form['slot'],veh_num=form['carnum'],owner=new_booking)
    db.session.add(new_log)
    db.session.commit() 
  return render_template('bookservice.html',details=details)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))    


@app.route('/status', methods=['GET','POST'])
@login_required
def status():
  form = StatusForm(csrf_enabled=False)
  if form.validate_on_submit():
    # query bookid here:
    st = Status.query.filter_by(bk_id=form.orderid.data)
    if not st is None:
      # login user here:
      ids=['booked','started','wash','wheelcare','checkup']
      flash('Valid id')
      return render_template('display_details.html',cur_status=st,ids=ids)
    else:
      flash('Invalid id')
      return redirect(url_for('status',_external=True))
  return render_template('status.html', form=form)    


@app.route('/servicelog',methods=['GET','POST'])
def service():
  details=Book_service.query.all()
  if request.method == 'POST':
    form=request.form
    details=Book_service.query.filter_by(date=form['date']).all()
    return render_template('display_orders.html',details=details) 
  return render_template('search_orders.html')  


@app.route('/rescheduleservice',methods=['GET','POST'])
@login_required
def rescheduleservice():
  order_details=Book_service.query.filter_by(user_id=current_user.id).all()
  details=Vehicle_details.query.filter_by(user_id=current_user.id).all()
  if request.method == 'POST':
    form=request.form
    new_details=Book_service.query.filter_by(id=form['order_num']).first()
    print("SELFPRINT:\t",form['order_num'])
    print("SELFPRINT:\t",type(form['order_num']))
    print("SELFPRINT:\t",new_details)
    new_details.date=form['date']
    new_details.slot=form['slot']
    print("SELFPRINT:\t Update done")
    
    db.session.commit()
     
  return render_template('bookreservice.html',order_details=order_details)

@app.route('/canceleservice',methods=['GET','POST'])
@login_required
def cancelservice():
  order_details=Book_service.query.filter_by(user_id=current_user.id).all()
  if request.method == 'POST':
    form=request.form
    history_details=Historylog.query.filter_by(id=form['order_num'],state='Booked').first()
    if not history_details is None:
      history_details.state='Canceled'
    new_details=Book_service.query.filter_by(id=form['order_num']).first()
    db.session.delete(new_details)
    render_template('cancelservice.html',order_details=order_details)
    print("SELFPRINT:\t Delete done")
    
    db.session.commit()
     
  return render_template('cancelservice.html',order_details=order_details)

@app.route('/historylog',methods=['GET','POST'])
def historylog():
  details=Historylog.query.all()
  return render_template('display_hlog.html',details=details) 
    
