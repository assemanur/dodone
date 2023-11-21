"""Server for a DoDone App website."""

from flask import (Flask, render_template, request, flash, session, redirect, url_for, jsonify)
from flask_sqlalchemy import SQLAlchemy
from models import connect_to_db, db
import crud, os
from jinja2 import StrictUndefined
from forms import CreateUserForm, SignInForm
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def home():
    """View the homepage."""

    if 'user_id' in session:
        # Redirect to dashboard page if logged in
        return redirect(url_for('dashboard'))

    return render_template('home.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Sign-in to the account."""

    form = SignInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Verify user's credentials
        user = crud.authenticate_user(email, password)
        if user:
            session['user_id'] = user.id  
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard or another appropriate page
        else:
            # Authentication failed
            flash('Invalid email or password.', 'error')
        return redirect(url_for('signin'))  # Redirect after successful login
    
    return render_template('signin.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up for an account."""

    form = CreateUserForm()
    if form.validate_on_submit():
        # getting email and password from the form
        email = form.email.data
        password = form.password.data

        # Checking if user already exists
        existing_user = crud.get_user_by_email(email)
        if existing_user:
            flash('A user with that email already exists.', 'error')
            return redirect(url_for('signup'))

        # Creating a new user and adding to the database
        user = crud.create_user(email=email, password=password)
        if user:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('signin'))  # Redirect to the login page or another appropriate page
        else:
            flash('An error occurred. Please try again.', 'error')

    return render_template('signup.html', form=form)


@app.route('/logout')
def handle_logout():
    """Log the user out."""

    del session["user_id"]
    flash("You have logged out successfully!", 'success')
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    #Fetch user
    if 'user_id' not in session:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('home'))

    user_id = session['user_id']
    user = crud.get_user_by_id(user_id)  # Get the current user

    if not user:
        # Handle case where user is not found
        return redirect(url_for('home'))
    
    todo_lists = crud.get_todo_lists_by_user_id(user_id)


    return render_template('dashboard.html', user=user, todo_lists=todo_lists)


@app.route('/add_task', methods=['POST'])
def quick_add_task():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']
    title = request.form.get('list_title')
    todo_item_description = request.form.get('task_description')  # Get the to-do item description from the form

    # Create the new to-do list with the initial to-do item
    new_list = crud.create_todo_list(title=title, description="", user_id=user_id, category_id=None)
    item_in_new_list = crud.create_todo_item(description=todo_item_description, list_id=new_list.id, comment="")

    if item_in_new_list:
        flash('New to-do list with an initial item added successfully!', 'success')
    else:
        flash('An error occurred. Please try again.', 'error')

    return redirect(url_for('dashboard'))


@app.route('/view_lists')
def view_lists():
    # Ensure the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']
    user = crud.get_user_by_id(user_id)

    if not user:
        return redirect(url_for('home'))

    todo_lists = crud.get_todo_lists_by_user_id(user_id)

    return render_template('view_lists.html', todo_lists=todo_lists)


@app.route('/add_new_list', methods=['POST'])
def add_new_list():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']
    title = request.form.get('list_title')
    description = request.form.get('list_description')
    category_id = request.form.get('list_category')
    todo_item_descriptions = request.form.getlist('todo_item[]')  # Get all to-do item descriptions
    todo_item_comments = request.form.getlist('todo_comment[]')    # Get all to-do item comments
    todo_item_due_dates = request.form.getlist('todo_due_date[]')   #Get all to-do item due dates

    # Create the new to-do list
    new_list = crud.create_todo_list(title, description, user_id, category_id)

    if new_list:
        # Add each to-do item to the list
        for item_desc, comment, due_date in zip(todo_item_descriptions, todo_item_comments, todo_item_due_dates):
            crud.create_todo_item(item_desc, new_list.id, comment, due_date)
        flash('New to-do list added successfully!', 'success')
    else:
        flash('An error occurred. Please try again.', 'error')

    return redirect(url_for('view_lists'))


@app.route('/update_status/<int:item_id>', methods=['POST'])
def update_status(item_id):
    """Update the status of the to-do item. """

    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    new_status = crud.update_todo_item_status(item_id)
    
    # Return the new status as a JSON response
    return jsonify(new_status=new_status)


@app.route('/list_details/<int:list_id>')
def list_details(list_id):

    # Fetch the specific list using list_id
    todo_list = db.session.get(crud.ToDoList, list_id)

    if not todo_list:
        flash('List not found.', 'error')
        return redirect(url_for('view_lists'))
    
    categories = crud.Category.query.all()

    return render_template('list_details.html', todo_list=todo_list, categories=categories)


@app.route('/update_list/<int:list_id>', methods=['POST'])
def update_list(list_id):
    """Update the to-do list details. """

    list_to_update = db.session.get(crud.ToDoList, list_id)

    if not list_to_update:
        flash('To-Do list not found.', 'error')
        return redirect(url_for('view_lists'))

    # Updating list properties
    list_to_update.title = request.form.get('list_title')
    list_to_update.description = request.form.get('list_description')
    list_to_update.category_id = request.form.get('list_category')

    # Updating tasks
    task_ids = request.form.getlist('task_id[]')
    task_descriptions = request.form.getlist('task_description[]')
    task_comments = request.form.getlist('task_comment[]')
    task_due_dates = request.form.getlist('task_due_date[]')
    task_statuses = request.form.getlist('task_status[]')

    for i, task_id in enumerate(task_ids):
        #print(f"Processing task {i}: ID = {task_id}")
        if task_id == 'new':
            new_task = crud.create_todo_item(
                description=task_descriptions[i], 
                list_id=list_id, 
                comment=task_comments[i], 
                due_date=task_due_dates[i])
            db.session.add(new_task)
        else:
            existing_task = db.session.get(crud.ToDoItem, int(task_id))
            if existing_task:
                # Updating task properties
                existing_task.description = task_descriptions[i]
                existing_task.comment = task_comments[i]

            # Handling empty due_date string
            if task_due_dates[i]:
                existing_task.due_date = datetime.strptime(task_due_dates[i], '%Y-%m-%d')
            else:
                existing_task.due_date = None 

            existing_task.status = task_statuses[i]

    db.session.commit()
    flash('List updated successfully!', 'success')

    return redirect(url_for('view_lists'))


@app.route('/delete_list/<int:list_id>', methods=['POST'])
def delete_list(list_id):

    # Fetch the list to be deleted
    list = db.session.get(crud.ToDoList, list_id)
    if not list:
        flash('List not found.', 'error')
        return redirect(url_for('view_lists'))

    # Deleting associated tasks
    crud.ToDoItem.query.filter_by(list_id=list_id).delete()

    # Deleting the list
    db.session.delete(list)

    db.session.commit()

    flash('List deleted successfully!', 'success')
    return redirect(url_for('view_lists'))


@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    # Retrieve the task by ID
    task = db.session.get(crud.ToDoItem, task_id)

    # Check if task exists
    if task is None:
        # If no task found, return an error message
        return jsonify({'message': 'Task not found'}), 404

    # Delete the task
    db.session.delete(task)

    # Commit the changes to the database
    db.session.commit()

    # Return a success message
    return jsonify({'message': 'Task deleted successfully'}), 200



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)