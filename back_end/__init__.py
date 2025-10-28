from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .view import view
    from .auth import auth

    app.register_blueprint(view, url_prefix = "/")
    app.register_blueprint(auth, url_prefix = "/")

    from .models import User, Note

    database(app)

    return app

def database(app):
    if not path.exists("back_end/ " + DB_NAME):
        db.create_all(app = app)
        print("Database Created!")