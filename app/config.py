import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///finance_tracker.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
