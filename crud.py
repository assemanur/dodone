"""CRUD operations in database."""

from flask import session
from models import db, User, ToDoList, ToDoItem, Category, Comment, connect_to_db
#import requests

def create_user(username, email, password):
    """Creating a new user."""

    new_user = User(username=username, email=email)
    new_user.password = password  # This will hash the password
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return new_user


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.verify_password(password):
        return user
    return None


def update_user(user_id, username=None, email=None, password=None):
    """Updating user information."""
    
    user = User.query.get(user_id)
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = password  # Assuming you have a password setter that hashes the password

        db.session.commit()
        return user
    else:
        return None  # User not found


if __name__ == '__main__':
    from server import app
    connect_to_db(app)