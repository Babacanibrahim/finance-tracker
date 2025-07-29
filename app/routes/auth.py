from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from passlib.hash import sha256_crypt
from app.utils import login_required
from app.forms import (
    RePassword, ChangePassword, ForgotPassword,
    LoginForm, RegisterForm, ProfileEditForm
)
from app.models import User
from app import db


auth_bp = Blueprint("auth", __name__)


# Profil Üzerinden Şifre Değiştirme
@auth_bp.route("/repassword", methods=["GET", "POST"])
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

    return render_template(
        "repassword.html",
        form=form,
        change_form=change_form,
        show_modal=show_modal,
        modal_action=url_for("auth.change_password")
    )

# Profil Düzenleme
@auth_bp.route("/profile", methods=["GET", "POST"])
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
        form.allow_notifications.data = user.allow_notifications

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
            user.allow_notifications = form.allow_notifications.data

            db.session.commit()
            flash("Profil bilgileriniz başarıyla güncellendi.", "success")
            return redirect(url_for("auth.profile"))

        elif action == "password":
            return redirect(url_for("auth.repassword"))

    return render_template("profile.html", form=form)

#Şifre değiştirme
@auth_bp.route("/change_password", methods=["GET", "POST"])
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
                return redirect(url_for("auth.profile"))
            else:
                flash("Şifreler eşleşmiyor.", "danger")
        show_modal = True

    return render_template(
        "repassword.html",
        form=repass_form,
        change_form=form,
        forgot_form=forgot_form,
        show_modal=show_modal,
        modal_action=url_for("auth.change_password")
    )

# Şifremi unuttum
@auth_bp.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPassword()
    change_form = ChangePassword()
    show_modal = False

    if "password" in request.form and "confirm" in request.form:
        if change_form.validate_on_submit():
            username = session.get("username_for_password_reset")
            user = User.query.filter_by(username=username).first()
            if user and change_form.password.data == change_form.confirm.data:
                user.password = sha256_crypt.hash(change_form.password.data)
                db.session.commit()
                session.pop("username_for_password_reset", None)
                flash("Şifreniz başarıyla sıfırlandı.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("Şifreler uyuşmuyor veya hata oluştu.", "danger")
        show_modal = True

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

    return render_template(
        "forgotpassword.html",
        form=form,
        change_form=change_form,
        show_modal=show_modal,
        modal_action=url_for("auth.forgot_password")
    )

# GİRİŞ
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    user = None
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and sha256_crypt.verify(password, user.password):
            flash("Giriş başarılı", "success")
            session["logged_in"] = True
            session["user_id"] = user.id
            return redirect(url_for("main.index"))
        elif user and not sha256_crypt.verify(password, user.password):
            flash("Şifreniz yanlış", "danger")
        else:
            flash("Böyle bir kullanıcı adı bulunamadı.", "danger")

    return render_template("login.html", form=form, user=user)

# Kayıt Ol
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        name = form.name.data
        surname = form.surname.data
        password = sha256_crypt.hash(form.password.data)
        email = form.email.data
        question = form.secret_quest.data
        answer = form.answer.data

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Bu kullanıcı adı daha önceden alınmış.", "danger")
            return render_template("register.html", form=form)
        else:
            new_user = User(
                username=username,
                name=name,
                surname=surname,
                password=password,
                email=email,
                question=question,
                answer=answer,
            )
            db.session.add(new_user)
            db.session.commit()
            session["logged_in"] = True
            session["user_id"] = new_user.id
            flash("Kayıt başarılı! Hoş geldiniz.", "success")
            return redirect(url_for("main.index"))
   
    else:
        return render_template("register.html", form=form)

# Çıkış Yap
@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
