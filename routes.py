from flask import render_template, request, session, redirect, url_for, render_template_string

from models import User, create_user
from app import app

app.config['SECRET_KEY'] = '1111'

@app.route('/')
def index():

    users = User.query.all()

    return render_template('index.html', users=users)


@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'GET':
        return render_template('add.html')

    username = request.form.get('username_field')
    email = request.form.get('email_field')
    password = request.form.get('password_field')

    user = create_user(username, email, password)
    return render_template('add.html', user=user)

@app.get('/logout')
def logout():
    session.pop('user', default=None)
    return redirect(url_for('login'))

@app.get('/post')
def getpostpage():
    session['user'] = 'user1'
    return render_template('post.html')

@app.post('/post')
def post_bai():
    if 'user' in session: