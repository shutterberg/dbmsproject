from forms import RegistrationForm, LoginForm
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user
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

class Vehicle_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    car_num = db.Column(db.String(120), unique=True, nullable=False)                                                                    
    fuel = db.Column(db.String(120), nullable=False)
    service_date = db.Column(db.String(120))


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  name=db.Column(db.String(64), index=True, unique=True)
  number=db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), unique = True, index = True)
  password_hash = db.Column(db.String(128))
  joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)

  def __repr__(self):
    return '<User {}>'.format(self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password) 

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)   


#uncomment if running on new machine for the first time only to create db
db.create_all()



@app.route('/')
def index():
    return 'hello world'

@app.route('/home')
def home():
    return render_template('base.html')  


             

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm(csrf_enabled=False)
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
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
      next_page = url_for('index')
      return redirect(next_page) if next_page else redirect(url_for('index', _external=True, _scheme='https'))
    else:
      return redirect(url_for('login',_external=True))
  return render_template('login.html', form=form)    


@app.route('/addvehicle',methods=['GET','POST'])
def addvehicle():
    if request.method=='POST':
        car=request.form
        db.session.add(car)
        db.session.commit()
    return render_template('addcarform.html')  