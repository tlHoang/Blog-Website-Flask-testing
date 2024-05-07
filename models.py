from app import db, app
from os import path
from sqlalchemy import desc

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='commenter', lazy='dynamic')
    likes = db.relationship('Like', backref='liker', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    followings = db.relationship('Follow', foreign_keys='Follow.following_id', backref='following', lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, follower_id, following_id):
        self.follower_id = follower_id
        self.following_id = following_id

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    imgs = db.relationship('Img', backref='post', lazy='dynamic')

    def __init__(self, user_id, title, content):
        self.user_id = user_id
        self.title = title
        self.content = content

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    content = db.Column(db.String(1000))

    def __init__(self, user_id, post_id, content):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, user_id, post_id, content):
        self.user_id = user_id
        self.post_id = post_id

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    img = db.Column(db.Text, nullable=False, unique=False)
    name = db.Column(db.Text, nullable=False, unique=False)
    mimetype = db.Column(db.Text, nullable=False)

    def __init__(self, post_id, img, name, mimetype):
        self.post_id = post_id
        self.img = img
        self.name = name
        self.mimetype = mimetype

def create_user(username, email, password):
    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()
    return user

def checkLogin(username, password):
    loginUser = User.query.filter_by(username=username, password=password).first()
    if loginUser:
        return {
            'id': loginUser.id,
            'username': loginUser.username,
            'email': loginUser.email,
            'password': loginUser.password
        }
    return None

def create_post(user_id, title, content):
    post = Post(user_id, title, content)
    db.session.add(post)
    db.session.commit()
    return post

def getLikeNumber(post_id):
    likes = Like.query.filter_by(post_id=post_id).all()
    return len(likes)

def checkUserLike(post_id, user_id):
    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if len(like) == 0:
        return False
    return True

def getCommentNumber(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    return len(comments)

def getCommentsFromPostId(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    if comments:
        comment_list = []
        for comment in comments:
            comment_dict = {
                'user_id': comment.user_id,
                'username': getUsernameFromId(comment.user_id),
                'content': comment.content
            }
            comment_list.append(comment_dict)
        return comment_list
    return None

def getUsernameFromId(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.username if user else None

def createComment(post_id, user_id, content):
    comment = Comment(user_id, post_id, content)
    db.session.add(comment)
    db.session.commit()
    return comment

def getPostDetailFromPostId(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        return {
            'id': post.id,
            'user_id': post.user_id,
            'title': post.title,
            'content': post.content,
            'numComment': getCommentNumber(post.id),
            'comments': getCommentsFromPostId(post.id),
            'numLike': getLikeNumber(post.id),
            'numImg' : getNumberImgPerPost(post.id),
            'Imgs' : getAllImgOfPost(post.id)
        }
    return None

def getUserIdFromPostId(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        return post.user_id
    return None

def getAllPost(user_id):
    posts = Post.query.filter_by(user_id=user_id).order_by(desc(Post.id)).all()
    if posts:
        post_list = []
        for post in posts:
            post_dict = {
                'id': post.id,
                'user_id': post.user_id,
                'title': post.title,
                'content': post.content,
                'numComment': getCommentNumber(post.id),
                'numLike': getLikeNumber(post.id),
                'numImg' : getNumberImgPerPost(post.id),
                'Imgs' : getAllImgOfPost(post.id)
            }
            post_list.append(post_dict)
        return post_list
    return None

def getPostFromPostID(post_id):
    post = Post.query.filter_by(id=post_id).first()
    return {
        'id': post.id,
        'user_id': post.user_id,
        'title': post.title,
        'content': post.content,
        'numImg' : getNumberImgPerPost(post.id),
        'Imgs' : getAllImgOfPost(post.id)
    }

def createImg(post_id, img, name, mimetype):
    img = Img(post_id, img, name, mimetype)
    db.session.add(img)
    db.session.commit()
    return img

def getNumberImgPerPost(post_id):
    imgs = Img.query.filter_by(post_id=post_id).all()
    return len(imgs)

def getAllImgOfPost(post_id):
    imgs = Img.query.filter_by(post_id=post_id).all()
    if imgs:
        image_list = []
        for image in imgs:
            img_dict = {
                'img': image.img,
                'name' : image.name,
                'mimetype': image.mimetype
            }
            image_list.append(img_dict)
        return image_list
    return None

if __name__ == "__main__":
    with app.app_context():
        if not path.exists('app.db'):
            print("Creating database tables...")
            db.create_all()
            print("Done!")