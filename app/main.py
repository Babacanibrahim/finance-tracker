from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,ValidationError
from passlib.hash import sha256_crypt
from functools import wraps
from flask_wtf import FlaskForm

app = Flask(__name__)

app.secret_key="babacanfinans"

app.config["MYSQL_HOST"]= "localhost"
app.config["MYSQL_USER"]= "root"
app.config["MYSQL_PASSWORD"]= ""
app.config["MYSQL_DB"]= "finance_tracker"
app.config["MYSQL_CURSORCLASS"]= "DictCursor"

mysql = MySQL(app)

#Custom Validators
def length_check_username(form, field):
    if len(field.data) < 3:
        raise ValidationError("En az 3 karakter olmalı.")
    elif len(field.data) > 20:
        raise ValidationError("En fazla 20 karakter olmalı.")
        
def length_check_password(form, field):
    if len(field.data) < 5:
        raise ValidationError("En az 3 karakter olmalı.")
    elif len(field.data) > 20 :
        raise ValidationError("En fazla 5 karakter olmalı.")

#Login Form
class LoginForm(FlaskForm):
    
    #Form
    username=StringField(" Kullanıcı adınız :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    password=PasswordField(" Parola :",validators=[validators.DataRequired(message="Parola kısmı boş olamaz.")])

#Register Form
class RegisterForm(FlaskForm):
  
    #Form
    username=StringField("* Kullanıcı adınız :",validators=[length_check_username,validators.DataRequired(message="Kullanıcı adı boş olamaz.")])
    email=StringField(" E posta :",validators=[validators.Email(message="Geçerli bir mail adresi giriniz.")])
    password=PasswordField("* Parola :",validators=[validators.DataRequired(message="Parola kısmı boş olamaz."),length_check_password,validators.EqualTo("confirm",message="Lütfen parolalarınızı kontrol edin")])
    confirm=PasswordField("* Parolanız tekrar :",validators=[validators.DataRequired()])

# Yönlendirmeler
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index")
def main_board():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/income")
def income():
    return render_template ("income.html")

@app.route("/expense")
def expense():
    return render_template ("expense.html")

#Login 
@app.route ("/login",methods=("GET","POST"))
def login ():
    form=LoginForm(request.form)
    if request.method=="POST" and form.validate():
        cursor=mysql.connection.cursor()
        query="SELECT * FROM users WHERE username=%s"
        result=cursor.execute(query,(form.username.data,))

        if result>0:
            user=cursor.fetchone()
            if not sha256_crypt.verify(form.password.data, user["password"]):
                flash("Şifreniz yanlış","danger")
                cursor.close()
                return render_template("login.html",form=form)
            else:
                flash("Giriş başarılı","success")
                cursor.close()
                return redirect(url_for("index"))
                

        else:
            flash("Böyle bir kullanıcı adı bulunamadı.","danger")
            cursor.close()
    cursor.close()
    return render_template("login.html",form=form)

#Register
@app.route("/register",methods=["GET","POST"])
def register():
    form=RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        cursor=mysql.connection.cursor()
        query="INSERT INTO users (username , email , password) VALUES (%s,%s,%s)"
        query_exist="SELECT * FROM users WHERE username=%s"

        username=form.username.data
        email=form.email.data
        password=sha256_crypt.hash(form.password.data)

        result=cursor.execute(query_exist,(username,))

        if result>0:
            flash("Böyle bir isme sahip kullanıcı mevcut. Şifrenizi unuttuysanız şifremi unuttum'la devam edebilirsiniz.","danger")
            return render_template("register.html")
    
        else:
            cursor.execute(query,(username,email,password))
            mysql.connection.commit()
            cursor.close()
            flash("Kaydınız başarıyla oluşturuldu.","success")
            return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)

#Logout
@app.route("/logout")
def logout():
    return render_template("/logout.html")

#Flask
if __name__ == '__main__':
    app.run(debug=True)