from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, HiddenField, validators
from wtforms.validators import DataRequired
 
class SearchForm(Form):
    search_terms = StringField("search_terms", validators=[DataRequired()])
    location = StringField("location", validators=[DataRequired()])
