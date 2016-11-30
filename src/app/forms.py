from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, HiddenField, validators
from wtforms.validators import DataRequired

alphanum_validator = validators.Regexp('^[a-zA-Z0-9]*$', message="username must be alphanumeric")
 
class SearchForm(Form):
    search_terms = StringField("search_terms", validators=[DataRequired()])
    location = StringField("location", validators=[DataRequired()])

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), alphanum_validator, validators.Length(min=4, max=25)])
    password = PasswordField('password', validators=[DataRequired(), validators.Length(min=6, max=35)])
    remember_me = BooleanField('remember_me', default=False)


class SignupForm(Form):
    username = StringField('username', validators=[DataRequired(), alphanum_validator, validators.Length(min=4, max=25)])
    password = PasswordField('password', validators=[DataRequired(), validators.Length(min=6, max=35),
                                                     validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    email = StringField('email', validators=[DataRequired(), validators.Length(min=4, max=25),
                                             validators.Email(message="Invalid Email")])
