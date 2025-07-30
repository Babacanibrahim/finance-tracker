from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "babacanfinans"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Blueprint importları
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.income import income_bp
from app.routes.expense import expense_bp
from app.routes.limits import limits_bp
from app.context_processors import context_bp
from app.routes.main import main_bp
from app.routes.notifications import notifications_bp

# Blueprint kayıtları
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(income_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(limits_bp)
app.register_blueprint(context_bp)
app.register_blueprint(main_bp)
app.register_blueprint(notifications_bp)