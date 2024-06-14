
from collections import defaultdict
from datetime import datetime,timedelta
from sqlalchemy import func, extract
from app import db
from flask import render_template, flash, redirect, url_for, request, abort, jsonify, current_app
from app.auth.forms import ChangePasswordForm
from app.main.forms import ExpenseForm, UpdateAccountForm, AddCategoryForm, \
    BudgetForm
from flask_login import current_user, login_required
from app.models import User, Expense, Category, Income, Payment
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
                payment_id=form.payment.data,
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

    payments = Payment.query.all()
    payment_dict = {payment.id: payment.name for payment in payments}

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['EXPENSES_PER_PAGE']

    pagination = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).paginate(page=page, per_page=per_page,error_out=False)
    expenses = pagination.items

    total_pages = pagination.pages
    current_page = pagination.page

    # Sayfa numaralarını oluştur
    page_nums = list(range(1, total_pages + 1))

    # Önceki ve sonraki sayfa URL'lerini oluştur
    prev_url = url_for('main.expense_history', page=current_page - 1) if pagination.has_prev else None
    next_url = url_for('main.expense_history', page=current_page + 1) if pagination.has_next else None

    return render_template('expense_history.html', title='Expenses', expenses=expenses,
                           category_dict=category_dict, form=form,payment_dict=payment_dict,
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
        expense.payment_id = form.payment.data
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
        for field, errors in password_form.errors.items():
            for error in errors:
                flash(f"{error}", 'error')

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
    expenses = Expense.query.filter_by(user_id=current_user.id, category_id=category_id).all()
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
        start_of_week = current_date - timedelta(days=current_date.weekday()+1)

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

    def total_income_last_month(user_id):
        # Bir önceki ay için gelirleri sorgulama
        last_month = datetime.now().month if datetime.now().month > 1 else 12
        last_year = datetime.now().year if last_month != 12 else datetime.now().year

        total_last_month_income = db.session.query(func.sum(Income.amount)). \
            filter(Income.user_id == user_id). \
            filter(func.extract('year', Income.date) == last_year). \
            filter(func.extract('month', Income.date) == last_month).scalar()

        return total_last_month_income or 0

    categories = Category.query.all()
    category_dict = {category.id: category.name for category in categories}

    payments = Payment.query.all()
    payment_dict = {payment.id: payment.name for payment in payments}

    last_five_expenses = last_five_expenses()
    total_spend_week = total_spend_week(current_user.id)
    total_spend_month = total_spend_month(current_user.id)
    total_spend_year = total_spend_year(current_user.id)
    total_last_month_income = total_income_last_month(current_user.id)

    return render_template('dashboard.html', title='Dashboard', last_five_expenses=last_five_expenses,
                           total_spend_week=total_spend_week, total_spend_month=total_spend_month,
                           total_spend_year=total_spend_year, total_last_month_income=total_last_month_income,
                           category_dict=category_dict,payment_dict=payment_dict, form=form)

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
            'start_of_week': start_of_week.strftime('%d %b'),
            'end_of_week': end_of_week.strftime('%d %b'),
            'amount': weekly_spend or 0  # Harcama miktarı 0 ise None yerine 0 olarak ayarlanır
        })

    # Grafik için gerekli verileri JSON formatında döndür
    return jsonify(weekly_spending)

@bp.route('/monthly_spending')
def monthly_spending():
    monthly_spending = defaultdict(int)

    # Şu anki yılın başlangıç ve bitiş tarihlerini al
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)
    end_of_year = datetime(current_year, 12, 31)

    # Kullanıcının tüm harcamalarını al
    expenses = Expense.query.filter_by(user_id=current_user.id).filter(
        Expense.date >= start_of_year,
        Expense.date <= end_of_year
    ).all()

    # Her ay için başlangıç değeri olarak 0 belirle
    for month in range(1, 13):
        month_key = datetime(current_year, month, 1).strftime('%b')
        monthly_spending[month_key] = 0

    # Aylık harcamaları topla
    for expense in expenses:
        month_key = expense.date.strftime('%b')
        monthly_spending[month_key] += expense.amount

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
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    return render_template('budget.html', title='Budget', form=form, incomes=incomes)


@bp.route('/monthly_income', methods=['GET'])
@login_required
def monthly_income():
    # En son yılı ve ayı al
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month

    # Kullanıcının belirtilen yıl ve ay için gelirlerini hesapla
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        func.extract('year', Income.date) == year,
        func.extract('month', Income.date) == month
    ).scalar()

    total_income = total_income or 0

    return render_template('dashboard.html', title='Monthly Income', total_income=total_income)

@bp.route('/bubble_chart_data')
@login_required
def bubble_chart_data():
    # Kullanıcının harcamalarını alın
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()

    # Kategorilere göre harcamaları gruplandırın
    category_expenses = {}
    for expense in user_expenses:
        category_id = expense.category_id
        if category_id not in category_expenses:
            category_expenses[category_id] = {
                'total_amount': 0,
                'expense_count': 0
            }
        category_expenses[category_id]['total_amount'] += expense.amount
        category_expenses[category_id]['expense_count'] += 1

    # Her kategori için balon grafik için veri noktası oluşturun
    bubble_chart_data = []
    for category_id, data in category_expenses.items():
        category = Category.query.get(category_id)
        bubble_chart_data.append({
            'x':data['total_amount'] ,  # Harcama sayısı x ekseninde
            'y': data['expense_count'],   # Toplam harcama miktarı y ekseninde
            'r': 10,                     # Balon boyutunu istediğiniz gibi ayarlayabilirsiniz
            'category_name': category.name
        })


    return jsonify(bubble_chart_data)


