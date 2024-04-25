from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from models import User, create_user, checkLogin
from app import app

app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SECRET_KEY'] = 'tanphat'

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

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.permanent = True
        username = request.form.get('username_field')
        password = request.form.get('password_field')
        checkUser = checkLogin(username, password)
        if checkUser:
            session['user'] = checkUser
            return redirect(url_for('user'))
    return render_template('login.html')

@app.route('/user')
def user():
    if 'user' in session:
        return session['user']