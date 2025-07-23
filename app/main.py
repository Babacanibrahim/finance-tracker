from flask import Flask,render_template,flash,redirect,url_for,session, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, validators, ValidationError, SelectField, DateField, DecimalField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_wtf import FlaskForm
from sqlalchemy import and_, func, or_
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key="babacanfinans"

# Yeni SQLite ayarı
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# User Tablosu DB için
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

# Harcama Kısıtı Tablosu DB için

class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String, nullable=False)  # 👈 Takma ad (hatırlatıcı isim)
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


#Income Category Tablosu DB için
class Income_Category(db.Model):
    __tablename__ = "income_category"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False,unique=True)
    incomes = db.relationship('Income', backref='income_category', lazy=True)

#Expense Category Tablosu DB için
class Expense_Category(db.Model):
    __tablename__ = "expense_category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # 🔸 yeni satır
    expenses = db.relationship('Expense', backref='expense_category', lazy=True)


# Income Tablosu DB için
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount=db.Column(db.Numeric(10,2),nullable=False)
    date=db.Column(db.Date , nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('income_category.id'), nullable=False)

# Expense Tablosu DB için
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount=db.Column(db.Numeric(10,2),nullable=False)
    date=db.Column(db.Date , nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'), nullable=False)


#Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için yetkiniz yok veya giriş yapmamışsınız.","danger")
            return redirect(url_for("login"))
    return decorated_function

#Custom Validators
def length_check_username(form, field):
    if len(field.data) < 3:
        raise ValidationError("En az 3 karakter olmalı.")
    elif len(field.data) > 20:
        raise ValidationError("En fazla 20 karakter olmalı.")
        
def length_check_password(form, field):
    if len(field.data) < 5:
        raise ValidationError("En az 5 karakter olmalı.")
    elif len(field.data) > 20 :
        raise ValidationError("En fazla 20 karakter olmalı.")
    
#Şifre yenileme kullanıcı doğrulama formu
class ForgotPassword(FlaskForm):
    
    #Form
    username=StringField("Kullanıcı adınız : ",validators=[validators.DataRequired()])
    secret_quest=SelectField("Gizli sorunuzu seçiniz :",choices=[("pet","Evcil hayvanınızın adı ?"),("child","Çocuğunuzun adı ?"),("music","En sevdiğiniz müzik türü ?"),("secretkey","Kendinize ait bir gizli anahtar ?")])
    answer=StringField("Gizli sorunun cevabı :")

#Şifre yenileme
class ChangePassword(FlaskForm):

    password=PasswordField("* Parola :",validators=[validators.DataRequired(message="Lütfen bir parola giriniz."),length_check_password,validators.EqualTo("confirm",message="Lütfen parolalarınızı kontrol edin")])
    confirm=PasswordField("* Parolanız tekrar :",validators=[validators.DataRequired(message="Lütfen parolanızı kontrol ediniz.")])

#Şifre Değiştirme
class RePassword(FlaskForm):

    current_password=PasswordField("Mevcut Parola :", validators=[validators.DataRequired("Güncel parolanız gerekli.")])

#Login Form
class LoginForm(FlaskForm):
    
    #Form
    username=StringField(" Kullanıcı adınız :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    password=PasswordField(" Parola :",validators=[validators.DataRequired(message="Parola kısmı boş olamaz.")])

#Register Form
class RegisterForm(FlaskForm):
  
    #Form
    name=StringField("İsim :")
    surname=StringField("Soyisim :")
    username=StringField("* Kullanıcı adınız :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    email=StringField(" E posta :",validators=[validators.optional(),validators.Email(message="Geçerli bir mail adresi giriniz.")])
    secret_quest=SelectField("Gizli sorunuzu seçiniz (şifrenizi unutmanız durumunda kullanılır opsiyoneldir)",choices=[("","Soru seçiniz."),("pet","Evcil hayvanınızın adı ?"),("child","Çocuğunuzun adı ?"),("music","En sevdiğiniz müzik tarzı ?"),("secretkey","Kendinize ait bir gizli anahtar ? (önerilmez)")],validate_choice=False)
    answer=StringField("Gizli sorunun cevabı :")
    password=PasswordField("* Parola :",validators=[validators.DataRequired(message="Parola kısmı boş olamaz."),length_check_password,validators.EqualTo("confirm",message="Lütfen parolalarınızı kontrol edin")])
    confirm=PasswordField("* Parolanız tekrar :",validators=[validators.DataRequired()])

#Profile Edit Form
class ProfileEditForm(FlaskForm):

    #Form
    name=StringField("İsim :")
    surname=StringField("Soyisim :")
    username=StringField("Kullanıcı adı :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    email=StringField("E posta :",validators=[validators.optional(),validators.Email(message="Geçerli bir mail adresi giriniz.")])
    secret_quest=SelectField("Gizli sorunuzu seçiniz (şifrenizi unutmanız durumunda kullanılır opsiyoneldir)",choices=[],validate_choice=False)
    answer=StringField("Gizli sorunun cevabı :")
    password=PasswordField("Mevcut parolanızı girin :")

#Expense Form
class ExpenseForm(FlaskForm):

    #Form
    date=DateField("* Harcama Tarihi",format="%Y-%m-%d",validators=[validators.DataRequired(message="Tarih zorunlu alandır")])
    amount=DecimalField("* Harcama Miktarı (TL olarak)", validators=[validators.DataRequired(message="Harcama miktarı zorunu alandır.")])
    category=SelectField("Harcama Kategorisi", coerce=int)
#Income Form
class IncomeForm(FlaskForm):

    #Form
    date=DateField("* Gelir Tarihi",format="%Y-%m-%d",validators=[validators.DataRequired(message="Tarih zorunlu alandır")])
    amount=DecimalField("* Gelir Miktarı (TL olarak)", validators=[validators.DataRequired(message="Gelir miktarı zorunu alandır.")])
    category=SelectField("Gelir Kategorisi", coerce=int)


#Limit kategorisi belirleme formu
class BudgetStep2Form(FlaskForm):
    other_category_name = StringField("Diğer Kategori Adı", validators=[validators.Optional()])
    other_amount = DecimalField("Diğer Kategori Limiti", validators=[validators.Optional()])

# Tarih Belirleme Formu
class BudgetStep1Form(FlaskForm):
    name = StringField("Harcamanız İçin Hatırlatıcı Bir İsim Belirleyin", validators=[validators.DataRequired()])
    start_date = DateField("Başlangıç Tarihi", format="%Y-%m-%d", validators=[validators.DataRequired()])
    end_date = DateField("Bitiş Tarihi", format="%Y-%m-%d", validators=[validators.DataRequired()])

# Delete Limit Formu (Formalite)
class DeleteForm(FlaskForm):
    pass

# Yönlendirmeler
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

# Otomatik Csrf Token
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

# Güncel Tarih
@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


#Otomatik User Gönderme
@app.context_processor
def inject_user():
    if "user_id" in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        return dict(user = user)
    return dict(user=None)

#Limit seçme adımları
@app.route("/budget_step_1", methods=["GET", "POST"])
@login_required
def budget_step_1():
    form = BudgetStep1Form()
    if form.validate_on_submit():
        session["budget_name"] = form.name.data
        session["budget_start_date"] = form.start_date.data.isoformat()
        session["budget_end_date"] = form.end_date.data.isoformat()
        return redirect(url_for("budget_step_2"))
    return render_template("budget_step_1.html", form=form)


@app.route("/budget_step_2", methods=["GET", "POST"])
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
        return redirect(url_for("budget_step_1"))

    if request.method == "POST" and form.validate():
        budget_name = session["budget_name"]
        start_date = datetime.fromisoformat(session["budget_start_date"]).date()
        end_date = datetime.fromisoformat(session["budget_end_date"]).date()

        # 👇 Budget adını da ekledik
        budget = Budget(
            user_id=session["user_id"],
            name=budget_name,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(budget)
        db.session.flush()

        # Varsayılan kategoriler için BudgetItem
        for category in categories:
            amount_str = request.form.get(f"amount_{category.id}")
            if amount_str:
                try:
                    amount = float(amount_str)
                    item = BudgetItem(
                        budget_id=budget.id,
                        category_id=category.id,
                        amount=amount,
                        custom_category=None,
                    )
                    db.session.add(item)
                except ValueError:
                    continue

        # Özel kategoriler
        custom_categories = request.form.getlist("custom_category[]")
        custom_amounts = request.form.getlist("custom_amount[]")

        for name, amount_str in zip(custom_categories, custom_amounts):
            if name and amount_str:
                try:
                    amount = float(amount_str)
                    custom_name = name.strip()

                    # Aynı isimde kullanıcıya özel kategori var mı kontrol
                    existing_cat = Expense_Category.query.filter_by(
                        name=custom_name,
                        user_id=session["user_id"]
                    ).first()

                    if not existing_cat:
                        new_cat = Expense_Category(
                            name=custom_name,
                            user_id=session["user_id"]
                        )
                        db.session.add(new_cat)
                        db.session.flush()
                        category_id = new_cat.id
                    else:
                        category_id = existing_cat.id

                    # BudgetItem kaydı
                    item = BudgetItem(
                        budget_id=budget.id,
                        category_id=category_id,
                        amount=amount,
                        custom_category=None,  # Hâlâ duruyor
                    )
                    db.session.add(item)
                except ValueError:
                    continue

        db.session.commit()
        session.pop("budget_start_date", None)
        session.pop("budget_end_date", None)
        session.pop("budget_name", None)

        flash("Bütçe başarıyla oluşturuldu!", "success")
        return redirect(url_for("view_limit", id=budget.id))

    return render_template("budget_step_2.html", form=form, categories=categories)


# Tüm Limtileri Gösterme
@app.route("/budgets", methods = ["GET"])
@login_required
def budgets():
    budgets = Budget.query.filter_by(user_id = session["user_id"]).all()
    return render_template("budgets.html" , budgets = budgets)

# ADIM 1: TARİH VE İSİM GÜNCELLEME
@app.route("/edit_limit_1/<int:id>", methods=["GET", "POST"])
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
        return redirect(url_for("edit_limit_2"))

    return render_template("edit_limit_1.html", form=form, budget=budget)

# ADIM 2: KATEGORİ VE BÜTÇE GÜNCELLEME
@app.route("/edit_limit_2", methods=["GET", "POST"])
@login_required
def edit_limit_2():
    if "editing_budget_id" not in session:
        flash("Önce bütçe tarihlerini düzenleyin.", "warning")
        return redirect(url_for("dashboard"))

    budget_id = session["editing_budget_id"]
    budget = Budget.query.filter_by(id=budget_id, user_id=session["user_id"]).first_or_404()

    start_date = datetime.fromisoformat(session["budget_start_date"]).date()
    end_date = datetime.fromisoformat(session["budget_end_date"]).date()
    budget.name = session.get("budget_name")

    categories = Expense_Category.query.filter(
        or_(
            Expense_Category.user_id == session["user_id"],
            Expense_Category.user_id == None
        )
    ).all()

    form = BudgetStep2Form()

    if request.method == "GET":
        existing_limits = {}
        for item in budget.items:
            if item.category_id is not None:
                existing_limits[item.category_id] = float(item.amount)

        return render_template(
            "edit_limit_2.html",
            form=form,
            categories=categories,
            budget=budget,
            existing_limits=existing_limits
        )

    elif request.method == "POST" and form.validate():
        budget.start_date = start_date
        budget.end_date = end_date

        BudgetItem.query.filter_by(budget_id=budget.id).delete()

        for category in categories:
            amount_str = request.form.get(f"amount_{category.id}")
            if amount_str:
                try:
                    amount = float(amount_str)
                    db.session.add(BudgetItem(
                        budget_id=budget.id,
                        category_id=category.id,
                        amount=amount,
                        custom_category=None
                    ))
                except ValueError:
                    continue

        custom_categories = request.form.getlist("custom_category[]")
        custom_amounts = request.form.getlist("custom_amount[]")

        for name, amount_str in zip(custom_categories, custom_amounts):
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

                    db.session.add(BudgetItem(
                        budget_id=budget.id,
                        category_id=category_id,
                        amount=amount,
                        custom_category=None
                    ))
                except ValueError:
                    continue

        db.session.commit()
        session.pop("budget_start_date", None)
        session.pop("budget_end_date", None)
        session.pop("editing_budget_id", None)

        flash("Bütçe başarıyla güncellendi!", "success")
        return redirect(url_for("view_limit", id=budget.id))

    # POST valid değilse veya başka durumlarda tekrar render
    return render_template("edit_limit_2.html", form=form, categories=categories, budget=budget, existing_limits={})

    
#Limit Silme
@app.route("/delete_limit/<int:id>", methods = ["POST"])
@login_required
def delete_limit(id):
    budget = Budget.query.filter_by(id = id , user_id = session["user_id"]).first()
    if budget:
        db.session.delete(budget)
        db.session.commit()
        flash("Bütçe Limit Başarılı Şekilde Silindi","success")
        return redirect(url_for("budgets"))
    
    else:
        flash("Yetkisiz işlem veya kayıt bulunamadı.","danger")
        return redirect(url_for("budgets"))


# Limit Detay
@app.route("/view_limit/<int:id>", methods=["GET"])
@login_required
def view_limit(id):
    budget = Budget.query.filter_by(id=id, user_id=session["user_id"]).first()
    if not budget:
        flash("Bütçe bulunamadı veya yetkiniz yok", "warning")
        return redirect(url_for("budget_step_1"))

    budget_items = budget.items
    expenses = {}

    total_spent_all = 0.0
    total_limit_all = 0.0

    for item in budget_items:
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

            expenses[item.id] = {
                "spent": float(total_spent),
                "limit": float(item.amount),
                "percent": round(percent, 2)
            }

        elif item.custom_category:
            expenses[item.id] = {
                "spent": None,
                "limit": float(item.amount),
                "percent": None
            }

            total_limit_all += float(item.amount)
        total_percent = float(total_spent_all) / float(total_limit_all) * 100 if item.amount > 0 else 0
    return render_template("view_limit.html", budget=budget, expenses=expenses, total_spent_all=total_spent_all, total_limit_all=total_limit_all , total_percent = round(total_percent,2))


# Mevcut Şifreyi Doğrulama
@app.route("/repassword", methods=["GET", "POST"])
@login_required
def repassword():
    form = RePassword()
    change_form = ChangePassword()
    user = User.query.get(session["user_id"])
    show_modal = False

    if form.validate_on_submit():
        if sha256_crypt.verify(form.current_password.data, user.password):
            show_modal = True
        else:
            flash("Mevcut şifreniz yanlış.", "danger")

    return render_template("repassword.html", form=form, change_form=change_form, show_modal=show_modal, modal_action=url_for("change_password"))

# Profil Düzenleme
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])
    form = ProfileEditForm()

    form.secret_quest.choices = [
        ("", "Soru seçiniz."),
        ("pet", "Evcil hayvanınızın adı ?"),
        ("child", "Çocuğunuzun adı ?"),
        ("music", "En sevdiğiniz müzik tarzı ?"),
        ("secretkey", "Kendinize ait bir gizli anahtar ? (önerilmez)")
    ]

    if request.method == "GET":
        form.name.data = user.name
        form.surname.data = user.surname
        form.username.data = user.username
        form.email.data = user.email
        form.secret_quest.data = user.question
        form.answer.data = user.answer

    if form.validate_on_submit():
        action = request.form.get("action")
        if action == "save":
            if form.username.data != user.username:
                existing_user = User.query.filter_by(username=form.username.data).first()
                if existing_user:
                    flash("Bu kullanıcı adı daha önce alınmış. Başka bir kullanıcı adı deneyin.", "danger")
                    return render_template("profile.html", form=form)

            user.name = form.name.data
            user.surname = form.surname.data
            user.username = form.username.data
            user.email = form.email.data
            user.question = form.secret_quest.data
            user.answer = form.answer.data

            db.session.commit()
            flash("Profil bilgileriniz başarıyla güncellendi.", "success")
            return redirect(url_for("profile"))

        elif action == "password":
            return redirect(url_for("repassword"))

    return render_template("profile.html", form=form)

#Gelir Ekleme
@app.route("/income",methods=["GET","POST"])
@login_required
def income():
    form=IncomeForm(request.form)

    categories=Income_Category.query.all()
    form.category.choices = [(c.id , c.name) for c in categories]

    if request.method=="POST" and form.validate():
        new_income=Income(
            category_id = form.category.data,
            amount = form.amount.data,
            date = form.date.data,
            user_id=session["user_id"])
        db.session.add(new_income)
        db.session.commit()
        flash("Gelir başarıyla eklendi","success")
        return redirect(url_for("income"))
    
    # Filtreleme için gelen parametreler
    selected_categories = request.args.getlist("categories[]")
    selected_dates = request.args.getlist("dates[]")
    selected_amounts = request.args.getlist("amounts[]")
    order_by = request.args.get("order_by", "date_desc")
    selected_order = order_by

    #Base query, sadece user bazlı
    query = Income.query.filter(Income.user_id ==session["user_id"])

    #Filtreleme fonksiyonları

    def parse_amount_range(r):
        min_val , max_val = r.split("-")
        max_val = float(max_val) if max_val!= "inf" else None
        return float(min_val), max_val
    
    def parse_date_range(r):
        now = datetime.utcnow().date()
        if r == "1_week":
            start_date = now - timedelta(days=7)
            end_date = now
        elif r == "1_month":
            start_date = now - timedelta(days=30)
            end_date = now
        elif r == "3_month":
            start_date = now - timedelta(days=90)
            end_date = now
        elif r == "6_month":
            start_date = now - timedelta(days=180)
            end_date = now
        elif r == "1_year":
            start_date = now - timedelta(days=365)
            end_date = now
        elif r == "5_year":
            start_date = now - timedelta(days=5*365)
            end_date = now
        else:
            start_date = None
            end_date = None
        return start_date, end_date
    
    #Kategori filtresi
    if selected_categories:
        query = query.filter(Income.category_id.in_(selected_categories))

    # Tutar aralığı filtresi
    if selected_amounts:
        amount_filters = []
        for r in selected_amounts:
            min_val, max_val = parse_amount_range(r)
            if max_val is None:
                amount_filters.append(Income.amount >= min_val)
            else:
                amount_filters.append(and_(Income.amount >= min_val, Income.amount <= max_val))
        query = query.filter(or_(*amount_filters))

    # Tarih aralığı filtresi
    if selected_dates:
        date_filters = []
        for r in selected_dates:
            start_date, end_date = parse_date_range(r)
            if start_date and end_date:
                date_filters.append(and_(Income.date >= start_date, Income.date <= end_date))
        if date_filters:
            query = query.filter(or_(*date_filters))

    # Toplam harcama
    sum_incomes = query.with_entities(func.sum(Income.amount)).scalar() or 0

    #Sıralama
    if order_by == "amount_desc":
        query = query.order_by(Income.amount.desc())
    elif order_by == "amount_asc":
        query = query.order_by(Income.amount.asc())
    elif order_by == "date_desc":
        query = query.order_by(Income.date.desc())
    elif order_by == "date_asc":
        query = query.order_by(Income.date.asc())
    elif order_by == "category_desc":
        query = query.join(Income_Category).order_by(Income_Category.name.desc())
    elif order_by == "category_asc":
        query = query.join(Income_Category).order_by(Income_Category.name.asc())

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

    
    return render_template ("income.html",incomes = incomes, selected_order = selected_order, date_ranges = date_ranges, amount_ranges = amount_ranges, categories = categories, form=form, sum_incomes = sum_incomes, selected_dates = selected_dates, selected_categories = selected_categories, selected_amounts = selected_amounts)

# Gelir Düzenleme
@app.route("/edit_income/<int:id>", methods = ["GET","POST"])
@login_required
def edit_income(id):
    income = Income.query.get(id)
    form = IncomeForm()
    categories = Income_Category.query.all()
    form.category.choices= [(c.id, c.name) for c in categories]

    if request.method == "GET":
        form.amount.data = income.amount
        form.category.data = income.category_id
        form.date.data = income.date
        return render_template("edit_income.html", form = form, income = income)

    elif form.validate_on_submit():
        income.amount = form.amount.data
        income.category_id = form.category.data
        income.date = form.date.data
        db.session.commit()
        flash("Geliriniz güncellenmiştir.","success")
        return redirect(url_for("income"))
    else:
        flash("BİR HATA OLUŞTU.","danger")
    return render_template("edit_income.html", form = form, income = income)

# Gelir Silme
@app.route("/delete_income/<int:id>", methods=["POST"])
@login_required
def delete_income(id):
    income = Income.query.get_or_404(id)
    db.session.delete(income)
    db.session.commit()
    flash("Gelir başarıyla silindi.", "success")
    return redirect(url_for("income"))
    

#Harcama Ekleme

@app.route("/expense", methods=["GET", "POST"])
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
        return redirect(url_for("expense"))

    # Filtreleme için gelen parametreler
    selected_categories = request.args.getlist("categories[]")
    selected_dates = request.args.getlist("dates[]")
    selected_amounts = request.args.getlist("amounts[]")
    order_by = request.args.get("order_by", "date_desc")
    selected_order = order_by

    # Base query, sadece user bazlı
    query = Expense.query.filter(Expense.user_id == session["user_id"])

    # Filtreleme fonksiyonları
    def parse_amount_range(r):
        min_val, max_val = r.split("-")
        max_val = float(max_val) if max_val != "inf" else None
        return float(min_val), max_val

    def parse_date_range(r):
        now = datetime.utcnow().date()
        if r == "1_week":
            start_date = now - timedelta(days=7)
            end_date = now
        elif r == "1_month":
            start_date = now - timedelta(days=30)
            end_date = now
        elif r == "3_month":
            start_date = now - timedelta(days=90)
            end_date = now
        elif r == "6_month":
            start_date = now - timedelta(days=180)
            end_date = now
        elif r == "1_year":
            start_date = now - timedelta(days=365)
            end_date = now
        elif r == "5_year":
            start_date = now - timedelta(days=5*365)
            end_date = now
        else:
            start_date = None
            end_date = None
        return start_date, end_date

    # Kategori filtresi
    if selected_categories:
        query = query.filter(Expense.category_id.in_(selected_categories))

    # Tutar aralığı filtresi
    if selected_amounts:
        amount_filters = []
        for r in selected_amounts:
            min_val, max_val = parse_amount_range(r)
            if max_val is None:
                amount_filters.append(Expense.amount >= min_val)
            else:
                amount_filters.append(and_(Expense.amount >= min_val, Expense.amount <= max_val))
        query = query.filter(or_(*amount_filters))

    # Tarih aralığı filtresi
    if selected_dates:
        date_filters = []
        for r in selected_dates:
            start_date, end_date = parse_date_range(r)
            if start_date and end_date:
                date_filters.append(and_(Expense.date >= start_date, Expense.date <= end_date))
        if date_filters:
            query = query.filter(or_(*date_filters))

    # Toplam harcama
    sum_expenses = query.with_entities(func.sum(Expense.amount)).scalar() or 0

    # Sıralama
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

    return render_template("expense.html",  categories=categories,
                           amount_ranges=amount_ranges,
                           date_ranges=date_ranges,
                           form=form,
                           selected_order=selected_order,
                           expenses=expenses,
                           sum_expenses=sum_expenses,
                           selected_categories=selected_categories,
                           selected_amounts=selected_amounts,
                           selected_dates=selected_dates)


# Harcama Düzenleme
@app.route("/edit_expense<int:id>", methods=["GET","POST"])
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

    elif form.validate_on_submit():
        expense.amount = form.amount.data
        expense.category_id = form.category.data
        expense.date = form.date.data
        db.session.commit()
        flash("Gider başarıyla güncellendi.","success")
        return redirect(url_for("expense"))
    else:
        flash("BİR HATA OLUŞTU.", "danger")
    return render_template("edit_expense.html", form=form, expense=expense)

# Harcama Silme
@app.route("/delete_expense/<int:id>", methods=["POST"])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Gelir başarıyla silindi.", "success")
    return redirect(url_for("expense"))


# Finansal Grafikler Ve Analiz
@app.route("/dashboard")
@login_required
def dashboard():
    incomes = Income.query.filter_by(user_id = session["user_id"]).order_by(Income.date).all()
    expenses = Expense.query.filter_by(user_id = session["user_id"]).order_by(Expense.date).all()

    selected_range = request.args.get("date_range","all")
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

# Yeni Şifre Belirleme
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePassword()
    repass_form = RePassword()
    forgot_form = ForgotPassword()
    user = User.query.get(session["user_id"])
    show_modal = False

    if request.method == "POST":
        if form.validate_on_submit():
            if form.password.data == form.confirm.data:
                user.password = sha256_crypt.hash(form.password.data)
                db.session.commit()
                flash("Şifreniz başarıyla değiştirildi.", "success")
                return redirect(url_for("profile"))
            else:
                flash("Şifreler eşleşmiyor.", "danger")
        show_modal = True

    return render_template("repassword.html", form=repass_form ,change_form=form ,forgot_form=forgot_form ,show_modal=show_modal ,modal_action=url_for("change_password"))


# Şifremi Unuttum - Gizli Soruyu Doğrulama ve Şifre Sıfırlama Modalı
@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPassword()
    change_form = ChangePassword()
    show_modal = False

    # Modal'dan gelen POST (şifre değiştirme)
    if "password" in request.form and "confirm" in request.form:
        if change_form.validate_on_submit():
            username = session.get("username_for_password_reset")
            user = User.query.filter_by(username=username).first()
            if user and change_form.password.data == change_form.confirm.data:
                user.password = sha256_crypt.hash(change_form.password.data)
                db.session.commit()
                session.pop("username_for_password_reset", None)
                flash("Şifreniz başarıyla sıfırlandı.", "success")
                return redirect(url_for("login"))
            else:
                flash("Şifreler uyuşmuyor veya hata oluştu.", "danger")
        show_modal = True  # Hatalı da olsa modal tekrar gösterilsin

    # İlk formdan gelen POST (kullanıcıyı doğrulama)
    elif form.validate_on_submit():
        username = form.username.data
        question = form.secret_quest.data
        answer = form.answer.data

        user = User.query.filter_by(username=username, question=question, answer=answer).first()
        if user:
            session["username_for_password_reset"] = username
            show_modal = True
        else:
            flash("Kullanıcı adı, gizli soru veya yanıt hatalı.", "danger")

    return render_template("forgotpassword.html", form=form, change_form=change_form, show_modal=show_modal, modal_action=url_for("forgot_password"))


#Login 
@app.route ("/login",methods=("GET","POST"))
def login ():
    form=LoginForm(request.form)
    user=None
    if request.method=="POST" and form.validate():
        username=form.username.data
        password=form.password.data

        user = User.query.filter_by(username=username).first()
        if user and sha256_crypt.verify(password, user.password):
            flash("Giriş başarılı","success")
            session["logged_in"]=True
            session["user_id"]=user.id
            return redirect(url_for("index"))
        
        elif user and not sha256_crypt.verify(password, user.password):
                flash("Şifreniz yanlış","danger")
                return render_template("login.html",form=form, user=user)
        else:
            flash("Böyle bir kullanıcı adı bulunamadı.","danger")

    return render_template("login.html",form=form, user = user)

#Register
@app.route("/register",methods=["GET","POST"])
def register():
     form = RegisterForm(request.form)
     if request.method == "POST" and form.validate():
        username = form.username.data
        name=form.name.data
        surname=form.surname.data
        password = sha256_crypt.hash(form.password.data)
        email = form.email.data
        question = form.secret_quest.data
        answer = form.answer.data

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Bu kullanıcı adı daha önceden alınmış.", "danger")
            return render_template("register.html", form = form)
        else:
            new_user = User(username=username, name=name, surname=surname, password=password, email=email, question=question, answer=answer)
            db.session.add(new_user)
            db.session.commit()
            flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
            return redirect(url_for("login"))
     else:
        return render_template("register.html", form=form)
#Logout
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

#Flask
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        expense_categories = ["Kredi Ödemesi", "Borç", "Yeme - içme", "Ulaşım", "Yatırım", "Eğlence", "Sağlık", "Kira", "Eğitim"]

        income_categories = ["Maaş", "Kredi", "Ödenek", "Borç geri ödeme", "Yatırım", "İş","Diğer"]

        if not Income_Category.query.first():
            for name in income_categories:
                db.session.add(Income_Category(name=name))
            db.session.commit()

        if not Expense_Category.query.first():
            for name in expense_categories:
                db.session.add(Expense_Category(name=name))
            db.session.commit()

    app.run(debug=True)