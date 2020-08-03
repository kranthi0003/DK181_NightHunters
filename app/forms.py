from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, SelectField, TextAreaField, SelectMultipleField, PasswordField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Email, Length

class UploadForm(FlaskForm):
	name = StringField('Name', validators=[InputRequired()])
	file = FileField()
	submit = SubmitField('Submit')


class SearchForm(FlaskForm):
	index = StringField('Name of the Book', validators=[InputRequired()])
	query = StringField('Question', validators=[InputRequired()])
	types = SelectField('Select', choices=[('sa','Short Answer'),('la', 'Long Answer')])
	submit = SubmitField('Search')

class MultiSearchForm(FlaskForm):
	books = SelectMultipleField('Select Books', coerce=int)
	query = StringField('Question', validators=[InputRequired()])
	types = SelectField('Select', choices=[('sa','Short Answer'),('la', 'Long Answer')])
	submit = SubmitField('Search')

class PPTForm(FlaskForm):
	index = StringField('Name of the Book', validators=[InputRequired()])
	topic = StringField('Enter a topic', validators=[InputRequired()])
	submit = SubmitField('Generate PPT')

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=2, max=80)])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=2, max=80)])
	submit = SubmitField('Signup')