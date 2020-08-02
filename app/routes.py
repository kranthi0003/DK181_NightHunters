from flask import render_template, redirect, flash, url_for, request, session
from app import app
from app.forms import UploadForm, SearchForm, MultiSearchForm, PPTForm
from werkzeug.utils import secure_filename
import urllib.request
import os
import time

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
			filename1 = filename
			filename = filename.split('.')[0]

			# elasticsearch indexing...
			index = form.name.data
			myfunctions.index_docs(index, filename)
			books = myfunctions.get_indices()
			books = sorted(books)
			print(books)
			print('Indexing done')
			flash('Book "' + filename1 + '" uploaded successfully!', 'success')

		else:
			print('Allowed file types are txt, pdf, docx')

		return redirect(url_for('index'))

	return render_template('index.html', title='Upload', form=form, books=books)


@app.route('/search', methods=['GET', 'POST'])
def search():
	books = myfunctions.get_indices()
	books = sorted(books)
	form = SearchForm()
	res = ''

	print(request.args.get('index'))

	if((form.validate_on_submit()) and ('submit' in request.form)):
		print("form validated")
		index = request.args.get('index', form.index.data)
		query = form.query.data

		# keyword extraction...
		modified_query = myfunctions.extract_keywords(query)

		# elasticsearch searching...
		results = myfunctions.retrieve_docs(index, modified_query)
		time.sleep(5)

		res = results

		'''
		if(form.types.data == 'sa'):
			res = myfunctions.get_answer(query, results[0])
		else:
			res = results[0]
		'''
		

		# BERT QA
		'''
		print('Choose one.\n1. Short answer\n2. Long answer\n')
		x = int(input())
		if(x==1):
			print('Answer:',bertqa.answer(qsn, l[0]),end='\n\n')
		elif(x==2):
			print('Answer:',l[0],'\n\n')
		'''

	return render_template('search.html', title='Search', form=form, books=books, res=res)


@app.route('/multisearch', methods=['GET', 'POST'])
def multisearch():
	form = MultiSearchForm()
	books = myfunctions.get_indices()
	books = sorted(books)

	books_list = [(i, books[i]) for i in range(len(books))]
	print(books_list)

	d = {}
	for x in books_list:
		d[x[0]] = x[1]

	form.books.choices = books_list
	
	#selected_books = form.books.data
	res = []

	if((form.validate_on_submit()) and ('submit' in request.form)):
		sel_books = form.books.data
		selected_books = []
		for x in sel_books:
			selected_books.append(d[x])

		print(form.books.data)
		print(selected_books)
		query = form.query.data
		modified_query = myfunctions.extract_keywords(query)

		answers = myfunctions.multi_retrieve(selected_books, modified_query)
		
		for ans in answers:
			res.append(ans[0])

		'''
		if(form.types.data == 'sa'):
			for ans in answers:
				res.append(myfunctions.get_answer(query, ans[0]))
		else:
			for ans in answers:
				res.append(ans[0])
		'''
		

	return render_template('multisearch.html', title='Search', form=form, books=books, res=res)


@app.route('/generateppt', methods=['GET', 'POST'])
def generateppt():
	books = myfunctions.get_indices()
	books = sorted(books)
	form = PPTForm()

	if((form.validate_on_submit()) and ('submit' in request.form)):
		index = form.index.data
		topic = form.topic.data
		results = myfunctions.retrieve_docs(index, topic)

		print(results)

		slides = []
		for res in results:
			slides.append(myfunctions.get_summary(res))

		print(slides)

	return render_template('generateppt.html', form=form, books=books)