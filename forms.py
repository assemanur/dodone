"""WTForms form classes."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=35)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[Optional(), Length(min=2, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=8, max=35)])



class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=35)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')


class ToDoListForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    user_id = IntegerField('User ID', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional()])
    submit = SubmitField('Create List')


class ToDoItemForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    comment = TextAreaField('Comment', validators=[Optional()])
    is_completed = BooleanField('Completed', validators=[Optional()])
    list_id = IntegerField('List ID', validators=[DataRequired()])
    submit = SubmitField('Add Item')

