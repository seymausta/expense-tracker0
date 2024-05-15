from collections import defaultdict
from datetime import datetime,timedelta
from sqlalchemy import func
from app import db
from flask import render_template, flash, redirect, url_for, request, abort, jsonify, current_app

from app.auth.forms import ChangePasswordForm
from app.main.forms import ExpenseForm, UpdateAccountForm, AddCategoryForm, \
    BudgetForm
from flask_login import current_user, login_required
from app.models import User, Expense, Category, Income
from app.main import bp

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template("index.html")

@bp.route('/add_expense', methods=['GET', 'POST'])
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
            return redirect(url_for('main.expense_history'))
        else:
            flash('You must be logged in to add an expense', 'error')
            return redirect(url_for('auth.login'))
    return render_template('add_expense.html', title='Add Expense', form=form)

@bp.route("/expenses", methods=["GET"])
def expenses():
    """Manage expenses"""

    return render_template("expenses.html", title='Manage Expenses')


@bp.route('/expense_history', methods=['GET'])
@login_required
def expense_history():
    form = ExpenseForm()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.all()
    category_dict = {category.id: category.name for category in categories}

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['EXPENSES_PER_PAGE']
    pagination = Expense.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    expenses = pagination.items

    total_pages = pagination.pages
    current_page = pagination.page

    # Sayfa numaralarını oluştur
    page_nums = list(range(1, total_pages + 1))

    # Önceki ve sonraki sayfa URL'lerini oluştur
    prev_url = url_for('main.expense_history', page=current_page - 1) if pagination.has_prev else None
    next_url = url_for('main.expense_history', page=current_page + 1) if pagination.has_next else None

    return render_template('expense_history.html', title='Expenses', expenses=expenses,
                           category_dict=category_dict, form=form,
                           prev_url=prev_url, next_url=next_url, page_nums=page_nums, current_page=current_page)

@bp.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:  # Kullanıcının kendi harcamasını silme yetkisi var mı kontrol et
        abort(403)  # 403 Hata Kodu: Yasak
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('main.expense_history'))


