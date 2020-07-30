from flask import render_template, redirect, flash, url_for, request, session
from app import app
from app.forms import UploadForm, SearchForm
from werkzeug.utils import secure_filename
import urllib.request
import os

import app.helpers as myfunctions

books = []

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
	books = myfunctions.get_indices()
	books = sorted(books)
	form = UploadForm()
	if((form.validate_on_submit()) and ('submit' in request.form)):
		file = request.files['file']
		if(file.filename == ''):
			print('No file selected for uploading')

		# checking if the uploaded file extension is allowed...
		elif(file and myfunctions.allowed_extension(file.filename)):
			filename = secure_filename(file.filename)
			print('Book "{}" uploaded successfully!'.format(form.name.data))

			# converting any type of document into txt...
			myfunctions.convert_to_text(filename)
			filename = filename.split('.')[0]

			# elasticsearch indexing...
			index = form.name.data
			myfunctions.index_docs(index, filename)
			books = myfunctions.get_indices()
			books = sorted(books)
			print(books)
			print('Indexing done')

		else:
			print('Allowed file types are txt, pdf, docx')

	return render_template('index.html', title='Upload', form=form, books=books)


@app.route('/search', methods=['GET', 'POST'])
def search():
	books = myfunctions.get_indices()
	books = sorted(books)
	form = SearchForm()

	print(request.args.get('index'))

	if((form.validate_on_submit()) and ('submit' in request.form)):
		index = request.args.get('index', form.index.data)
		query = form.query.data

		# keyword extraction...
		modified_query = myfunctions.extract_keywords(query)

		# elasticsearch searching...
		results = myfunctions.retrieve_docs(index, modified_query)
		time.sleep(10)

		# BERT QA
		final_answer = myfunctions.get_answer(query, results[0])
		print('hihello')
		print(final_answer)
		session['question'] = query
		session['final_answer'] = final_answer
		return redirect(url_for('answer'))


	return render_template('search.html', title='Search', form=form, books=books)


@app.route('/answer', methods=['GET', 'POST'])
def answer():
	print('Entered into answer()')
	question = ''
	answer = ''
	if 'question' in session and 'final_answer' in session:
		print("Session available")
		question = session['question']
		answer = session['final_answer']

	else:
		return redirect(url_for("search"))

	return render_template('answer.html', question=question, answer=answer)