from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json
from flask_cors import CORS, cross_origin

view = Blueprint("views", __name__)

@view.route("/", methods=["GET", "POST"])
@cross_origin()
@login_required
def home():
    from .models import Feedback, User
    from . import db

    if request.method == "POST":
        print("Content-Type:", request.headers.get('Content-Type'))
        print("Is JSON?", request.is_json)

        if request.is_json:
            data = request.get_json() #-----> nagamit parin naman nung nilagay mo, nangyari lang parehas form at yung sayo
            print("JSON Data:", data)
        else:
            data = request.form  # ------> ETO SIR!!!
            print("Form Data:", dict(data))
        
        message = (
            data.get("message")  # if frontend sends { message: "..." }
            or data.get("data")  # if frontend sends { data: "..." }
            or data.get("feedback")  # if frontend sends { feedback: "..." }
            or data.get("note")  # if frontend sends { note: "..." }
            or ""
        )

        rating = data.get("rating")

        if not message:
            return jsonify({"status": 400, "message": "No feedback message provided."})
        else:
            new_feedback = Feedback(data=message, rating=rating, user_id=current_user.id)
            db.session.add(new_feedback)
            db.session.commit()
            return {
                "status": 200,
                "message": "Feedback Added!"
            }


# @view.route("/delete-note", methods=["POST"])
# @cross_origin()
# def delete_note():
#     # request.data is a bytes object; parse JSON safely and handle errors.
#     try:
#         data = json.loads(request.data)
#     except Exception:
#         # Return a client error if JSON is invalid.
#         return {"error": "invalid request"}, 400

#     # The original code mistakenly accessed Note.data["noteID"].
#     # `Note` is the model class; `Note.data` is a Column descriptor, not
#     # the incoming JSON. We must read the note ID from the parsed JSON.
#     note_id = data.get("noteID") or data.get("noteId")
#     if not note_id:
#         return {"error": "missing note id"}, 400

#     # Import Note and db here to avoid ImportError during module import.
#     from .models import Note
#     from . import db

#     note = Note.query.get(note_id)
#     if not note:
#         return {"error": "note not found"}, 404

#     # Ensure the logged-in user owns the note before deleting.
#     if note.user_id != current_user.id:
#         return {"error": "unauthorized"}, 403

#     db.session.delete(note)
#     db.session.commit()
#     return jsonify({})
