from functools import wraps
from flask import session, flash, redirect, url_for

# Giriş kontrolü (decorator)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için yetkiniz yok veya giriş yapmamışsınız.", "danger")
            return redirect(url_for("auth.login"))
    return decorated_function