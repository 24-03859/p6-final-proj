# LIVE LEADERBOARD IMPLEMENTATION GUIDE FOR LOCAL GAME
# ====================================================
#
# This guide shows how to implement a live leaderboard that:
# - Shows ONLY the current_user's rank and position
# - Saves all previous users' scores in the database
# - Breaks ties: if users have the same score, the one who finished more recently gets higher rank
#
# SETUP INSTRUCTIONS:
# ===================
# 1. Make sure your models.py already has the Score model (it should be there)
# 2. Create or edit leaderboards.py in your back_end folder
# 3. Copy the code blocks below (uncommented) into leaderboards.py
# 4. Make sure the blueprint is registered in __init__.py
# 5. Test using Postman or your frontend
#
# IMPORTANT NOTES:
# - This is for LOCAL games (not deployed)
# - The leaderboard only shows the current_user's rank
# - All scores are saved but only current_user sees their position
# - Tie-breaking: More recent completion = Higher rank when scores are equal


# ============================================================
# STEP 1: IMPORTS AND BLUEPRINT SETUP
# ============================================================
# Add these imports at the top of your leaderboards.py file:

# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from sqlalchemy import desc, func
# from datetime import datetime
# from . import db
# from .models import Score, User

# leaderboard = Blueprint("leaderboard", __name__)


# ============================================================
# STEP 2: TO SUBMIT/SAVE SCORE
# ============================================================
# This endpoint saves the current_user's score to the database.
# All scores are saved, even from previous users.

# @leaderboard.route("/submit-score", methods=["POST"])
# @login_required
# def submit_score():
#     """
#     Saves the current_user's score to the database.
#     Test in Postman:
#     POST http://localhost:5000/submit-score
#     Headers: 
#         Content-Type: application/json
#     Body:
#         {
#             "score": 100
#         }
#     """
#     try:
#         # Get score from request
#         data = request.get_json()
        
#         if not data or 'score' not in data:
#             return jsonify({
#                 "status": 400,
#                 "message": "Score is required"
#             }), 400
            
#         # Validate score is an integer
#         try:
#             score = int(data['score'])
#             if score < 0:
#                 return jsonify({
#                     "status": 400,
#                     "message": "Score must be a positive integer"
#                 }), 400
#         except (TypeError, ValueError):
#             return jsonify({
#                 "status": 400,
#                 "message": "Score must be an integer"
#             }), 400
        
#         # Create and save new score with current timestamp
#         new_score = Score(
#             score=score,
#             user_id=current_user.id,
#             date=datetime.utcnow()
#         )
        
#         db.session.add(new_score)
#         db.session.commit()
        
#         return jsonify({
#             "status": 200,
#             "message": "Score submitted successfully",
#             "data": {
#                 "score": score,
#                 "date": new_score.date.isoformat(),
#                 "username": current_user.username
#             }
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             "status": 500,
#             "message": f"Error submitting score: {str(e)}"
#         }), 500


# ============================================================
# STEP 3: TO GET CURRENT_USER'S BEST SCORE
# ============================================================
# This endpoint gets the current_user's best (highest) score.

# @leaderboard.route("/my-best-score", methods=["GET"])
# @login_required
# def get_my_best_score():
#     """
#     Gets the current_user's best (highest) score.
#     Test in Postman:
#     GET http://localhost:5000/my-best-score
#     """
#     try:
#         # Get user's best score
#         best_score = db.session.query(
#             func.max(Score.score)
#         ).filter_by(
#             user_id=current_user.id
#         ).scalar()
        
#         if best_score is None:
#             return jsonify({
#                 "status": 200,
#                 "data": {
#                     "username": current_user.username,
#                     "best_score": 0,
#                     "message": "No scores yet"
#                 }
#             }), 200
        
#         return jsonify({
#             "status": 200,
#             "data": {
#                 "username": current_user.username,
#                 "best_score": best_score
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             "status": 500,
#             "message": f"Error fetching best score: {str(e)}"
#         }), 500


