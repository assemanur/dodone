"""SQLAlchemy models."""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    """A user model."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(200), nullable=False)
    f_name = db.Column(db.String(50), nullable=False)
    l_name = db.Column(db.String(50), nullable=False)
    profile_picture_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.String(500), nullable=True)
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
        return f'<User {self.email}>'


class ToDoList(db.Model):
    """To-Do list model."""

    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    items = db.relationship('ToDoItem', backref='todolist', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ToDoList {self.title}>'
    
class ToDoItem(db.Model):
    """An item in To-Do list."""

    __tablename__ = 'todo_items'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)  # For storing the due date
    status = db.Column(Enum('active', 'completed', name='status_types'), default='active')  # Track the status of the task
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # Modification timestamp
    list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'), nullable=False)

    def __repr__(self):
        return f'<ToDoItem {self.description}>'


class Category(db.Model):
    """To-Do list category."""

    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lists = db.relationship('ToDoList', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'
    

def connect_to_db(flask_app, db_uri="postgresql:///todo_list", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")
    
if __name__ == "__main__":
    from server import app
    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.
    connect_to_db(app)