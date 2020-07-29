from flask import render_template, redirect, flash, url_for, request
from app import app
from app.forms import UploadForm, SearchForm
from werkzeug.utils import secure_filename
import urllib.request
import os

import app.helpers as myfunctions


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
	form = UploadForm()
	if((form.validate_on_submit()) and ('submit' in request.form)):
		file = request.files['file']
		if(file.filename == ''):
			flash('No file selected for uploading')
			return redirect(request.url)

		# checking if the uploaded file extension is allowed...
		if(file and myfunctions.allowed_extension(file.filename)):
			filename = secure_filename(file.filename)
			flash('Book "{}" uploaded successfully!'.format(form.name.data))

			# converting any type of document into txt...
			if(filename.split('.')[1] != 'txt'):
				myfunctions.convert_to_text(filename)
			filename = filename.split('.')[0]

			# elasticsearch indexing...
			index = form.name.data
			myfunctions.indexing(index, filename)

		else:
			flash('Allowed file types are txt, pdf, docx')
			return redirect(request.url)

	return render_template('index.html', title='Upload', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
	form = SearchForm()
	if((form.validate_on_submit()) and ('submit' in request.form)):
		index = form.index.data
		query = form.query.data

		# keyword extraction...
		query = myfunctions.extract_keywords(query)
		print(query)

		# elasticsearch searching...
		results = myfunctions.search_documents(index, query)
		print(results)

	return render_template('search.html', title='Search', form=form)