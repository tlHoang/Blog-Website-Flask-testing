from flask import Flask, redirect, url_for, render_template, request, session, redirect, url_for, render_template_string, session, flash, Response, abort, jsonify
from datetime import timedelta
from models import *
from app import app
import base64
import html

app.permanent_session_lifetime = timedelta(minutes=20)
app.config['SECRET_KEY'] = 'tanphat'

@app.get('/post_detail/post_id=<int:post_id>')
def get_post_detail(post_id):
    user_id = getUserIdFromPostId(post_id)
    user_id_view = None
    my_post = False
    if session.get('user'):
        user_id_view = session['user']['id']
        if session['user']['id'] is user_id and user_id is not None:
            my_post = True
    post_detail = getPostDetailFromPostId(post_id, user_id_view)
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
        f"<a href='/user/user_id={comment.user_id}' class='name'><h6 class='card-title comment-title'>{getUsernameFromId(comment.user_id)}</h6></a>"
        f"<p class='card-text comment-content'>{html.escape(comment.content)}</p>"
        "<p class='card-text update-time text-muted'>Updated: just now </p>"
        "</div>"
    )
    return html_response, 200

@app.get('/following_posts')
def following_posts():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_id = session['user']['id']
    posts = getPostsFromFollowing(user_id)
    return render_template('following_posts.html', posts=posts)


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

@app.post('/follow_action')
def follow_action():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = request.json
    followerId = data['followerId']
    followingId = data['followingId']
    if str(followerId) != str(session['user']['id']):
        return {
            'message': 'User ID is incorrect'
        }, 401
    if checkFollowing(followerId, followingId):
        removeFollow(followerId, followingId)
        return {
            'followStatus': 'remove'
        }, 200
    createFollow(followerId, followingId)
    return {
        'followStatus': 'add'
    }, 200

@app.get('/user_profile')
def user_profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    posts = getAllPostFromUserId(session['user']['id'])
    return render_template('user_profile.html', posts=posts)

@app.post('/update_password')
def update_password():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = request.json
    if str(data['userId']) != str(session['user']['id']):
        return {
            'message': 'User ID is incorrect'
        }, 401
    if data['newPassword'] == '':
        return {
            'message': 'New password cannot be empty'
        }, 400
    if not checkPassword(data['userId'], data['currentPassword']):
        return {
            'message': 'Current password is incorrect'
        }, 401
    updatePassword(data['userId'], data['newPassword'])
    return {
        'message': 'Password updated successfully'
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
    if 'user' in session:
        user_id = session['user']['id']
        shared_posts = getAllSharedPostWithSharer(user_id)
        posts = shared_posts + getAllPost(user_id)
        return render_template('home.html', posts=posts)
    return render_template('home.html', posts=getAllPost())

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

@app.route('/user/user_id=<int:user_id>')
def user(user_id=None):
    is_my_profile = False
    is_following = False
    if 'user' in session:
        if session['user']['id'] is user_id and user_id is not None:
            is_my_profile = True
        else:
            is_following = checkFollowing(session['user']['id'], user_id)

        posts = getAllPostFromUserId(user_id)
        user = getUserFromId(user_id)
        return render_template('user_profile.html', user=user, posts=posts, is_my_profile=is_my_profile, is_following=is_following)
    return redirect(url_for('login'))
    # con 1 truong hop la user chua dang nhap, tam thoi se chuyen ve trang login

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
        my_post = getAllPostFromUserId(user_id)
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

@app.route('/discover')
def discover():
    return render_template('discover.html', posts=getAllPost())

# @app.route('/search/query=<string:query>&category=<string:category>')
# def search():
