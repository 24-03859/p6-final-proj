from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_user, login_required, current_user
from flask_cors import CORS, cross_origin

auth = Blueprint("auth", __name__)
cors = CORS(auth, resources={r"/api/*": {"origins": "http://localhost:5173/"}})
@cross_origin
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.is_json: #----------> ETO DIN!
            data = request.get_json()
        else:
            data = request.form

        username = (
            data.get("username")
            or data.get("email")
            or data.get("firstName")
            or ""
        ).strip()
        password = data.get("password") or ""

        from .models import User
        from . import db

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return {
                    "status": 200,
                    "message": "Account logged in Successfully!"
                }
            else:
                return {
                    "status": 406,
                    "message": "Incorrect Password!"
                }
        else:
            return {
                "status": 406,
                "message": "Email does not exist"
            }
        

@cross_origin
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return {
        "status": 200,
        "message": "Logged out Successfully!"
    }

@auth.route("/sign-up", methods=["GET", "POST"])
@cross_origin()
def sign_up():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        username = (
            data.get("username")
            or data.get("email")
            or data.get("firstName")
            or ""
        ).strip()
        password1 = data.get("password1") or data.get("password") or ""
        password2 = data.get("password2") or data.get("passwordConfirm") or password1 or ""

        from .models import User
        from . import db

        user = User.query.filter_by(username=username).first()

        if user:
            return {
                "status": 406,
                "message": "Username Already Exist!"
            }
        elif len(username) < 4:
            return {
                "status": 406,
                "message": "Username must be more than 4 characters."
            }
        elif len(password1) < 7:
            return {
                "status": 406,
                "message": "Password must contain more than 6 characters."
            }
        elif password1 != password2:
            return {
                "status": 406,
                "message": "Password don't match!"
            }
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                return {
                    "status": 406,
                    "message": "Username already exists."
                }
            else:
                new_user = User(username=username, password=generate_password_hash(password1, method="pbkdf2:sha256"))
                db.session.add(new_user)    
                db.session.commit()
                login_user(new_user, remember=True)
                return {
                    "status": 200,
                    "message": "Account Created!"
                }