from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json

# NOTE: Importing models at module import time can sometimes trigger
# circular-import problems (ImportError) in Flask apps where the package
# `back_end` initializes `db` and registers blueprints in `create_app()`.
# To avoid that, import the `Note` model (and package `db`) inside the
# request-handling functions where they're actually needed.

view = Blueprint("views", __name__)

# NOTE: The correct Flask parameter name is `methods` (plural).
# Using `method=[...]` will raise TypeError: unexpected keyword argument 'method'.
@view.route("/", methods=["GET", "POST"])
@login_required
def home():
    # Import models and db here to avoid circular-import / ImportError when
    # the module is imported during app startup.
    from .models import Note
    from . import db

    if request.method == "POST":
        # request.form.get may return None if 'note' isn't supplied.
        # Guard against that to avoid TypeError from len(None).
        note = request.form.get("note") or ""

        if len(note) < 1:
            flash("Note too short!", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Note Added!", category="success")

    return render_template("home.html", user=current_user)


# NOTE: Defining two routes with the same path `/` (one for GET/POST and
# another for delete) causes routing conflicts. Use a distinct endpoint
# for delete actions and the correct `methods` keyword.
@view.route("/delete-note", methods=["POST"])
def delete_note():
    # request.data is a bytes object; parse JSON safely and handle errors.
    try:
        data = json.loads(request.data)
    except Exception:
        # Return a client error if JSON is invalid.
        return {"error": "invalid request"}, 400

    # The original code mistakenly accessed Note.data["noteID"].
    # `Note` is the model class; `Note.data` is a Column descriptor, not
    # the incoming JSON. We must read the note ID from the parsed JSON.
    note_id = data.get("noteID") or data.get("noteId")
    if not note_id:
        return {"error": "missing note id"}, 400

    # Import Note and db here to avoid ImportError during module import.
    from .models import Note
    from . import db

    note = Note.query.get(note_id)
    if not note:
        return {"error": "note not found"}, 404

    # Ensure the logged-in user owns the note before deleting.
    if note.user_id != current_user.id:
        return {"error": "unauthorized"}, 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({})