# ============================================================
# STEP 4: ADAPTATION OF LIVE LEADERBOARD FOR CURRENT_USER
# ============================================================
# This endpoint shows ONLY the current_user's rank in the leaderboard.
# It calculates rank considering:
# - Higher scores = Higher rank
# - If scores are tied, more recent completion = Higher rank
# - All previous users' scores are saved but not shown

# @leaderboard.route("/my-leaderboard-rank", methods=["GET"])
# @login_required
# def get_my_leaderboard_rank():
#     """
#     Gets the current_user's rank in the live leaderboard.
#     Only shows the current_user's position, not other users.
#     Tie-breaking: More recent completion = Higher rank when scores are equal.
#     
#     Test in Postman:
#     GET http://localhost:5000/my-leaderboard-rank
#     """
#     try:
#         # Get current_user's best score and when they achieved it
#         user_best = db.session.query(
#             Score.score,
#             Score.date
#         ).filter_by(
#             user_id=current_user.id
#         ).order_by(
#             Score.score.desc(),
#             Score.date.desc()  # Most recent if same score
#         ).first()
        
#         if not user_best:
#             return jsonify({
#                 "status": 200,
#                 "data": {
#                     "username": current_user.username,
#                     "rank": None,
#                     "score": 0,
#                     "message": "No scores submitted yet"
#                 }
#             }), 200
        
#         user_score = user_best.score
#         user_date = user_best.date
        
#         # Count how many users have a better score OR same score but finished earlier
#         # (Earlier = lower rank, so we count users who finished before current_user when tied)
#         better_rank_count = db.session.query(
#             func.count(func.distinct(Score.user_id))
#         ).join(
#             User, Score.user_id == User.id
#         ).filter(
#             # Users with higher scores
#             (Score.score > user_score) |
#             # OR users with same score but finished earlier (more recent = higher rank)
#             (
#                 (Score.score == user_score) &
#                 (Score.date > user_date)  # Finished after current_user = higher rank
#             )
#         ).scalar()
        
#         # Rank is count of users above + 1
#         user_rank = better_rank_count + 1
        
#         # Get total number of players for context
#         total_players = db.session.query(
#             func.count(func.distinct(Score.user_id))
#         ).scalar()
        
#         return jsonify({
#             "status": 200,
#             "data": {
#                 "username": current_user.username,
#                 "rank": user_rank,
#                 "score": user_score,
#                 "total_players": total_players,
#                 "date_achieved": user_date.isoformat()
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             "status": 500,
#             "message": f"Error fetching leaderboard rank: {str(e)}"
#         }), 500


# ============================================================
# STEP 5: ALTERNATIVE - GET RANK WITH CONTEXT (OPTIONAL)
# ============================================================
# This shows current_user's rank plus a few players around them
# for context. Still focused on current_user.

# @leaderboard.route("/my-leaderboard-with-context", methods=["GET"])
# @login_required
# def get_my_leaderboard_with_context():
#     """
#     Gets current_user's rank plus 2 players above and 2 below for context.
#     Still focused on current_user but shows nearby players.
#     
#     Test in Postman:
#     GET http://localhost:5000/my-leaderboard-with-context
#     """
#     try:
#         # Get current_user's best score
#         user_best = db.session.query(
#             Score.score,
#             Score.date
#         ).filter_by(
#             user_id=current_user.id
#         ).order_by(
#             Score.score.desc(),
#             Score.date.desc()
#         ).first()
        
#         if not user_best:
#             return jsonify({
#                 "status": 200,
#                 "data": {
#                     "username": current_user.username,
#                     "rank": None,
#                     "score": 0,
#                     "context": [],
#                     "message": "No scores submitted yet"
#                 }
#             }), 200
        
#         user_score = user_best.score
#         user_date = user_best.date
        
