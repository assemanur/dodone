"""SQLAlchemy models."""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from server import app

db = SQLAlchemy(app)

class User(db.Model):
    """A user model."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(200), nullable=False)
    lists = db.relationship('ToDoList', backref='user', lazy=True)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class ToDoList(db.Model):
    """To-Do list model."""

    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    items = db.relationship('ToDoItem', backref='todolist', lazy=True)

    def __repr__(self):
        return f'<ToDoList {self.title}>'
    
class ToDoItem(db.Model):
    """An item in To-Do list."""

    __tablename__ = 'todo_items'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    comments = db.relationship('Comment', backref='todoitem', lazy=True)

    def __repr__(self):
        return f'<ToDoItem {self.description}>'
    
class Category(db.Model):
    """To-Do list category."""

    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lists = db.relationship('ToDoList', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'
    
class Comment(db.Model):
    """A comment to the item in To-Do list."""

    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('to_do_item.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.content}>'
    

def connect_to_db(flask_app, db_uri="postgresql:///todo_list", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")
    
if __name__ == "__main__":

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.
    connect_to_db(app)