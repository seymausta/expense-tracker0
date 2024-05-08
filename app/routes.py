from app import app,db
from flask import render_template, flash, redirect, url_for, request, abort
from app.forms import LoginForm, RegistrationForm, ExpenseForm, UpdateExpenseForm, UpdateAccountForm, AddCategoryForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User, Expense, Category
from urllib.parse import urlsplit
from app.email import send_password_reset_email


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid e-mail or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data,lastname=form.lastname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_expense = Expense(
                name=form.name.data,
                amount=form.amount.data,
                category_id=form.category.data,
                date=form.date.data,
                description=form.description.data,
                user_id=current_user.id  # Kullanıcının kimliği
            )
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expense_history'))
        else:
            flash('You must be logged in to add an expense', 'error')
            return redirect(url_for('login'))
    return render_template('add_expense.html', title='Add Expense', form=form)

@app.route("/expenses", methods=["GET"])
def expenses():
    """Manage expenses"""

    return render_template("expenses.html", title='Manage Expenses')


@app.route('/expense_history', methods=['GET'])
@login_required
def expense_history():
    form = ExpenseForm()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.all()
    category_dict = {category.id: category.name for category in categories}

    page = request.args.get('page', 1, type=int)
    per_page = app.config['EXPENSES_PER_PAGE']
    pagination = Expense.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    expenses = pagination.items

    total_pages = pagination.pages
    current_page = pagination.page

    # Sayfa numaralarını oluştur
    page_nums = list(range(1, total_pages + 1))

    # Önceki ve sonraki sayfa URL'lerini oluştur
    prev_url = url_for('expense_history', page=current_page - 1) if pagination.has_prev else None
    next_url = url_for('expense_history', page=current_page + 1) if pagination.has_next else None

    return render_template('expense_history.html', title='Expenses', expenses=expenses,
                           category_dict=category_dict, form=form,
                           prev_url=prev_url, next_url=next_url, page_nums=page_nums, current_page=current_page)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:  # Kullanıcının kendi harcamasını silme yetkisi var mı kontrol et
        abort(403)  # 403 Hata Kodu: Yasak
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expense_history'))


@app.route('/update_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    form = UpdateExpenseForm(expense=expense)  # Expense objesini form başlatılırken geçirin.

    if form.validate_on_submit():
        print("Form validation successful!")
        print("Before update:", expense.name, expense.amount)  # Güncellemeden önceki değerler
        expense.name = form.name.data
        expense.amount = form.amount.data
        expense.category_id = form.category.data
        expense.date = form.date.data
        expense.description = form.description.data

        print("Name:", expense.name)
        print("Amount:", expense.amount)

        print("After update:", expense.name, expense.amount)  # Güncellemeden sonraki değerler
        try:
            db.session.commit()
            flash('Your expense has been updated!', 'success')
            return redirect(url_for('expense_history'))
        except Exception as e:
            flash('An error occurred while updating the expense.', 'danger')
            print('Error:', e)  # Hatanın ayrıntılarını konsola yazdır
            db.session.rollback()  # Veritabanı değişikliklerini geri al

    return render_template('expense_history.html', title='Update Expense', form=form)



@app.route('/categories', methods=['GET', 'POST'])
def categories():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.paginate(page=page, per_page=app.config['CATEGORY_PER_PAGE'], error_out=False)
    next_url = url_for('categories', page=categories.next_num) if categories.has_next else None
    prev_url = url_for('categories', page=categories.prev_num) if categories.has_prev else None

    form = AddCategoryForm()
    if form.validate_on_submit():
        category_name = form.categoryName.data
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash('New category added successfully!', 'success')
        return redirect(url_for('categories'))

    return render_template('categories.html', title='Spend Categories', form=form, categories=categories.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
    return render_template('account.html', title='Account', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/category/<int:category_id>/expenses')
@login_required
def category_expenses(category_id):
    category = Category.query.get_or_404(category_id)
    expenses = category.expenses
    return render_template('category_expenses.html', title='Category Expenses', category=category, expenses=expenses)

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('login'))