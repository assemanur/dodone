"""Script to seed database."""

import os
import json

import crud
import models
import server

os.system('dropdb todo_list')
os.system('createdb todo_list')

with server.app.app_context():
    models.connect_to_db(server.app)
    models.db.create_all()

    #Inserting fake users data into the database
    with open('data/users_mock_data.json') as f:
        users_data = json.loads(f.read())

    #Iterating through each item in dictionary
    users_in_db = []
    for user in users_data:
        email, password = (
            user["email"],
            user["password"],
        )

        db_users = crud.create_user(email, password)
        users_in_db.append(db_users)

    models.db.session.add_all(users_in_db)
    models.db.session.commit()