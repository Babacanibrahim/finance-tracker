from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

# Ana Sayfa
@main_bp.route("/")
def index():
    return render_template("index.html")

# Hakkımda sayfası
@main_bp.route("/about")
def about():
    return render_template("about.html")
