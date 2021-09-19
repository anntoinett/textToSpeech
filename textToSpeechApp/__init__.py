from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# There are two special exceptions with regards to the value of __name__:

#    Inside a __init__.py package constructor module, the value of __name__ is the package name, without __init__. For example, in my_package/__init__.py, the value of __name__ is just my_package.
#   In the main module of the application (the file you run the Python interpreter on) the value of __name__ has the special value of __main__.

# name - np. my_package.my_class if class in package but if in top-level directory then = my_class, flask uses it to know where to look up resources ..
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bbe3578bd468a2f5bc5e47ca515b5b47'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "sqlite:///site2.db"  # relative path from an actual file - it should be created in our project directory, same as __init__
db = SQLAlchemy(app)  # in alchemy we can represent database structures as classes - each class -> a table in db
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #function name of the route
login_manager.login_message_category = 'info' #category in bootstrap css


from textToSpeechApp import routes  # here because our routes are importing app which is above and must be known when we get into routes
