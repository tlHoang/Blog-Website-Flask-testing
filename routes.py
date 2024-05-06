from flask import Flask, redirect, url_for, render_template, request, session, redirect, url_for, render_template_string, session, flash, Response
from datetime import timedelta
from models import *
from app import app
import base64

app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SECRET_KEY'] = 'tanphat'

@app.route('/')
def index():
    return render_template('home.html')

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
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/user')
def user():
    if 'user' in session:
        return session['user']

@app.get('/logout')
def logout():
    session.pop('user', default=None)
    return redirect(url_for('index'))

@app.get('/post')
def getpostpage():
    if 'user' in session:
        return render_template('post_input.html')
    return redirect(url_for('index'))

@app.post('/post')
def post_bai():
    if 'user' in session:
        user_id = session['user']['id']
        title = request.form['title']
        content = request.form['content']
        post = create_post(user_id, title, content)
        images = request.files.getlist('image')
        for image in images:
            if image.filename != '':
                image_data = image.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                createImg(post.id, base64_image, image.filename, image.mimetype)

        postWithImage = getPostFromPostID(post.id)
        return render_template('post_content.html', post=postWithImage)
    
    return redirect(url_for('login'))

@app.get('/my_post')
def my_post():
    if 'user' in session:
        user_id = session['user']['id']
        my_post = getAllPost(user_id)
        # print(my_post)
        return render_template('my_post.html', myPosts=my_post)
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')