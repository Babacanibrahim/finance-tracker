from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100))
    question = db.Column(db.String(100))
    answer = db.Column(db.String(100))
    incomes = db.relationship('Income', backref='user', lazy=True)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    allow_notifications = db.Column(db.Boolean, default=True)


class Income_Category(db.Model):
    __tablename__ = "income_category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    incomes = db.relationship('Income', backref='income_category', lazy=True)

class Expense_Category(db.Model):
    __tablename__ = "expense_category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    expenses = db.relationship('Expense', backref='expense_category', lazy=True)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('income_category.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'), nullable=False)

class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    items = db.relationship("BudgetItem", backref="budget", cascade="all, delete-orphan")

class BudgetItem(db.Model):
    __tablename__ = "budget_items"
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey("budgets.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_category.id"), nullable=True)
    custom_category = db.Column(db.String, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    category = db.relationship("Expense_Category")
