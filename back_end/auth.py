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
        # Accept either 'username' or 'email' (templates use 'email')
        username = (
            request.form.get("username")
            or request.form.get("email")
            or request.form.get("firstName")
            or ""
        ).strip()
        password = request.form.get("password")

        from .models import User
        from . import db

        user = User.query.filter_by(username=username).first()
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
        # Templates use 'email' and 'firstName' for the name fields.
        # Accept either 'username' or 'email' (or 'firstName') to be resilient.
        data = request.json
        username = data.get("username") or ""
            
        password1 = data.get("password1") or ""
        password2 = data.get("password2") or ""

        from .models import User
        from . import db

        user = User.query.filter_by(username=username).first()

        if user:
            # flash("Email Already Exist!", category="error")
            return {
                "status": 406,
                "message": "Username Already Exist!"
            }
        # Validate username after normalizing to empty-string when missing.
        elif len(username) < 4:
            # flash("Email must be more than 4 characters.", category="error")
            return {
                "status": 406,
                "message": "Username must be more than 4 characters."
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
            user = User.query.filter_by(username=username).first()
            if user:
                # flash('Email already exists.', category='error')
                return {
                    "status": 406,
                    "message": "Username already exists."
                }
            else:
                new_user = User(username=username, password=generate_password_hash(password1, method="pbkdf2:sha256"))
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