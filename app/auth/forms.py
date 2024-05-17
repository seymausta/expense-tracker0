import re
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectField, \
    TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange, Regexp
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    firstname = StringField('Name', validators=[DataRequired()])
    lastname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password):
        password_value = password.data
        if len(password_value) < 8:
            raise ValidationError('Password must be at least 8 characters long!')
        elif not re.search("[a-z]", password_value):
            raise ValidationError('Password must contain at least one lowercase letter!')
        elif not re.search("[A-Z]", password_value):
            raise ValidationError('Password must contain at least one uppercase letter!')
        elif not re.search("[0-9]", password_value):
            raise ValidationError('Password must contain at least one digit!')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_password(self, field):
        password_value = field.data
        if len(password_value) < 8:
            raise ValidationError('Password must be at least 8 characters long!')
        elif not re.search("[a-z]", password_value):
            raise ValidationError('Password must contain at least one lowercase letter!')
        elif not re.search("[A-Z]", password_value):
            raise ValidationError('Password must contain at least one uppercase letter!')
        elif not re.search("[0-9]", password_value):
            raise ValidationError('Password must contain at least one digit!')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

    def validate_old_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Old password is incorrect!')

    def validate_new_password(self, field):
        password_value = field.data
        if len(password_value) < 8:
            raise ValidationError('Password must be at least 8 characters long!')
        elif not re.search("[a-z]", password_value):
            raise ValidationError('Password must contain at least one lowercase letter!')
        elif not re.search("[A-Z]", password_value):
            raise ValidationError('Password must contain at least one uppercase letter!')
        elif not re.search("[0-9]", password_value):
            raise ValidationError('Password must contain at least one digit!')

    def validate_confirm_password(self, field):
        print("New Password:", self.new_password.data)
        print("Confirm Password:", field.data)
        if field.data != self.new_password.data:
            print("Passwords do not match!")
            raise ValidationError('Passwords must match!')

