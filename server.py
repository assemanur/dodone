"""Server for a DoDone App website."""

from flask import (Flask, render_template, request, flash, session, redirect, url_for)
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


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)