from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

from app import db
from app.models import Income, Income_Category
from app.forms import IncomeForm
from app.utils import login_required

income_bp = Blueprint("income", __name__)


@income_bp.route("/income", methods=["GET", "POST"])
@login_required
def income():
    form = IncomeForm(request.form)
    categories = Income_Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "POST" and form.validate():
        new_income = Income(
            category_id=form.category.data,
            amount=form.amount.data,
            date=form.date.data,
            user_id=session["user_id"]
        )
        db.session.add(new_income)
        db.session.commit()
        flash("Gelir başarıyla eklendi", "success")
        return redirect(url_for("income.income"))

    # Filtreleme
    selected_categories = request.args.getlist("categories[]")
    selected_dates = request.args.getlist("dates[]")
    selected_amounts = request.args.getlist("amounts[]")
    order_by = request.args.get("order_by", "date_desc")
    selected_order = order_by

    query = Income.query.filter(Income.user_id == session["user_id"])

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

    # Kategori filtreleme
    if selected_categories:
        query = query.filter(Income.category_id.in_(selected_categories))

    # Miktar filtreleme
    if selected_amounts:
        filters = []
        for r in selected_amounts:
            min_val, max_val = parse_amount_range(r)
            if max_val is None:
                filters.append(Income.amount >= min_val)
            else:
                filters.append(and_(Income.amount >= min_val, Income.amount <= max_val))
        query = query.filter(or_(*filters))

    # Tarih filtreleme
    if selected_dates:
        filters = []
        for r in selected_dates:
            start_date, end_date = parse_date_range(r)
            if start_date and end_date:
                filters.append(and_(Income.date >= start_date, Income.date <= end_date))
        if filters:
            query = query.filter(or_(*filters))

    # Toplam gelir
    sum_incomes = query.with_entities(func.sum(Income.amount)).scalar() or 0

    # Sıralama
    order_map = {
        "amount_desc": Income.amount.desc(),
        "amount_asc": Income.amount.asc(),
        "date_desc": Income.date.desc(),
        "date_asc": Income.date.asc(),
        "category_desc": (Income_Category.name.desc(), True),
        "category_asc": (Income_Category.name.asc(), True),
    }
    if order_by in order_map:
        order_value = order_map[order_by]
        if isinstance(order_value, tuple) and order_value[1]:
            query = query.join(Income_Category).order_by(order_value[0])
        else:
            query = query.order_by(order_value)

    incomes = query.all()

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

    return render_template(
        "income.html",
        incomes=incomes,
        selected_order=selected_order,
        date_ranges=date_ranges,
        amount_ranges=amount_ranges,
        categories=categories,
        form=form,
        sum_incomes=sum_incomes,
        selected_dates=selected_dates,
        selected_categories=selected_categories,
        selected_amounts=selected_amounts
    )


@income_bp.route("/edit_income/<int:id>", methods=["GET", "POST"])
@login_required
def edit_income(id):
    income = Income.query.get(id)
    form = IncomeForm()
    categories = Income_Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "GET":
        form.amount.data = income.amount
        form.category.data = income.category_id
        form.date.data = income.date
        return render_template("edit_income.html", form=form, income=income)

    if form.validate_on_submit():
        income.amount = form.amount.data
        income.category_id = form.category.data
        income.date = form.date.data
        db.session.commit()
        flash("Geliriniz güncellenmiştir.", "success")
        return redirect(url_for("income.income"))

    flash("Bir hata oluştu.", "danger")
    return render_template("edit_income.html", form=form, income=income)


@income_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_income(id):
    income = Income.query.get_or_404(id)
    db.session.delete(income)
    db.session.commit()
    flash("Gelir başarıyla silindi.", "success")
    return redirect(url_for("income.income"))
