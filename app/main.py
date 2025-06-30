from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,ValidationError,SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_wtf import FlaskForm

app = Flask(__name__)

app.secret_key="babacanfinans"


#Mysql konfigürasyonları
"""
app.config["MYSQL_HOST"]= "localhost"
app.config["MYSQL_USER"]= "root"
app.config["MYSQL_PASSWORD"]= ""
app.config["MYSQL_DB"]= "finance_tracker"
app.config["MYSQL_CURSORCLASS"]= "DictCursor"

mysql = MySQL(app)"""


# Yeni SQLite ayarı
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# User Tablosu DB için
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100))
    question = db.Column(db.String(100))
    answer = db.Column(db.String(100))

# Expense Tablosu DB için
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category=db.Column(db.String(50))
    amount=db.Column(db.Numeric(10,2),nullable=False)
    date=db.Column(db.DateTime , nullable=False)

# Income Tablosu DB için
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category=db.Column(db.String(50))
    amount=db.Column(db.Numeric(10,2),nullable=False)
    date=db.Column(db.DateTime , nullable=False)


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

#Login Form
class LoginForm(FlaskForm):
    
    #Form
    username=StringField(" Kullanıcı adınız :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    password=PasswordField(" Parola :",validators=[validators.DataRequired(message="Parola kısmı boş olamaz.")])

#Register Form
class RegisterForm(FlaskForm):
  
    #Form
    username=StringField("* Kullanıcı adınız :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    email=StringField(" E posta :",validators=[validators.optional(),validators.Email(message="Geçerli bir mail adresi giriniz.")])
    secret_quest=SelectField("Gizli sorunuzu seçiniz (şifrenizi unutmanız durumunda kullanılır opsiyoneldir)",choices=[("","Soru seçiniz."),("pet","Evcil hayvanınızın adı ?"),("child","Çocuğunuzun adı ?"),("music","En sevdiğiniz müzik türü ?"),("secretkey","Kendinize ait bir gizli anahtar ? (önerilmez)")],validate_choice=False)
    answer=StringField("Gizli sorunun cevabı :")
    password=PasswordField("* Parola :",validators=[validators.DataRequired(message="Parola kısmı boş olamaz."),length_check_password,validators.EqualTo("confirm",message="Lütfen parolalarınızı kontrol edin")])
    confirm=PasswordField("* Parolanız tekrar :",validators=[validators.DataRequired()])

# Yönlendirmeler
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/income")
@login_required
def income():
    return render_template ("income.html")

@app.route("/expense")
@login_required
def expense():
    return render_template ("expense.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

#Şifre Yenileme
@app.route("/change_password",methods=["POST","GET"])
def change_password():
    form=ChangePassword(request.form)

    if form.validate_on_submit():
        username=session.get("username_for_password_reset")
        if not username:
            flash("İşlem için doğrulama yapmalısınız.","danger")
            return redirect(url_for("forgotpassword"))
        
        user=User.query.filter_by(username=username).first()

        if user:
            user.password=sha256_crypt.hash(form.password.data)
            db.session.commit()
            flash("Şifreniz başarıyla değiştirildi","success")
            return redirect(url_for("login"))
        else :
            flash("Kullanıcı bulunamadı.","danger")
            return redirect(url_for("forgotpassword"))
    else:
        flash("Bir hata oluştu. Daha sonra tekrar deneyiniz.","danger")
        return redirect(url_for("forgotpassword"))

#Şifremi unuttum
@app.route("/forgotpassword",methods=["GET","POST"])
def forgot_password():
    form=ForgotPassword(request.form)
    show_modal = False
    change_form = ChangePassword()
    if request.method=="POST" and form.validate():
        
        username=form.username.data
        question=form.secret_quest.data
        answer=form.answer.data

        user=User.query.filter_by(username=username , answer=answer , question=question).first()
        answer_error=User.query.filter(User.username==username , User.answer!=answer , User.question==question).first()
        question_error=User.query.filter(User.username==username , User.answer==answer , User.question!=question).first()

        if user :
            session["username_for_password_reset"] = username
            show_modal = True
        
        elif answer_error:
            flash("Gizli sorunun yanıtı hatalı.","danger")

        elif question_error:
            flash("Gizli soru hatalı.","danger")

        else:
            flash("Böyle bir kullanıcı maalesef bulunamadı.","danger")

    return render_template("forgotpassword.html",form=form, change_form=change_form, show_modal=show_modal)

#Login 
@app.route ("/login",methods=("GET","POST"))
def login ():
    form=LoginForm(request.form)
    if request.method=="POST" and form.validate():
        username=form.username.data
        password=form.password.data

        user = User.query.filter_by(username=username).first()
        if user and sha256_crypt.verify(password, user.password):
            flash("Giriş başarılı","success")
            session["logged_in"]=True
            session["username"]=username
            return redirect(url_for("index"))
        
        elif user and not sha256_crypt.verify(password, user.password):
                flash("Şifreniz yanlış","danger")
                return render_template("login.html",form=form)
        else:
            flash("Böyle bir kullanıcı adı bulunamadı.","danger")

    return render_template("login.html",form=form)

#Register
@app.route("/register",methods=["GET","POST"])
def register():
     form = RegisterForm(request.form)
     if request.method == "POST" and form.validate():
        username = form.username.data
        password = sha256_crypt.hash(form.password.data)
        email = form.email.data
        question = form.secret_quest.data
        answer = form.answer.data

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Bu kullanıcı adı daha önceden alınmış.", "danger")
        else:
            new_user = User(username=username, password=password, email=email, question=question, answer=answer)
            db.session.add(new_user)
            db.session.commit()
            flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
            return redirect(url_for("login"))
     else:
        return render_template("register.html", form=form)
#Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#Flask
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)