@bp.route('/expense_categories', methods=['GET'])
@login_required
def expense_categories():
    # Kullanıcının harcama kategorilerini al
    categories = Category.query.all()

    # Her bir kategori için toplam harcamayı hesapla
    category_expenses = []
    for category in categories:
        total_expense = db.session.query(func.sum(Expense.amount)).filter_by(category_id=category.id, user_id=current_user.id).scalar() or 0
        category_expenses.append({
            'category_name': category.name,
            'total_amount': total_expense  # total_expense yerine total_amount kullanıyoruz
        })

    return jsonify(category_expenses)

@bp.route('/category_report')
@login_required
def category_report():
    user_id = current_user.id
    current_year = datetime.now().year

    # Kategorilere göre harcamaları hesaplayın
    category_spending_trends_table = calculate_category_spending_trends(user_id, current_year)

    # Ödeme yöntemlerine göre harcamaları hesaplayın
    payment_method_spending_trends_table = calculate_payment_method_spending_trends(user_id, current_year)

    categories = Category.query.all()

    # Ödeme yöntemlerini al
    payment_methods = Payment.query.all()

    return render_template('category_report.html',
                           category_spending_trends_table=category_spending_trends_table,
                           payment_method_spending_trends_table=payment_method_spending_trends_table,
                           current_year=current_year,categories =categories,payment_methods=payment_methods)

def calculate_category_spending_trends(user_id, current_year):
    categories = Category.query.all()
    spending_trends_table = {}

    for month in range(1, 13):
        month_name = datetime.strptime(str(month), "%m").strftime("%B")
        category_expenses = []

        for category in categories:
            category_expense = Expense.query.filter(
                Expense.category_id == category.id,
                Expense.user_id == user_id,
                func.strftime('%Y', Expense.date) == str(current_year),
                func.strftime('%m', Expense.date) == str(month).zfill(2)
            ).all()
            total_expense = sum(expense.amount for expense in category_expense)
            category_expenses.append(total_expense)

        total_monthly_expense = sum(category_expenses)
        spending_trends_table[month_name] = {'expenses': category_expenses, 'total': total_monthly_expense}

    return spending_trends_table

def calculate_payment_method_spending_trends(user_id, current_year):
    payment_methods = Payment.query.all()
    spending_trends_table = {}

    for month in range(1, 13):
        month_name = datetime.strptime(str(month), "%m").strftime("%B")
        payment_method_expenses = []

        for payment_method in payment_methods:
            payment_expense = Expense.query.filter(
                Expense.payment_id == payment_method.id,
                Expense.user_id == user_id,
                func.strftime('%Y', Expense.date) == str(current_year),
                func.strftime('%m', Expense.date) == str(month).zfill(2)
            ).all()
            total_expense = sum(expense.amount for expense in payment_expense)
            payment_method_expenses.append(total_expense)

        total_monthly_expense = sum(payment_method_expenses)
        spending_trends_table[month_name] = {'expenses': payment_method_expenses, 'total': total_monthly_expense}

    return spending_trends_table

@bp.route('/monthly_report', methods=['GET', 'POST'])
@login_required
def monthly_report():
    if request.method == 'POST':
        selected_year = int(request.form.get('year', datetime.now().year))
    else:
        selected_year = datetime.now().year

    # Seçilen yıldaki her ayın tarihini al
    expense_dates = [datetime(selected_year, month, 1).strftime('%B') for month in range(1, 13)]

    # Seçilen yıla ait tüm harcamaları en güncelden en eskiye sıralayarak getir
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == selected_year
    ).order_by(Expense.date.desc()).all()

    # Kategori adlarını içeren bir sözlük oluştur
    category_dict = {}
    for category in Category.query.all():
        category_dict[category.id] = category.name

    payment_dict = {}
    for payment in Payment.query.all():
        payment_dict[payment.id] = payment.name

    # Seçilen yıla ait her ay için toplam harcamaları hesapla
    monthly_expense_totals = []
    for month in range(1, 13):
        total_expense = Expense.query.with_entities(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == selected_year,
            extract('month', Expense.date) == month
        ).scalar() or 0
        monthly_expense_totals.append(total_expense)

    year = datetime.now().year

    return render_template('monthly_report.html',
                           expense_dates=expense_dates,
                           selected_year=selected_year,
                           expenses=expenses, year=year,
                           category_dict=category_dict,
                           payment_dict=payment_dict,
                           monthly_expense_totals=monthly_expense_totals)

@bp.route("/report", methods=["GET"])
@login_required
def report():
    """View reports"""

    return render_template("report.html")

@bp.route('/expense_pie_chart')
@login_required
def expense_pie_chart():
    # Kullanıcının harcamalarını ödeme yöntemine göre gruplayın
    expenses_by_payment = db.session.query(Expense.payment_id, func.sum(Expense.amount)).\
        filter_by(user_id=current_user.id).group_by(Expense.payment_id).all()

    # Harcanan toplam tutarları ödeme yöntemine göre alın
    payment_labels = []
    payment_amounts = []
    for payment_id, total_amount in expenses_by_payment:
        payment_name = Payment.query.get(payment_id).name  # Ödeme yöntemi adını al
        payment_labels.append(payment_name)
        payment_amounts.append(total_amount)

    # JSON olarak verileri döndür
    return jsonify(labels=payment_labels, data=payment_amounts)