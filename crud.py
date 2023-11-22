"""CRUD operations in database."""

from flask import jsonify
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

    return ToDoList.query.filter_by(user_id=user_id).order_by(ToDoList.created_at.desc()).all()


def get_upcoming_tasks(user_id):

    #category-color mapping
    category_colors = {
        1: "#C086E6",
        2: "#4679F2",
        3: "#FF9999",
        4: "#3EB65A",
        5: "#F9BA28",
    }

    todo_lists = ToDoList.query.filter_by(user_id=user_id).all()
    tasks = []
    for todo_list in todo_lists:
        list_tasks = ToDoItem.query.filter(ToDoItem.list_id == todo_list.id, ToDoItem.due_date != None).all()
        # Add each task's details to the tasks list
        for task in list_tasks:
            task_color = category_colors.get(todo_list.category_id, "#A0A0A0")  # Default color if category not in dict
            task_info = {
                "title": task.description,
                "start": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                "color": task_color,  # Assign color based on category
                "list_category": todo_list.category_id,
                "task_id": task.id
            }
            tasks.append(task_info)
    return tasks
    

def create_todo_list(title, description, user_id, category_id):
    """Create and return a new to-do list."""

    new_todo_list = ToDoList(title=title, description=description, user_id=user_id, category_id=category_id)
    db.session.add(new_todo_list)
    db.session.commit()
    return new_todo_list


def create_todo_item(description, list_id, comment=None, due_date=None):
    """Create and return a new to-do item."""
    if due_date == '':
        due_date = None
    new_todo_item = ToDoItem(description=description, list_id=list_id, comment=comment, due_date=due_date)
    db.session.add(new_todo_item)
    db.session.commit()
    return new_todo_item


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