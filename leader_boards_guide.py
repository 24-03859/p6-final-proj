"""
Simple Leaderboard Implementation Guide
------------------------------------

This guide shows how to implement a basic leaderboard system with just username, rank, and points
using Flask. The system works without a frontend and can be tested using Postman.

Your models.py is already set up correctly with the User and Score models, so let's implement
the leaderboard functionality:

Implementation Steps:
-------------------

1. In leaderboards.py, implement these routes:

```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Score, User

leaderboard = Blueprint("leaderboard", __name__)

# Submit a new score
@leaderboard.route("/submit-score", methods=["POST"])
@login_required
def submit_score():
    try:
        data = request.get_json()
        
        if not data or 'score' not in data:
            return jsonify({
                "status": 400,
                "message": "Score is required"
            })
            
        new_score = Score(
            user_id=current_user.id,
            score=data['score']
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        return jsonify({
            "status": 200,
            "message": "Score submitted successfully",
            "data": {
                "score": new_score.score
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": 500,
            "message": f"Error submitting score: {str(e)}"
        })

# Get the leaderboard
@leaderboard.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        # Get top scores for each user
        subquery = db.session.query(
            Score.user_id,
            db.func.max(Score.score).label('max_score')
        ).group_by(Score.user_id).subquery()
        
        # Join with User table and order by score
        leaderboard_data = db.session.query(
            User.username,
            subquery.c.max_score.label('points')
        ).join(
            subquery,
            User.id == subquery.c.user_id
        ).order_by(
            subquery.c.max_score.desc()
        ).all()
        
        # Add ranking
        ranked_data = []
        for rank, (username, points) in enumerate(leaderboard_data, 1):
            ranked_data.append({
                "rank": rank,
                "username": username,
                "points": points
            })
            
        return jsonify({
            "status": 200,
            "data": ranked_data
        })
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Error fetching leaderboard: {str(e)}"
        })

# Get current user's best score and rank
@leaderboard.route("/my-rank", methods=["GET"])
@login_required
def get_my_rank():
    try:
        # Get user's best score
        best_score = db.session.query(
            db.func.max(Score.score)
        ).filter_by(
            user_id=current_user.id
        ).scalar()

        if not best_score:
            return jsonify({
                "status": 200,
                "data": {
                    "username": current_user.username,
                    "rank": None,
                    "points": 0
                }
            })

        # Count how many users have a better score
        better_scores = db.session.query(
            db.func.count(db.distinct(Score.user_id))
        ).filter(
            Score.score > best_score
        ).scalar()

        return jsonify({
            "status": 200,
            "data": {
                "username": current_user.username,
                "rank": better_scores + 1,
                "points": best_score
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Error fetching rank: {str(e)}"
        })
```

Testing with Postman:
-------------------

1. Submit a Score:
   - Method: POST
   - URL: http://localhost:5000/submit-score
   - Headers: 
     * Content-Type: application/json
   - Body: 
     ```json
     {
         "score": 100
     }
     ```
   - Auth: Must be logged in (send session cookie)

2. View Leaderboard:
   - Method: GET
   - URL: http://localhost:5000/leaderboard
   - No authentication required
   - Returns: List of players with rank, username, and points

3. Check Your Rank:
   - Method: GET
   - URL: http://localhost:5000/my-rank
   - Auth: Must be logged in (send session cookie)
   - Returns: Your username, rank, and best score

Features of this Implementation:
-----------------------------
1. Only stores the best score for each player
2. Automatically calculates ranks
3. Works without frontend
4. Can be tested with Postman
5. Includes proper error handling
6. Uses authentication for score submission

Important Notes:
--------------
1. Make sure users are logged in before submitting scores
2. The leaderboard shows only the best score for each player
3. Ranks are calculated dynamically
4. Error handling is included for all operations
5. All responses are in JSON format for easy integration
"""