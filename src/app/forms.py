from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, HiddenField, validators
from wtforms.validators import DataRequired

username_validator = validators.Regexp('^[a-zA-Z0-9\._]*$', message="Username can only contain: a-Z, 0-9, . and _.")
search_validator = validators.Regexp('^[a-zA-Z0-9\. ]*$', message="Search contains invalid characters.")
distance_validator = validators.Regexp('^([0-9][0-9]?km|)$', message="Distance is invalid.")
 

class SearchForm(Form):
    search_terms = StringField("search_terms", validators=[search_validator, validators.Length(max=100, message="Search too long."), DataRequired()])
    location = StringField("location", validators=[DataRequired()])
    distance = StringField("distance", validators=[distance_validator])
    category = StringField("category", validators=[search_validator])

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), username_validator, validators.Length(min=4, max=25)])
    password = PasswordField('password', validators=[DataRequired(), validators.Length(min=6, max=35)])
    remember_me = BooleanField('remember_me', default=False)


class SignupForm(Form):
    username = StringField('username', validators=[DataRequired(), username_validator, validators.Length(min=4, max=25)])
    password = PasswordField('password', validators=[DataRequired(), validators.Length(min=6, max=35),
                                                     validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    email = StringField('email', validators=[DataRequired(), validators.Length(min=4, max=25),
                                             validators.Email(message="Invalid Email")])
