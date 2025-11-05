from flask import Flask, Blueprint

leaderboard = Blueprint("leaderboard", __name__)

@leaderboard.route("/", methods=["GET", "POST"])
def leaderboards():
    from . import db
    from .models import User, Score



# sir owen are ay uumpisahan ko palang