from app import db, app
from datetime import datetime
from os import path
from sqlalchemy import desc

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='commenter', lazy='dynamic')
    likes = db.relationship('Like', backref='liker', lazy='dynamic')
    # shares = db.relationship('Share', backref='sharer', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    followings = db.relationship('Follow', foreign_keys='Follow.following_id', backref='following', lazy='dynamic')

    def __init__(self, username, nickname, email, password):
        self.username = username
        self.nickname = nickname
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
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, user_id, title, content):
        self.user_id = user_id
        self.title = title
        self.content = content

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    content = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, user_id, post_id, content):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, user_id, recipient_id, post_id):
        self.user_id = user_id
        self.recipient_id = recipient_id
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

def check_createUser(username, nickname, email):
    if User.query.filter_by(username=username).first():
        return 'Username already exists!'
    elif User.query.filter_by(nickname=nickname).first():
        return 'Nickname already exists!'
    elif User.query.filter_by(email=email).first():
        return 'Email already exists!'
    else:
        return ''

def create_user(username, nickname, email, password):
    user = User(username, nickname, email, password)
    db.session.add(user)
    db.session.commit()
    return user

def checkLogin(username, password):
    loginUser = User.query.filter_by(username=username, password=password).first()
    if loginUser:
        return {
            'id': loginUser.id,
            'username': loginUser.username,
            'nickname': loginUser.nickname,
            'email': loginUser.email,
            # 'password': loginUser.password
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
    if user_id is None:
        return False
    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    return True if like else False


def createLike(post_id, user_id):
    like = Like(user_id, post_id)
    db.session.add(like)
    db.session.commit()
    return like

def removeLike(post_id, user_id):
    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    db.session.delete(like)
    db.session.commit()
    return like

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
                'nickname': getNicknameFromId(comment.user_id),
                'content': comment.content,
                'created_at': comment.created_at,
                'lastUpdated': getReadableTimeString(datetime.now() - comment.created_at)
            }
            comment_list.append(comment_dict)
        return comment_list
    return None

def sharePost(user_id, recipient_id, post_id):
    share = Share(user_id, recipient_id, post_id)
    db.session.add(share)
    db.session.commit()
    app.logger.debug(f"User {user_id} shared post {post_id} to user {recipient_id} successfully!")
    return share

def getReadableTimeString(time):
    if time.days == 0:
        if time.seconds < 60:
            return "just now"
        elif time.seconds < 3600:
            minutes = time.seconds // 60
            return f"{minutes} minutes ago"
        else:
            hours = time.seconds // 3600
            return f"{hours} hours ago"
    else:
        days = time.days
        if days == 1:
            return "yesterday"
        else:
            return f"{days} days ago"

def getUserFromId(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'email': user.email
        }
    return None

def checkPassword(user_id, password):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user.password == password
    return False

def updatePassword(user_id, password):
    user = User.query.filter_by(id=user_id).first()
    user.password = password
    db.session.commit()
    return user

def checkFollowing(follower_id, following_id):
    follow = Follow.query.filter_by(follower_id=follower_id, following_id=following_id).first()
    return True if follow else False

def removeFollow(follower_id, following_id):
    follow = Follow.query.filter_by(follower_id=follower_id, following_id=following_id).first()
    db.session.delete(follow)
    db.session.commit()
    return follow

def getPostsFromFollowing(user_id):
    follows = Follow.query.filter_by(follower_id=user_id).all()
    if not follows:
        return None
    following_ids = [follow.following_id for follow in follows]
    posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
    post_list = []
    for post in posts:
        post_dict = {
            'id': post.id,
            'user_id': post.user_id,
            'user_nickname': getNicknameFromId(post.user_id),
            'title': post.title,
            'content': post.content,
            'numComment': getCommentNumber(post.id),
            'comments': getCommentsFromPostId(post.id),
            'numLike': getLikeNumber(post.id),
            'isLiked': checkUserLike(post.id, user_id),
            'numImg' : getNumberImgPerPost(post.id),
            'Imgs' : getAllImgOfPost(post.id),
            'created_at': post.created_at,
            'lastUpdated': getReadableTimeString(datetime.now() - post.created_at)
        }
        post_list.append(post_dict)
    return post_list

def createFollow(follower_id, following_id):
    follow = Follow(follower_id, following_id)
    db.session.add(follow)
    db.session.commit()
    return follow

def getUsernameFromId(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.username if user else None

def getNicknameFromId(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.nickname if user else None

def getAllNickname():
    users = User.query.all()
    if users:
        user_list = []
        for user in users:
            user_dict = {
                'id': user.id,
                'nickname': user.nickname
            }
            user_list.append(user_dict)
        return user_list
    return None

def createComment(post_id, user_id, content):
    comment = Comment(user_id, post_id, content)
    db.session.add(comment)
    db.session.commit()
    return comment

def getPostDetailFromPostId(post_id, user_id=None):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        return {
            'id': post.id,
            'user_id': post.user_id,
            'user_nickname': getNicknameFromId(post.user_id),
            'title': post.title,
            'content': post.content,
            'numComment': getCommentNumber(post.id),
            'comments': getCommentsFromPostId(post.id),
            'numLike': getLikeNumber(post.id),
            'isLiked': checkUserLike(post.id, user_id),
            'numImg' : getNumberImgPerPost(post.id),
            'Imgs' : getAllImgOfPost(post.id),
            'created_at': post.created_at,
            'lastUpdated': getReadableTimeString(datetime.now() - post.created_at)
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
                'isLiked': checkUserLike(post.id, user_id),
                'numImg' : getNumberImgPerPost(post.id),
                'Imgs' : getAllImgOfPost(post.id),
                'created_at': post.created_at,
                'lastUpdated': getReadableTimeString(datetime.now() - post.created_at)
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