#         # Get all unique user best scores with tie-breaking
#         # For each user, get their best score (highest, or most recent if tied)
#         all_user_scores = db.session.query(
#             Score.user_id,
#             func.max(Score.score).label('max_score'),
#             func.max(Score.date).label('max_date')
#         ).group_by(Score.user_id).subquery()
        
#         # Get all scores ordered by: score DESC, date DESC (recent first when tied)
#         ranked_scores = db.session.query(
#             User.username,
#             all_user_scores.c.max_score.label('score'),
#             all_user_scores.c.max_date.label('date'),
#             User.id.label('user_id')
#         ).join(
#             all_user_scores, User.id == all_user_scores.c.user_id
#         ).order_by(
#             all_user_scores.c.max_score.desc(),
#             all_user_scores.c.max_date.desc()  # More recent = higher rank when tied
#         ).all()
#         
#         # Find current_user's position
#         user_rank = None
#         for idx, (username, score, date, user_id) in enumerate(ranked_scores, 1):
#             if user_id == current_user.id:
#                 user_rank = idx
#                 break
#         
#         if user_rank is None:
#             return jsonify({
#                 "status": 200,
#                 "data": {
#                     "username": current_user.username,
#                     "rank": None,
#                     "score": user_score,
#                     "context": []
#                 }
#             }), 200
        
#         # Get context: 2 above and 2 below current_user
#         context_start = max(0, user_rank - 3)  # 2 above + current_user
#         context_end = min(len(ranked_scores), user_rank + 2)  # current_user + 2 below
        
#         context_data = []
#         for idx in range(context_start, context_end):
#             username, score, date, user_id = ranked_scores[idx]
#             context_data.append({
#                 "rank": idx + 1,
#                 "username": username,
#                 "score": score,
#                 "isCurrentUser": user_id == current_user.id
#             })
#         
#         return jsonify({
#             "status": 200,
#             "data": {
#                 "username": current_user.username,
#                 "rank": user_rank,
#                 "score": user_score,
#                 "total_players": len(ranked_scores),
#                 "context": context_data
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             "status": 500,
#             "message": f"Error fetching leaderboard with context: {str(e)}"
#         }), 500


# ============================================================
# STEP 6: REGISTER BLUEPRINT (__init__.py)
# ============================================================
# In your back_end/__init__.py file, make sure you have:

# from .leaderboards import leaderboard
# app.register_blueprint(leaderboard, url_prefix="/")


# ============================================================
# TESTING INSTRUCTIONS
# ============================================================
# 
# 1. Make sure you're logged in (use your login endpoint first)
# 
# 2. Submit a score:
#    POST http://localhost:5000/submit-score
#    Headers: Content-Type: application/json
#    Body: { "score": 100 }
# 
# 3. Get your best score:
#    GET http://localhost:5000/my-best-score
# 
# 4. Get your leaderboard rank:
#    GET http://localhost:5000/my-leaderboard-rank
# 
# 5. Get your rank with context (optional):
#    GET http://localhost:5000/my-leaderboard-with-context
#
# TIE-BREAKING TEST:
# - Submit score 100 for User A
# - Submit score 100 for User B (later)
# - User B should have rank 1, User A should have rank 2
# - This is because User B finished more recently


# ============================================================
# ERROR HANDLING
# ============================================================
# The API handles these cases:
# - Invalid score values (non-integer, negative)
# - Missing required fields
# - Database errors
# - Authentication errors (not logged in)
# - Users with no scores yet
#
# Each error returns appropriate HTTP status codes:
# - 200: Success
# - 400: Bad Request (invalid input)
# - 401: Unauthorized (not logged in - handled by @login_required)
# - 500: Server Error
#
# Remember to test:
# 1. Submitting scores with invalid values
# 2. Accessing endpoints without login
# 3. Getting rank when user has no scores
# 4. Tie-breaking with same scores at different times
