"""CRUD operations in database."""

from flask import session
from models import db, User, ToDoList, ToDoItem, Category, connect_to_db
#import requests

def create_user(email, password):
    """Creating a new user."""

    new_user = User(email=email)
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


def update_user(user_id, email=None, password=None):
    """Updating user information."""

    user = User.query.get(user_id)
    if user:
        if email:
            user.email = email
        if password:
            user.password = password

        db.session.commit()
        return user
    else:
        return None  # User not found
    

def get_todo_lists_by_user_id(user_id):
    """Return to-do lists for a user with the given user_id."""

    # First, get the user by email
    user = User.query.filter_by(id=user_id).first()

    # If the user exists, return their to-do lists
    if user:
        return user.lists
    else:
        return None
    

def create_todo_list(title, description, user_id, todo_item_description):
    """Create and return a new to-do list."""
    new_todo_list = ToDoList(title=title, description=description, user_id=user_id)
    db.session.add(new_todo_list)
    db.session.commit()

    # Add an initial to-do item to the list
    new_todo_item = ToDoItem(description=todo_item_description, list_id=new_todo_list.id)
    db.session.add(new_todo_item)
    db.session.commit()

    return new_todo_list


def update_todo_item_status(item_id):
    """Update the status of a to-do item and return the new status."""
    item = ToDoItem.query.get(item_id)
    if item:
        # toggle between 'active' and 'completed' statuses
        if item.status == 'active':
            item.status = 'completed'
        elif item.status == 'completed':
            item.status = 'active'

        db.session.commit()
        return item.status

    return None



if __name__ == '__main__':
    from server import app
    connect_to_db(app)