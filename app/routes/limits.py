from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from sqlalchemy import or_, func

from app import db
from app.models import Budget, BudgetItem, Expense_Category, Expense
from app.forms import BudgetStep1Form, BudgetStep2Form
from app.utils import login_required

limits_bp = Blueprint("limits", __name__)

#Tarih ve isim belirleme
@limits_bp.route("/budget_step_1", methods=["GET", "POST"])
@login_required
def budget_step_1():
    form = BudgetStep1Form()
    if form.validate_on_submit():
        session["budget_name"] = form.name.data
        session["budget_start_date"] = form.start_date.data.isoformat()
        session["budget_end_date"] = form.end_date.data.isoformat()
        return redirect(url_for("limits.budget_step_2"))
    return render_template("budget_step_1.html", form=form)

# Kategori ve tutar belirleme
@limits_bp.route("/budget_step_2", methods=["GET", "POST"])
@login_required
def budget_step_2():
    categories = Expense_Category.query.filter(
        or_(
            Expense_Category.user_id == session["user_id"],
            Expense_Category.user_id == None
        )
    ).all()
    form = BudgetStep2Form()

    if "budget_start_date" not in session or "budget_end_date" not in session:
        flash("Önce tarihleri seçmelisiniz.", "warning")
        return redirect(url_for("limits.budget_step_1"))

    if request.method == "POST" and form.validate():
        budget = Budget(
            user_id=session["user_id"],
            name=session["budget_name"],
            start_date=datetime.fromisoformat(session["budget_start_date"]).date(),
            end_date=datetime.fromisoformat(session["budget_end_date"]).date()
        )
        db.session.add(budget)
        db.session.flush()

        for category in categories:
            amount_str = request.form.get(f"amount_{category.id}")
            if amount_str:
                try:
                    amount = float(amount_str)
                    item = BudgetItem(budget_id=budget.id, category_id=category.id, amount=amount)
                    db.session.add(item)
                except ValueError:
                    continue

        for name, amount_str in zip(request.form.getlist("custom_category[]"), request.form.getlist("custom_amount[]")):
            if name and amount_str:
                try:
                    amount = float(amount_str)
                    custom_name = name.strip()

                    existing_cat = Expense_Category.query.filter_by(
                        name=custom_name,
                        user_id=session["user_id"]
                    ).first()

                    if not existing_cat:
                        new_cat = Expense_Category(name=custom_name, user_id=session["user_id"])
                        db.session.add(new_cat)
                        db.session.flush()
                        category_id = new_cat.id
                    else:
                        category_id = existing_cat.id

                    item = BudgetItem(budget_id=budget.id, category_id=category_id, amount=amount)
                    db.session.add(item)
                except ValueError:
                    continue

        db.session.commit()
        session.pop("budget_start_date", None)
        session.pop("budget_end_date", None)
        session.pop("budget_name", None)

        flash("Bütçe başarıyla oluşturuldu!", "success")
        return redirect(url_for("limits.view_limit", id=budget.id))

    return render_template("budget_step_2.html", form=form, categories=categories)

# Tüm limitler
@limits_bp.route("/budgets")
@login_required
def budgets():
    budgets = Budget.query.filter_by(user_id=session["user_id"]).order_by(Budget.id.desc()).all()
    return render_template("budgets.html", budgets=budgets)

# Bütçe düzenleme tarih ve isim belirleme
@limits_bp.route("/edit_limit_1/<int:id>", methods=["GET", "POST"])
@login_required
def edit_limit(id):
    budget = Budget.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()
    form = BudgetStep1Form()

    if request.method == "GET":
        form.start_date.data = budget.start_date
        form.end_date.data = budget.end_date
        form.name.data = budget.name
    elif form.validate_on_submit():
        session["budget_start_date"] = form.start_date.data.isoformat()
        session["budget_end_date"] = form.end_date.data.isoformat()
        session["budget_name"] = form.name.data
        session["editing_budget_id"] = id
        return redirect(url_for("limits.edit_limit_2"))

    return render_template("edit_limit_1.html", form=form, budget=budget)


