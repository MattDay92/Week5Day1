from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from secrets import token_hex
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

# different way of creating a table
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
                        #VARCHAR in SQL
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    apitoken = db.Column(db.String)
    post = db.relationship('Post', backref='author', lazy=True)
                                #who is the author?
    followed = db.relationship('User', 
        # MULTI JOIN
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        secondary = followers,
        backref=db.backref('followers', lazy='dynamic'), 
        lazy = 'dynamic'
        )


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.apitoken = token_hex(16)

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def follow(self, user):
        self.followed.append(user)
        db.session.commit()

    def unfollow(self, user):
        # cannot have duplicate entries with the .remove in sqlalchemy
        self.followed.remove(user)
        db.session.commit()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String, nullable=False)
    caption = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Likes', lazy=True)
                        # Table Name


    def __init__(self, title, img_url, caption, user_id):
        self.title = title
        self.img_url = img_url
        self.caption = caption
        self.user_id = user_id

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def saveChanges(self):
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()
    def getLikeCounter(self):
        return len(self.likes)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'img_url': self.img_url,
            'caption': self.caption,
            'date_created': self.date_created,
            'user_id': self.user_id,
            'author': self.author.username,
            'like_counter': len(self.likes)
        }

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
        # Liking the Post

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()
        # Unliking the Post




        