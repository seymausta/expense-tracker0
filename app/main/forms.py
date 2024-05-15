from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectField, \
    TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,  Length, NumberRange
import sqlalchemy as sa
from wtforms.widgets import HiddenInput
from app import db
from app.models import User, Category, Expense


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

    def __init__(self, expense=None, *args, **kwargs):
        super(UpdateExpenseForm, self).__init__(*args, **kwargs)
        if expense:
            self.name.data = expense.name
            self.amount.data = expense.amount
            self.category.choices = [(category.id, category.name) for category in Category.query.all()]
            self.category.data = expense.category_id
            self.date.data = expense.date
            self.description.data = expense.description

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


class BudgetForm(FlaskForm):
    name = StringField('Income Name', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Add Income')