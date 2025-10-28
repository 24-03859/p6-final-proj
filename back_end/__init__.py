from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret_key"

    from .view import view
    from .auth import auth

    app.register_blueprint(view, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app