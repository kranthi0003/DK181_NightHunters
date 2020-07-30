from flask import render_template, redirect, flash, url_for, request, session
from app import app
from app.forms import UploadForm, SearchForm
from werkzeug.utils import secure_filename
import urllib.request
import os
import time

import app.helpers as myfunctions

books = []
sa = None
la = None

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
	books = myfunctions.get_indices()
	form = UploadForm()
	if((form.validate_on_submit()) and ('submit' in request.form)):
		file = request.files['file']
		if(file.filename == ''):
			print('No file selected for uploading')
			#return redirect(request.url)

		# checking if the uploaded file extension is allowed...
		elif(file and myfunctions.allowed_extension(file.filename)):
			filename = secure_filename(file.filename)
			print('Book "{}" uploaded successfully!'.format(form.name.data)) #flash

			# converting any type of document into txt...
			#if(filename.split('.')[1] != 'txt'):
			myfunctions.convert_to_text(filename)
			filename = filename.split('.')[0]

			# elasticsearch indexing...
			index = form.name.data
			myfunctions.index_docs(index, filename)
			books = myfunctions.get_indices()
			print('Indexing done')

		else:
			print('Allowed file types are txt, pdf, docx') #flash
		
		return redirect(url_for('index'))

	return render_template('index.html', title='Upload', form=form, books=books)


@app.route('/search', methods=['GET', 'POST'])
def search():
	res = ''
	books = myfunctions.get_indices()
	form = SearchForm()
	print(request)
	print(request.args.get('index'))
	if((form.validate_on_submit()) and ('submit' in request.form)):
		index = request.args.get('index', form.index.data)
		query = form.query.data

		# keyword extraction...
		modified_query = myfunctions.extract_keywords(query)
		
		# elasticsearch searching...
		results = myfunctions.retrieve_docs(index, modified_query)
		time.sleep(5)
		if(form.types.data == 'sa'):
			res = myfunctions.get_answer(query, results[0])
		else:
			res = results[0]
		
		'''
		session['question'] = query
		session['answer'] = answer
		return redirect(url_for('answer'))
		'''
		'''
		print('Choose one.\n1. Short answer\n2. Long answer\n')
        x = int(input())
        if(x==1):
            print('Answer:',bertqa.answer(qsn, l[0]),end='\n\n')
        elif(x==2):
            print('Answer:',l[0],'\n\n')
		'''
	return render_template('search.html', title='Search', form=form, books=books, res=res)

'''
@app.route('/answer', methods=['GET', 'POST'])
def answer():
	print('Entered into answer')
	print(session, type(session))
	print()
	print('question' in session)
	
	print("Session available")
	if 'question' in session and 'answer' in session:
		question = session['question']
		answer = session['answer']
	
	else:
		return redirect(url_for("search"))
	
	return render_template('answer.html', question=question, answer=answer)
'''