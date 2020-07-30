from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired

class UploadForm(FlaskForm):
	name = StringField('Name/Index', validators=[InputRequired()])
	file = FileField()
	submit = SubmitField('Submit')


class SearchForm(FlaskForm):
	index = StringField('Name of the Book', validators=[InputRequired()])
	query = StringField('Question', validators=[InputRequired()])
	types = SelectField('Select', choices=[('sa','Short Answer'),('la', 'Long Answer')])
	submit = SubmitField('Search')
	answer = StringField('Answer', default='Nothing')