@bp.route('/update_expense/<int:expense_id>', methods=['POST'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    form = ExpenseForm()

    if form.validate_on_submit():
        expense.name = form.name.data
        expense.amount = form.amount.data
        expense.category_id = form.category.data
        expense.date = form.date.data
        expense.description = form.description.data

        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('main.expense_history'))

    return render_template('expense_history.html', title='Update Expense', form=form)



@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.paginate(page=page, per_page=current_app.config['CATEGORY_PER_PAGE'], error_out=False)
    next_url = url_for('main.categories', page=categories.next_num) if categories.has_next else None
    prev_url = url_for('main.categories', page=categories.prev_num) if categories.has_prev else None

    form = AddCategoryForm()
    if form.validate_on_submit():
        category_name = form.categoryName.data
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash('New category added successfully!', 'success')
        return redirect(url_for('main.categories'))

    return render_template('categories.html', title='Spend Categories', form=form, categories=categories.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    account_form = UpdateAccountForm()
    password_form = ChangePasswordForm()

    if account_form.validate_on_submit():
        current_user.firstname = account_form.firstname.data
        current_user.lastname = account_form.lastname.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.account'))

    elif request.method == 'POST' and password_form.validate():
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Your password has been changed!', 'success')
        return redirect(url_for('main.account'))

    elif request.method == 'POST':
        flash('Passwords do not match!', 'danger')
        account_form.firstname.data = current_user.firstname
        account_form.lastname.data = current_user.lastname

    elif request.method == 'GET':
        account_form.firstname.data = current_user.firstname
        account_form.lastname.data = current_user.lastname

    return render_template('account.html', title='Account', account_form=account_form, password_form=password_form)



@bp.route('/category/<int:category_id>/expenses')
@login_required
def category_expenses(category_id):
    category = Category.query.get_or_404(category_id)
    expenses = category.expenses
    return render_template('category_expenses.html', title='Category Expenses', category=category, expenses=expenses)

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
def dashboard():
    form = ExpenseForm()

    def last_five_expenses():
        return Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()

    def total_spend_week(user_id):
            # Haftanın başlangıç tarihini bulma
        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=current_date.weekday())

            # Haftalık harcamaları sorgulama
        total_weekly_spend = db.session.query(func.sum(Expense.amount)). \
            filter(Expense.user_id == user_id). \
            filter(Expense.date >= start_of_week).scalar()

        return total_weekly_spend or 0

    def total_spend_year(user_id):
            # İçinde bulunulan yıl için harcamaları sorgulama
        total_yearly_spend = db.session.query(func.sum(Expense.amount)). \
            filter(Expense.user_id == user_id). \
            filter(func.extract('year', Expense.date) == datetime.now().year).scalar()

        return total_yearly_spend or 0

    def total_spend_month(user_id):
            # İçinde bulunulan ay için harcamaları sorgulama
        total_monthly_spend = db.session.query(func.sum(Expense.amount)). \
            filter(Expense.user_id == user_id). \
            filter(func.extract('year', Expense.date) == datetime.now().year). \
            filter(func.extract('month', Expense.date) == datetime.now().month).scalar()

        return total_monthly_spend or 0


    categories = Category.query.all()
    category_dict = {category.id: category.name for category in categories}

    last_five_expenses = last_five_expenses()
    total_spend_week = total_spend_week(current_user.id)
    total_spend_month = total_spend_month(current_user.id)
    total_spend_year = total_spend_year(current_user.id)

    return render_template('dashboard.html', title='Dashboard', last_five_expenses=last_five_expenses,
                               total_spend_week=total_spend_week, total_spend_month=total_spend_month,
                               total_spend_year=total_spend_year, category_dict=category_dict,
                               weekly_spending=weekly_spending, form=form)

@bp.route('/weekly_spending')
def weekly_spending():
    # Haftalık harcama verilerini hazırla
    weekly_spending = []

    # Son 4 haftanın başlangıç ve bitiş tarihlerini belirleme
    today = datetime.today()
    for i in range(4):
        end_of_week = today - timedelta(days=(i * 7))
        start_of_week = end_of_week - timedelta(days=6)

        # Haftalık harcamaları sorgulama
        weekly_spend = db.session.query(func.sum(Expense.amount)). \
            filter(Expense.user_id == current_user.id). \
            filter(Expense.date >= start_of_week). \
            filter(Expense.date <= end_of_week).scalar()

        # Haftalık harcama miktarını sözlüğe ekleme
        weekly_spending.append({
            'start_of_week': start_of_week.strftime('%b %d'),
            'end_of_week': end_of_week.strftime('%b %d'),
            'amount': weekly_spend or 0  # Harcama miktarı 0 ise None yerine 0 olarak ayarlanır
        })

    # Grafik için gerekli verileri JSON formatında döndür
    return jsonify(weekly_spending)

@bp.route('/monthly_spending')
def monthly_spending():
    monthly_spending = defaultdict(int)

    # Şu anki yılın başlangıç tarihini al
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)

    # Şu anki yılın bitiş tarihini al
    end_of_year = datetime(current_year, 12, 31)

    # Kullanıcının tüm harcamalarını al
    expenses = Expense.query.filter_by(user_id=current_user.id).filter(
        Expense.date >= start_of_year,
        Expense.date <= end_of_year
    ).all()

    # Aylık harcamaları topla
    for expense in expenses:
        monthly_key = expense.date.strftime('%b %Y')
        monthly_spending[monthly_key] += expense.amount

    # JSON formatında aylık harcama verilerini döndür
    return jsonify(monthly_spending)

@bp.route('/budget', methods=['GET', 'POST'])
def budget():
    form = BudgetForm()
    if form.validate_on_submit():
        income = Income(name=form.name.data, amount=form.amount.data, date=form.date.data,user_id=current_user.id)
        db.session.add(income)
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('main.budget'))
    incomes = Income.query.all()
    return render_template('budget.html', title='Budget', form=form, incomes=incomes)