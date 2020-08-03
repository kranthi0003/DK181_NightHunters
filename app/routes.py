from flask import render_template, redirect, flash, url_for, request, session, Flask
from app import app
from app.forms import UploadForm, SearchForm, MultiSearchForm, PPTForm, LoginForm, RegisterForm
from werkzeug.utils import secure_filename
import urllib.request
import os
import time
from . import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import app.helpers as myfunctions
from app.models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


books = []

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	username = current_user.username
	books = myfunctions.get_user_books(username)
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
			myfunctions.index_book_to_user(username, index)
			books = myfunctions.get_user_books(username)
			books = sorted(books)
			print(books)
			print('Indexing done')
			flash('Book "' + filename1 + '" uploaded successfully!', 'success')

		else:
			print('Allowed file types are txt, pdf, docx')

		return redirect(url_for('index'))

	return render_template('index.html', title='Upload', form=form, books=books, username=username)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
	username = current_user.username
	books = myfunctions.get_user_books(username)
	books = sorted(books)
	form = SearchForm()
	res = ''

	print(request.args.get('index'))

	if((form.validate_on_submit()) and ('submit' in request.form)):
		index = request.args.get('index', form.index.data)

		if index not in books:
			flash('Book "{}" not available in your library.'.format('index'))
			return redirect(url_for('search'))

		query = form.query.data

		# keyword extraction...
		modified_query = myfunctions.extract_keywords(query)

		# elasticsearch searching...
		results = myfunctions.retrieve_docs(index, modified_query)
		time.sleep(5)

		#res = results

		
		if(form.types.data == 'sa'):
			res = myfunctions.get_answer(query, results[0])
		else:
			res = results[0]
		

	return render_template('search.html', title='Search', form=form, books=books, res=res)


@app.route('/multisearch', methods=['GET', 'POST'])
@login_required
def multisearch():
	form = MultiSearchForm()
	username = current_user.username
	books = myfunctions.get_user_books(username)
	books = sorted(books)

	books_list = [(i, books[i]) for i in range(len(books))]
	print(books_list)

	d = {}
	for x in books_list:
		d[x[0]] = x[1]

	form.books.choices = books_list

	res = []

	if((form.validate_on_submit()) and ('submit' in request.form)):
		sel_books = form.books.data
		selected_books = []
		for x in sel_books:
			selected_books.append(d[x])

		query = form.query.data
		modified_query = myfunctions.extract_keywords(query)

		answers = myfunctions.multi_retrieve(selected_books, modified_query)
		
		'''
		for ans in answers:
			res.append(ans[0])
		'''

		
		if(form.types.data == 'sa'):
			for ans in answers:
				res.append(myfunctions.get_answer(query, ans[0]))
		else:
			for ans in answers:
				res.append(ans[0])
		
		

	return render_template('multisearch.html', title='Search', form=form, books=books, res=res)


@app.route('/generateppt', methods=['GET', 'POST'])
@login_required
def generateppt():
	username = current_user.username
	books = myfunctions.get_user_books(username)
	books = sorted(books)
	form = PPTForm()

	if((form.validate_on_submit()) and ('submit' in request.form)):
		index = form.index.data
		topic = form.topic.data
		results = myfunctions.retrieve_docs(index, topic)

		slides = []
		for res in results:
			slides.append(myfunctions.get_summary(res))

		print(slides)

	return render_template('generateppt.html', form=form, books=books)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if(form.validate_on_submit() and 'submit' in request.form):
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('index'))

		flash('Please check your login details and try again.')
		return redirect(url_for('login'))

	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()

	if(form.validate_on_submit() and 'submit' in request.form):
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			flash('User already exists')
			return redirect(url_for('login'))

		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()

		return redirect(url_for('login'))

	return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))