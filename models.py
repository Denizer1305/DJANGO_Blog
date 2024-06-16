from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from connect_db import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
    posts = db.relationship('Post', backref='user', cascade='all, delete')

    def __repr__(self):
        return f"<users {self.id}>"

    def set_password(self, password):
        self.psw = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.psw, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='category', cascade='all, delete')

    def __repr__(self):
        return f"<categories {self.id}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(50))
    desc = db.Column(db.String(300), nullable=False)
    post = db.Column(db.String(2500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self):
        return f"<posts {self.id}>"
