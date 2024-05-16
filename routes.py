from flask import Flask, redirect, url_for, render_template, request, session, redirect, url_for, render_template_string, session, flash, Response, abort, jsonify
from datetime import timedelta
from models import *
from app import app
import base64
import html

app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SECRET_KEY'] = 'tanphat'

@app.get('/test_comment')
def test_comment_page():
    session['user'] = {
        'id': 1
    }
    return render_template('test_comment.html')

@app.post('/test_comment')
def test_comment():
    post_id = request.form.get('post_id')
    comments = getCommentsFromPostId(post_id)
    return render_template('test_comment_result.html', comments=comments)

@app.get('/test_add_comment')
def test_add_comment():
    session['user'] = {
        'id': 1
    }
    return render_template('test_add_comment.html', post_id=1)

@app.post('/test_add_comment/<int:post_id>')
def test_add_comment_post(post_id):
    user_id = session['user']['id']
    print(user_id)
    if not user_id:
        abort(403)
    content = request.form.get('content')
    createComment(user_id=user_id, post_id=post_id, content=content)
    return redirect(url_for('test_add_comment'))

###

@app.get('/post_detail/post_id=<int:post_id>')
def get_post_detail(post_id):
    user_id = getUserIdFromPostId(post_id)
    my_post = False
    if session.get('user'):
        if session['user']['id'] is user_id and user_id is not None:
            my_post = True
    post_detail = getPostDetailFromPostId(post_id)
    return render_template('post_detail.html', post=post_detail, is_my_post=my_post)

@app.post('/comment/post_id=<int:post_id>')
def post_comment(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    createComment(user_id=session['user']['id'], post_id=post_id, content=request.form.get('content'))
    return redirect(url_for('get_post_detail', post_id=post_id))

@app.post('/comment')
def new_comment():
    data = request.json
    comment = createComment(data['postId'], data['userId'], data['content'])
    html_response = (
        "<div class='card-body comment-body'>"
        f"<h6 class='card-title comment-title'>{getUsernameFromId(comment.user_id)}</h6>"
        f"<p class='card-text comment-content'>{html.escape(comment.content)}</p>"
        "<p class='card-text update-time text-muted'>Updated: just now </p>"
        "</div>"
    )
    return html_response, 200

@app.post('/like_action')
def like_action():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = request.json
    user_id = session['user']['id']
    post_id = data['postId']
    if checkUserLike(post_id, user_id):
        removeLike(post_id, user_id)
        return {
            'likeStatus': 'remove',
            'likeCount': getLikeNumber(post_id)
        }, 200
    createLike(post_id, user_id)
    return {
        'likeStatus': 'add',
        'likeCount': getLikeNumber(post_id)
    }, 200

@app.post('/share_action')
def share_action():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_id = session['user']['id']
    post_id = request.form.get('postId')
    recipient_ids = request.form.getlist('recipientId')
    app.logger.info(f"Recipient ids recieve by share_action(): {recipient_ids}")
    for recipient_id in recipient_ids:
        sharePost(user_id, recipient_id, post_id)
        app.logger.info(f"User {user_id} shared post {post_id} to user {recipient_id}")
    return jsonify({}), 204
###

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'GET':
        return render_template('add.html')

    username = request.form.get('username_field')
    nickname = request.form.get('nickname_field')
    email = request.form.get('email_field')
    password = request.form.get('password_field')

    user = create_user(username, nickname, email, password)
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
            app.logger.info(f"User {username} logged in successfully!")
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
        nicknameList = getAllNickname()
        # Remove the current user from the nicknameList
        nicknameList = [user for user in nicknameList if user['id'] != user_id]

        return render_template('post_content.html', post=postWithImage, nicknameList=nicknameList)
    
    return redirect(url_for('login'))

@app.get('/my_post')
def my_post():
    if 'user' in session:
        user_id = session['user']['id']
        my_post = getAllPost(user_id)
        return render_template('my_post.html', myPosts=my_post)
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username_field']
        email = request.form['email_field']
        password = request.form['password_field']
        check = check_createUser(username, email)
        if check == '':
            create_user(username, email, password)
            flash("Your account has been successfully created!", 'info')
        else:
            flash(check, 'info')
    return render_template('register.html')