from flask import Blueprint, session
from flask_wtf.csrf import generate_csrf
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models import User, Budget, Expense

context_bp = Blueprint("context", __name__)

@context_bp.app_context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

@context_bp.app_context_processor
def inject_year():
    return {"current_year": datetime.now().year}

@context_bp.app_context_processor
def inject_user_and_notifications():
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
                        total_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                            Expense.user_id == session["user_id"],
                            Expense.category_id == item.category_id,
                            Expense.date >= budget.start_date,
                            Expense.date <= budget.end_date
                        ).scalar()

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