# Bütçe düzenleme kategori ve tutar belirleme
@limits_bp.route("/edit_limit_2", methods=["GET", "POST"])
@login_required
def edit_limit_2():
    if "editing_budget_id" not in session:
        flash("Önce bütçe tarihlerini düzenleyin.", "warning")
        return redirect(url_for("dashboard"))

    budget_id = session["editing_budget_id"]
    budget = Budget.query.filter_by(id=budget_id, user_id=session["user_id"]).first_or_404()
    categories = Expense_Category.query.filter(
        or_(
            Expense_Category.user_id == session["user_id"],
            Expense_Category.user_id == None
        )
    ).all()

    form = BudgetStep2Form()

    if request.method == "GET":
        existing_limits = {item.category_id: float(item.amount) for item in budget.items if item.category_id}
        return render_template("edit_limit_2.html", form=form, categories=categories, budget=budget, existing_limits=existing_limits)

    elif form.validate_on_submit():
        budget.start_date = datetime.fromisoformat(session["budget_start_date"]).date()
        budget.end_date = datetime.fromisoformat(session["budget_end_date"]).date()
        budget.name = session.get("budget_name")

        BudgetItem.query.filter_by(budget_id=budget.id).delete()

        for category in categories:
            amount_str = request.form.get(f"amount_{category.id}")
            if amount_str:
                try:
                    db.session.add(BudgetItem(
                        budget_id=budget.id,
                        category_id=category.id,
                        amount=float(amount_str)
                    ))
                except ValueError:
                    continue

        for name, amount_str in zip(request.form.getlist("custom_category[]"), request.form.getlist("custom_amount[]")):
            if name and amount_str:
                try:
                    amount = float(amount_str)
                    custom_name = name.strip()

                    existing_cat = Expense_Category.query.filter_by(name=custom_name, user_id=session["user_id"]).first()
                    if not existing_cat:
                        new_cat = Expense_Category(name=custom_name, user_id=session["user_id"])
                        db.session.add(new_cat)
                        db.session.flush()
                        category_id = new_cat.id
                    else:
                        category_id = existing_cat.id

                    db.session.add(BudgetItem(budget_id=budget.id, category_id=category_id, amount=amount))
                except ValueError:
                    continue

        db.session.commit()
        session.pop("budget_start_date", None)
        session.pop("budget_end_date", None)
        session.pop("editing_budget_id", None)

        flash("Bütçe başarıyla güncellendi!", "success")
        return redirect(url_for("limits.view_limit", id=budget.id))

    return render_template("edit_limit_2.html", form=form, categories=categories, budget=budget, existing_limits={})

# Limit Silme
@limits_bp.route("/delete_limit/<int:id>", methods=["POST"])
@login_required
def delete_limit(id):
    budget = Budget.query.filter_by(id=id, user_id=session["user_id"]).first()
    if budget:
        db.session.delete(budget)
        db.session.commit()
        flash("Bütçe Limit Başarılı Şekilde Silindi", "success")
    else:
        flash("Yetkisiz işlem veya kayıt bulunamadı.", "danger")
    return redirect(url_for("limits.budgets"))

# Limit detay
@limits_bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view_limit(id):
    budget = Budget.query.filter_by(id=id, user_id=session["user_id"]).first()
    if not budget:
        flash("Bütçe bulunamadı veya yetkiniz yok", "warning")
        return redirect(url_for("limits.budget_step_1"))

    expenses = {}
    total_spent_all = 0.0
    total_limit_all = 0.0

    for item in budget.items:
        if item.category_id:
            total_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == session["user_id"],
                Expense.category_id == item.category_id,
                Expense.date >= budget.start_date,
                Expense.date <= budget.end_date
            ).scalar()

            total_spent_all += float(total_spent)
            total_limit_all += float(item.amount)

            percent = float(total_spent) / float(item.amount) * 100 if item.amount > 0 else 0
            expenses[item.id] = {"spent": float(total_spent), "limit": float(item.amount), "percent": round(percent, 2)}
        elif item.custom_category:
            expenses[item.id] = {"spent": None, "limit": float(item.amount), "percent": None}
            total_limit_all += float(item.amount)

    total_percent = (total_spent_all / total_limit_all * 100) if total_limit_all > 0 else 0
    return render_template("view_limit.html", budget=budget, expenses=expenses, total_spent_all=total_spent_all, total_limit_all=total_limit_all, total_percent=round(total_percent, 2))
