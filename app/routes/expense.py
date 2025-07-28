from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

from app import db
from app.models import Expense, Expense_Category
from app.forms import ExpenseForm
from app.utils import login_required

expense_bp = Blueprint("expense", __name__)

@expense_bp.route("/expense", methods=["GET", "POST"])
@login_required
def expense():
    form = ExpenseForm(request.form)

    categories = Expense_Category.query.filter(
        or_(Expense_Category.user_id == session["user_id"], Expense_Category.user_id == None)
    ).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "POST" and form.validate():
        new_expense = Expense(
            category_id=form.category.data,
            amount=form.amount.data,
            date=form.date.data,
            user_id=session["user_id"]
        )
        db.session.add(new_expense)
        db.session.commit()
        flash("Harcamanız başarıyla kaydedildi.", "success")
        return redirect(url_for("expense.expense"))

    selected_categories = request.args.getlist("categories[]")
    selected_dates = request.args.getlist("dates[]")
    selected_amounts = request.args.getlist("amounts[]")
    order_by = request.args.get("order_by", "date_desc")
    selected_order = order_by

    query = Expense.query.filter(Expense.user_id == session["user_id"])

    def parse_amount_range(r):
        min_val, max_val = r.split("-")
        max_val = float(max_val) if max_val != "inf" else None
        return float(min_val), max_val

    def parse_date_range(r):
        now = datetime.utcnow().date()
        ranges = {
            "1_week": 7, "1_month": 30, "3_month": 90,
            "6_month": 180, "1_year": 365, "5_year": 5 * 365
        }
        days = ranges.get(r)
        if days:
            return now - timedelta(days=days), now
        return None, None

    if selected_categories:
        query = query.filter(Expense.category_id.in_(selected_categories))

    if selected_amounts:
        amount_filters = []
        for r in selected_amounts:
            min_val, max_val = parse_amount_range(r)
            if max_val is None:
                amount_filters.append(Expense.amount >= min_val)
            else:
                amount_filters.append(and_(Expense.amount >= min_val, Expense.amount <= max_val))
        query = query.filter(or_(*amount_filters))

    if selected_dates:
        date_filters = []
        for r in selected_dates:
            start_date, end_date = parse_date_range(r)
            if start_date and end_date:
                date_filters.append(and_(Expense.date >= start_date, Expense.date <= end_date))
        if date_filters:
            query = query.filter(or_(*date_filters))

    sum_expenses = query.with_entities(func.sum(Expense.amount)).scalar() or 0

    if order_by == "amount_desc":
        query = query.order_by(Expense.amount.desc())
    elif order_by == "amount_asc":
        query = query.order_by(Expense.amount.asc())
    elif order_by == "date_desc":
        query = query.order_by(Expense.date.desc())
    elif order_by == "date_asc":
        query = query.order_by(Expense.date.asc())
    elif order_by == "category_desc":
        query = query.join(Expense_Category).filter(
            or_(Expense_Category.user_id == session["user_id"], Expense_Category.user_id == None)
        ).order_by(Expense_Category.name.desc())
    elif order_by == "category_asc":
        query = query.join(Expense_Category).filter(
            or_(Expense_Category.user_id == session["user_id"], Expense_Category.user_id == None)
        ).order_by(Expense_Category.name.asc())

    expenses = query.all()

    amount_ranges = {
        "0 - 10.000 ₺": "0-10000",
        "10.001 - 50.000 ₺": "10001-50000",
        "50.001 - 250.000 ₺": "50001-250000",
        "250.001 ₺ ve üzeri": "250001-inf"
    }

    date_ranges = {
        "Son 1 Hafta": "1_week",
        "Son 1 Ay": "1_month",
        "Son 3 Ay": "3_month",
        "Son 6 Ay": "6_month",
        "Son 1 Yıl": "1_year",
        "Son 5 Yıl": "5_year"
    }

    return render_template("expense.html", categories=categories,
                           amount_ranges=amount_ranges,
                           date_ranges=date_ranges,
                           form=form,
                           selected_order=selected_order,
                           expenses=expenses,
                           sum_expenses=sum_expenses,
                           selected_categories=selected_categories,
                           selected_amounts=selected_amounts,
                           selected_dates=selected_dates)


@expense_bp.route("/edit_expense/<int:id>", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()

    categories = Expense_Category.query.filter(
        or_(Expense_Category.user_id == session["user_id"], Expense_Category.user_id == None)
    ).all()
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "GET":
        form.amount.data = expense.amount
        form.category.data = expense.category_id
        form.date.data = expense.date
        return render_template("edit_expense.html", form=form, expense=expense)

    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.category_id = form.category.data
        expense.date = form.date.data
        db.session.commit()
        flash("Gider başarıyla güncellendi.", "success")
        return redirect(url_for("expense.expense"))

    flash("Bir hata oluştu.", "danger")
    return render_template("edit_expense.html", form=form, expense=expense)


@expense_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Gider başarıyla silindi.", "success")
    return redirect(url_for("expense.expense"))
