from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email=StringField("Email",validators=[InputRequired(), Length(min=5, max=50)])
    first_name=StringField("First Name",validators=[InputRequired(), Length(min= 2, max=30)])
    last_name=StringField("Last Name",validators=[InputRequired(),Length(min= 2, max=30)])

class UserLogin(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class TweetForm(FlaskForm):
    text = StringField("Tweet Text", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title=StringField("Title",validators=[InputRequired(), Length(min=1, max=100)])
    content=TextAreaField("Your feedback:",validators=[InputRequired()])
    
