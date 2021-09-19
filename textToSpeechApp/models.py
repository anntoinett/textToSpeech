from datetime import datetime
from textToSpeechApp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#models
class User(db.Model, UserMixin): #inheritance inside parenthesis
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) #reltionship to Post-model,
                                                                # backref says that if we have a post we can easily get its user by querying post.author being in post table,
                                                                # lazy-sql willl load data when necessary

    def __repr__(self): #how it would be represented
        return f"User('{self.username}, {self.email}, {self.image_file})"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #we pass function not current date
    content = db.Column(db.Text,nullable=False)
    last_part = db.Column(db.Integer, nullable=False, default=0)
    number_of_parts = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)#user is lowercase because here its the tablename which should be low

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

