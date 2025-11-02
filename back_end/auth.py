from flask import Blueprint, request, json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_user, login_required, current_user
from flask_cors import CORS, cross_origin

auth = Blueprint("auth", __name__)
cors = CORS(auth, resources={r"/api/*": {"origins": "http://localhost:5173/"}})


@cross_origin
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = _read_payload(request)
        
        username = (
            data.get("username")
            or data.get("name")
            or data.get("user")
            or data.get("email")
            or data.get("firstName")
            or ""
        ).strip()
        password = data.get("password") or data.get("password1") or ""

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
            all_users = User.query.with_entities(User.username).all()
            return {
                "status": 406,
                "message": f"Username '{username}' does not exist. Available usernames: {[u[0] for u in all_users]}"
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



def _read_payload(req):
    data = req.get_json(silent=True) or {}
    if not data:
        data = req.form.to_dict() or {}
    if not data and req.data:
        try:
            data = json.loads(req.data.decode("utf-8"))
        except Exception:
            data = {}
    for k, v in req.args.items():
        data.setdefault(k, v)
    return data


@auth.route("/sign-up", methods=["POST"])
@cross_origin()
def sign_up():
    data = _read_payload(request)

    username = (
        data.get("username")
        or data.get("name")
        or data.get("user")
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
        return {"status": 406, "message": "Username already exists."}
    elif len(username) < 4:
        return {"status": 406, "message": "Username must be more than 4 characters."}
    elif len(password1) < 7:
        return {"status": 406, "message": "Password must contain more than 6 characters."}
    elif password1 != password2:
        return {"status": 406, "message": "Password don't match!"}
    new_user = User(username=username, password=generate_password_hash(password1, method="pbkdf2:sha256"))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    return {"status": 200, "message": "Account Created!"}