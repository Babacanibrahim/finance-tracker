from flask import Blueprint, render_template, request, session, flash
from app.utils import login_required
from datetime import datetime, timedelta
from sqlalchemy import func, or_
from app import db
from app.models import Income, Expense, Income_Category, Expense_Category

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    incomes = Income.query.filter_by(user_id=session["user_id"]).order_by(Income.date).all()
    expenses = Expense.query.filter_by(user_id=session["user_id"]).order_by(Expense.date).all()

    selected_range = request.args.get("date_range", "all")
    now = datetime.utcnow().date()

    # Dönemlere ayırma
    if selected_range == "1_week":
        start_date = now - timedelta(days=7)
    elif selected_range =="1_month" : 
        start_date = now - timedelta(days=30)
    elif selected_range =="3_month" : 
        start_date = now - timedelta(days=90)
    elif selected_range =="6_month" : 
        start_date = now - timedelta(days = 180)
    elif selected_range =="1_year" : 
        start_date = now - timedelta(days=365)
    elif selected_range =="5_year" : 
        start_date = now - timedelta(days=5*365)  
    else:
        start_date = None    
    
    #Tarih filtreleme
    if start_date:
        incomes = [inc for inc in incomes if inc.date >= start_date]
        expenses = [exp for exp in expenses if exp.date >= start_date]

    #Tarihleri uniq yap
    all_dates = sorted(set([inc.date for inc in incomes] + [exp.date for exp in expenses]))

    labels = [date.strftime("%d/%m/%Y") for date in all_dates]

    income_data = []
    expense_data = []

    # Arraylere dahil etme
    for date in all_dates:
        income_on_date = sum(float(inc.amount) for inc in incomes if inc.date == date)
        expense_on_date = sum(float(exp.amount) for exp in expenses if exp.date == date)
        income_data.append(income_on_date)
        expense_data.append(expense_on_date)

    total_income = sum(income_data)
    total_expense = sum(expense_data)

    # Finansal analiz raporu
    rapor = ""
    if  total_income < total_expense :
        rapor = "Zarar"
        try:
            state = int((total_expense/total_income)*100)
        except:
            state = None
   
    elif total_income > total_expense:
        rapor = "Kar"
        try:
            state = int((total_income/total_expense)*100)
        except:
            state = None
       
    else:
        rapor = "Aynı"
        state =None

    #PİE CHART INCOMES
    income_query = db.session.query(Income).filter(Income.user_id ==session["user_id"])
    if start_date:
        income_query = income_query.filter(Income.date>=start_date)
    incomes_pie = income_query.all()

    income_category_totals_query =db.session.query(Income_Category.name, func.sum(Income.amount)).join(Income, Income.category_id ==
    Income_Category.id).filter(Income.user_id==session["user_id"])

    if start_date :
        income_category_totals_query = income_category_totals_query.filter(Income.date>=start_date)

    income_category_totals_query = income_category_totals_query.group_by(Income_Category.name)
    income_category_totals = income_category_totals_query.all()

    label_pie_incomes = [name for name, _ in income_category_totals]
    data_pie_incomes = [float(total) for _, total in income_category_totals]

    #PİE CHART EXPENSES
    expense_query = db.session.query(Expense).filter(Expense.user_id == session["user_id"])
    if start_date:
        expense_query = expense_query.filter(Expense.date >= start_date)
    expenses = expense_query.all()

    # GİDER KATEGORİ TOPLAMI
    expense_category_totals_query = db.session.query(
    Expense_Category.name,
    func.sum(Expense.amount)
).join(Expense, Expense.category_id == Expense_Category.id).filter(
    Expense.user_id == session["user_id"],
    or_(
        Expense_Category.user_id == session["user_id"],
        Expense_Category.user_id == None
    )
)
    if start_date:
        expense_category_totals_query = expense_category_totals_query.filter(Expense.date >= start_date)

    expense_category_totals_query = expense_category_totals_query.group_by(Expense_Category.name)
    expense_category_totals = expense_category_totals_query.all()

    # GİDER GRAFİĞİ İÇİN VERİLER
    label_pie_expenses = [name for name, _ in expense_category_totals]
    data_pie_expenses = [float(total) for _, total in expense_category_totals]

    return render_template("dashboard.html", data_pie_incomes = data_pie_incomes, label_pie_incomes = label_pie_incomes, data_pie_expenses = data_pie_expenses, label_pie_expenses = label_pie_expenses, expense_data = expense_data, income_data = income_data, labels = labels, selected_range = selected_range, rapor = rapor, state = state, total_income = total_income, total_expense = total_expense)