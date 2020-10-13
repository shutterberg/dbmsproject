from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  name=StringField('Name', validators=[DataRequired()])
  number=IntegerField('Number', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')    

class LoginForm(FlaskForm):
  email = StringField('Email',validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')  
  
class NewvDetails(FlaskForm):
  company=StringField('Company', validators=[DataRequired()])
  chasis=IntegerField('Chasis', validators=[DataRequired()])
  color = StringField('Color', validators=[DataRequired()])
  car_num = StringField('Car NUmber', validators=[DataRequired()])
  fuel=StringField('Fuel', validators=[DataRequired()])
  submit = SubmitField('Add Car')

class StatusForm(FlaskForm):
  orderid=StringField('Order ID', validators=[DataRequired()])
  submit = SubmitField('Check Status')
        
