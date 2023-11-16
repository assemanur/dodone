"""Server for a DoDone App website."""

from flask import (Flask, render_template, request, flash, session, redirect)
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined


app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = StrictUndefined

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

@app.route('/')
def home():
    """View the homepage."""
    return render_template('home.html')

@app.route('/signin')
def signin():
    """Sign-in to the account."""
    return render_template('signin.html')  # You need to create a signin.html template

@app.route('/signup')
def signup():
    """Sign up for an account."""
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)