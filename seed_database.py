"""Script to seed database."""

import os
import json

#import crud
import models
from models import db, User, ToDoList, ToDoItem, Category
import server
from server import app

os.system('dropdb todo_list')
os.system('createdb todo_list')

with open('data/mock_data.json') as f:
    data = json.loads(f.read())

# Seed the database
with server.app.app_context():
    models.connect_to_db(server.app)
    models.db.create_all()

    # Seed categories
    for category_data in data['categories']:
        category = Category(name=category_data['name'])
        db.session.add(category)

    # Iterating through each item in dictionary
    for user_data in data['users']:
        user = User(email=user_data['email'], password=user_data['password_hash'])
        db.session.add(user)

        #db_users = crud.create_user(email, password)

    # Seed to-do lists
    for list_data in data['todo_lists']:
        todo_list = ToDoList(title=list_data['title'], 
                             description=list_data['description'], 
                             user_id=list_data['user_id'], 
                             category_id=list_data['category_id'])
        db.session.add(todo_list)

    # Seed to-do items
    for item_data in data['todo_items']:
        todo_item = ToDoItem(description=item_data['description'], 
                             comment=item_data['comment'], due_date=item_data['due_date'], 
                             status=item_data['status'], list_id=item_data['todolist_id'])
        db.session.add(todo_item)

    # Commit the session
    db.session.commit()

print("Database seeded successfully!")

    #models.db.session.add_all(users_in_db)
    #models.db.session.commit()