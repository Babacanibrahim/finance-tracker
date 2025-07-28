from functools import wraps
from flask import session, flash, redirect, url_for
from app.models import User, Budget, Expense, BudgetItem
from sqlalchemy import func
from flask_wtf.csrf import generate_csrf
from datetime import datetime

# Giriş kontrolü (decorator)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için yetkiniz yok veya giriş yapmamışsınız.", "danger")
            return redirect(url_for("auth.login"))
    return decorated_function

# Templatelara csrf token otomatik ekleme
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

# Templatelara yıl ekleme
def inject_year():
    return {"current_year": datetime.now().year}

# Templatelara kullanıcı ve bildirim verilerini ekleme
def inject_user_data():
    user = None
    notification_count = 0
    notification_list = []

    if "user_id" in session:
        user = User.query.get(session["user_id"])

        if user and user.allow_notifications:
            budgets = Budget.query.filter_by(user_id=session["user_id"]).all()
            for budget in budgets:
                for item in budget.items:
                    if item.category_id:
                        total_spent = (
                            BudgetItem.query.session.query(func.coalesce(func.sum(Expense.amount), 0))
                            .filter(
                                Expense.user_id == session["user_id"],
                                Expense.category_id == item.category_id,
                                Expense.date >= budget.start_date,
                                Expense.date <= budget.end_date
                            )
                            .scalar()
                        )

                        if item.amount > 0 and float(total_spent) / float(item.amount) >= 0.9:
                            percent = round(float(total_spent) / float(item.amount) * 100, 2)
                            notification_list.append({
                                "budget_id": budget.id,
                                "budget_name": budget.name,
                                "category": item.category.name,
                                "percent": percent
                            })

            notification_count = len(notification_list)

    return dict(
        user=user,
        notification_count=notification_count,
        notification_list=notification_list
    )
