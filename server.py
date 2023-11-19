"""Server for a DoDone App website."""

from flask import (Flask, render_template, request, flash, session, redirect, url_for, jsonify)
from flask_sqlalchemy import SQLAlchemy
from models import connect_to_db, db
import crud, os
from jinja2 import StrictUndefined
from forms import CreateUserForm, SignInForm


app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def home():
    """View the homepage."""
    return render_template('home.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Sign-in to the account."""

    form = SignInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Here, you can add the logic to verify the user's credentials
        user = crud.authenticate_user(email, password)
        if user:
            session['user_id'] = user.id  # Assuming the user model has an 'id' field
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
        # Here, you can add the logic to create a new user
        # For example, hash the password and save the user to the database
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


@app.route('/dashboard')
def dashboard():
    #Fetch user
    if 'user_id' not in session:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signin'))

    user_id = session['user_id']
    user = crud.get_user_by_id(user_id)  # Get the current user

    if not user:
        # Handle case where user is not found
        return redirect(url_for('signin'))
    
    todo_lists = crud.get_todo_lists_by_user_id(user_id)


    return render_template('dashboard.html', user=user, todo_lists=todo_lists)


@app.route('/view_lists')
def view_lists():
    # Ensure the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user_id = session['user_id']
    user = crud.get_user_by_id(user_id)

    if not user:
        return redirect(url_for('signup'))

    todo_lists = crud.get_todo_lists_by_user_id(user_id)

    return render_template('view_lists.html', todo_lists=todo_lists)


@app.route('/add_new_list', methods=['POST'])
def add_new_list():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user_id = session['user_id']
    title = request.form.get('list_title')
    description = request.form.get('list_description')
    todo_item_description = request.form.get('todo_item')  # Get the to-do item description from the form

    # Create the new to-do list with the initial to-do item
    new_list = crud.create_todo_list(title, description, user_id, todo_item_description)

    if new_list:
        flash('New to-do list with an initial item added successfully!', 'success')
    else:
        flash('An error occurred. Please try again.', 'error')

    return redirect(url_for('view_lists'))


@app.route('/update_status/<int:item_id>', methods=['POST'])
def update_status(item_id):
    # Update the status of the to-do item
    new_status = crud.update_todo_item_status(item_id)
    
    # Return the new status as a JSON response
    return jsonify(new_status=new_status)


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)