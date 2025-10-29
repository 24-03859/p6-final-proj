from flask import Blueprint, render_template
from flask_login import login_required, current_user



view = Blueprint("views", __name__)


@view.route("/")
@login_required
def home():
    return render_template("home.html")

