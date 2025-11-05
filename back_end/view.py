from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json
from flask_cors import CORS, cross_origin

view = Blueprint("views", __name__)

@view.route("/rate", methods=["GET", "POST"])
@cross_origin()
@login_required
def home():
    from .models import Feedback, User
    from . import db

    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        raw_rating = data.get("rating")
        print(f"Raw rating value: {raw_rating}, Type: {type(raw_rating)}")
        
        if raw_rating is None:
            return jsonify({
                "status": 400,
                "message": ""
            })
            
        try:
            rating = int(float(raw_rating))
            
            if not (1 <= rating <= 5):
                return jsonify({
                    "status": 400,
                    "message": f"Rating must be between 1 and 5. You sent: {rating}"
                })
        except (ValueError, TypeError) as e:
            return jsonify({
                "status": 400,
                "message": f"Invalid rating value: {raw_rating}. Must be a number between 1 and 5."
            })

        message = (
            data.get("message")
            or data.get("data")
            or data.get("feedback")
            or data.get("content")
            or ""
        ).strip()   

        try:
            new_feedback = Feedback(
                data=message,
                rating=rating,
                user_id=current_user.id
            )
            db.session.add(new_feedback)
            db.session.commit()
            
            return jsonify({
                "status": 200,
                "message": "Feedback Added Successfully!",
                "data": {
                    "message": message,
                    "rating": rating
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": 500,
                "message": "Error saving feedback. Please try again."
            })


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
