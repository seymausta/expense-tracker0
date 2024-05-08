from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,  Length, NumberRange
import sqlalchemy as sa
from wtforms.widgets import HiddenInput

from app import db
from app.models import User, Category, Expense

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

class ExpenseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=140)])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add')
    delete = SubmitField('Delete', widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]

    def validate_category(self, category):
        if not Category.query.get(category.data):
            raise ValidationError('Invalid category.')

class UpdateExpenseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=140)])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Update')
    delete = SubmitField('Delete', widget=HiddenInput())

    def __init__(self, expense, *args, **kwargs):
        super(UpdateExpenseForm, self).__init__(*args, **kwargs)
        self.expense = expense
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]
        self.populate_form_fields()

    def populate_form_fields(self):
        self.name.data = self.expense.name
        self.amount.data = self.expense.amount
        self.category.data = self.expense.category_id
        self.date.data = self.expense.date
        self.description.data = self.expense.description

        print("Expense Name:", self.expense.name)
        print("Expense Amount:", self.expense.amount)
        print("Expense Category ID:", self.expense.category_id)
        print("Expense Date:", self.expense.date)
        print("Expense Description:", self.expense.description)

    def validate_category(self, category):
        if not Category.query.get(category.data):
            raise ValidationError('Invalid category.')

class UpdateAccountForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Update Account')

class AddCategoryForm(FlaskForm):
    categoryName = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')