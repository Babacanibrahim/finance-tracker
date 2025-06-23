from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

app.secret_key="babacanfinans"

app.config["MYSQL_HOST"]= "localhost"
app.config["MYSQL_USER"]= "root"
app.config["MYSQL_PASSWORD"]= ""
app.config["MYSQL_DB"]= "finance_tracker"
app.config["MYSQL_CURSORCLASS"]= "DictCursor"

mysql = MySQL(app)


# Yönlendirmeler
@app.route("/index")
def index():
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
@app.route ("/login")
def login ():
    return render_template("login.html")

#Register
@app.route("/register")
def register():
    return render_template("/register.html")    

#Logout
@app.route("/logout")
def logout():
    return render_template("/logout.html")    

#Flask
if __name__ == '__main__':
    app.run(debug=True)
