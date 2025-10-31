from flask import Blueprint, request
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_user, login_required, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
               # flash("Account logged in Successfully!", category="success")
                login_user(user, remember=True)
                return {
                    "status": 200,
                    "message": "Account logged in Successfully!"
                }
            else:
                # flash("Incorrect Password!", category="error")
                return {
                    "status": 406,
                    "message": "Incorrect Password!"
                }
        else:
            # flash("Email does not exist.", category="error")
            return {
                "status": 406,
                "message": "Email does not exist"
            }
        
    # return render_template("login.html", user=current_user)
    return {
        "status": 200,
        "message": "Logged In Successfully!"
    }

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return {
        "status": 200,
        "message": "Logged out Successfully!"
    }

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()

        if user:
            # flash("Email Already Exist!", category="error")
            return {
                "status": 406,
                "message": "Email Already Exist!"
            }
        elif len(email) < 4:
            # flash("Email must be more than 4 characters.", category="error")
            return {
                "status": 406,
                "message": "Email must be more than 4 characters."
            }
        elif len(first_name) < 2:
            # flash("First Name should atleast contain 2 characters.", category="error")
            return {
                "status": 406,
                "message": "First Name should atleast contain 2 characters."
            }
        elif len(password1) < 7:
            # flash("password must contain more than 6 characters.", category="error")
            return {
                "status": 406,
                "message": "Password must contain more than 6 characters."
            }
        elif password1 != password2:
            # flash("Passwords don't match!", category="error")
            return {
                "status": 406,
                "message": "Password don't match!"
            }
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                # flash('Email already exists.', category='error')
                return {
                    "status": 406,
                    "message": "Email already exists."
                }
            else:
                new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="pbkdf2:sha256"))
                db.session.add(new_user)    
                db.session.commit()
                login_user(new_user, remember=True)
                # flash("Account Created!", category="success")
                return {
                    "status": 200,
                    "message": "Done Creating Account!"
                }

    # return render_template("sign_up.html", user=current_user)
    return {
        "status": 200,
        "message": "Account Created"
    }