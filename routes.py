from flask import render_template, request

from models import User, create_user
from app import app


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