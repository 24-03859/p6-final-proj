# BACKEND LEADERBOARDS IMPLEMENTATION GUIDE
# -----------------------------------

# 1. DATABASE MODEL SETUP (models.py)
# ---------------------------------
# Add this Score model to your models.py:

# from . import db
# from sqlalchemy.sql import func

# class Score(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     score = db.Column(db.Integer, nullable=False)
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# # Update User model to include the relationship:
# class User(db.Model, UserMixin):
#     # ... existing fields ...
#     scores = db.relationship('Score', backref='user', lazy=True)


# 2. LEADERBOARD ROUTES (leaderboards.py)
# -------------------------------------
# Create leaderboards.py with these endpoints:

# from flask import Blueprint, request, jsonify
# from flask_login import current_user, login_required
# from sqlalchemy import desc, func
# from datetime import datetime, timedelta
# from . import db
# from .models import Score, User

# leaderboards = Blueprint('leaderboards', __name__)

# @leaderboards.route('/add-score', methods=['POST'])
# @login_required
# def add_score():
#     """
#     Test in Postman:
#     POST http://localhost:5000/add-score
#     Headers: 
#         Content-Type: application/json
#     Body:
#         {
#             "score": 100
#         }
#     """
#     try:
#         data = request.get_json()
        
#         if not data or 'score' not in data:
#             return jsonify({
#                 "status": 400,
#                 "message": "Score is required"
#             }), 400
            
#         try:
#             score = int(data['score'])
#             if not (0 <= score <= 999999):
#                 return jsonify({
#                     "status": 400,
#                     "message": "Score must be between 0 and 999999"
#                 }), 400
#         except (TypeError, ValueError):
#             return jsonify({
#                 "status": 400,
#                 "message": "Score must be an integer"
#             }), 400
        
#         new_score = Score(
#             score=score,
#             user_id=current_user.id,
#             date=datetime.utcnow()
#         )
        
#         db.session.add(new_score)
#         db.session.commit()
        
#         return jsonify({
#             "status": 200,
#             "message": "Score added successfully",
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
#             "message": f"Error adding score: {str(e)}"
#         }), 500

# @leaderboards.route('/get-leaderboard', methods=['GET'])
# def get_leaderboard():
#     """
#     Test in Postman:
#     GET http://localhost:5000/get-leaderboard?period=all&limit=10
    
#     Query Parameters:
#     - period: all, daily, weekly, monthly (default: all)
#     - limit: number of scores to return (default: 10, max: 100)
#     """
#     try:
#         period = request.args.get('period', 'all')
#         try:
#             limit = min(int(request.args.get('limit', 10)), 100)
#         except ValueError:
#             limit = 10
            
#         query = Score.query
        
#         now = datetime.utcnow()
#         if period == 'daily':
#             query = query.filter(Score.date >= now.date())
#         elif period == 'weekly':
#             query = query.filter(Score.date >= now - timedelta(days=7))
#         elif period == 'monthly':
#             query = query.filter(Score.date >= now - timedelta(days=30))
            
#         # Get highest score per user
#         subquery = db.session.query(
#             Score.user_id,
#             func.max(Score.score).label('max_score')
#         ).group_by(Score.user_id).subquery()
        
#         scores = db.session.query(Score, User)\
#             .join(subquery, db.and_(
#                 Score.user_id == subquery.c.user_id,
#                 Score.score == subquery.c.max_score
#             ))\
#             .join(User)\
#             .order_by(Score.score.desc())\
#             .limit(limit)\
#             .all()
        
#         leaderboard_data = [{
#             "rank": idx + 1,
#             "username": user.username,
#             "score": score.score,
#             "date": score.date.isoformat(),
#             "isCurrentUser": user.id == current_user.id if current_user.is_authenticated else False
#         } for idx, (score, user) in enumerate(scores)]
        
#         return jsonify({
#             "status": 200,
#             "data": {
#                 "period": period,
#                 "scores": leaderboard_data
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             "status": 500,
#             "message": f"Error fetching leaderboard: {str(e)}"
#         }), 500

# @leaderboards.route('/my-scores', methods=['GET'])
# @login_required
# def get_my_scores():
#     """
#     Test in Postman:
#     GET http://localhost:5000/my-scores?limit=10
    
#     Query Parameters:
#     - limit: number of scores to return (default: 10, max: 100)
#     """
#     try:
#         try:
#             limit = min(int(request.args.get('limit', 10)), 100)
#         except ValueError:
#             limit = 10
            
#         scores = Score.query\
#             .filter_by(user_id=current_user.id)\
#             .order_by(Score.score.desc())\
#             .limit(limit)\
#             .all()
            
#         scores_data = [{
#             "score": score.score,
#             "date": score.date.isoformat(),
#             "rank": idx + 1
#         } for idx, score in enumerate(scores)]
        
#         # Get user's highest score and global rank
#         if scores:
#             highest_score = scores[0].score
#             rank_query = db.session.query(func.count(Score.id))\
#                 .join(User)\
#                 .filter(Score.score > highest_score)\
#                 .group_by(User.id)
#             global_rank = rank_query.count() + 1
#         else:
#             highest_score = 0
#             global_rank = None
            
#         return jsonify({
#             "status": 200,
#             "data": {
#                 "username": current_user.username,
#                 "highest_score": highest_score,
#                 "global_rank": global_rank,
#                 "scores": scores_data
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             "status": 500,
#             "message": f"Error fetching user scores: {str(e)}"
#         }), 500

# @leaderboards.route('/stats', methods=['GET'])
# def get_stats():
#     """
#     Test in Postman:
#     GET http://localhost:5000/stats
#     """
#     try:
#         total_scores = Score.query.count()
#         total_players = db.session.query(Score.user_id).distinct().count()
        
#         highest_score = db.session.query(
#             User.username,
#             Score.score,
#             Score.date
#         ).join(Score)\
#           .order_by(Score.score.desc())\
#           .first()
        
#         today = datetime.utcnow().date()
#         scores_today = Score.query.filter(
#             func.date(Score.date) == today
#         ).count()
        
#         return jsonify({
#             "status": 200,
#             "data": {
#                 "total_scores_submitted": total_scores,
#                 "total_players": total_players,
#                 "scores_today": scores_today,
#                 "highest_score": {
#                     "username": highest_score[0] if highest_score else None,
#                     "score": highest_score[1] if highest_score else 0,
#                     "date": highest_score[2].isoformat() if highest_score else None
#                 }
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             "status": 500,
#             "message": f"Error fetching stats: {str(e)}"
#         }), 500


# 3. REGISTER BLUEPRINT (__init__.py)
# --------------------------------
# In __init__.py, add these lines:

# from .leaderboards import leaderboards
# app.register_blueprint(leaderboards, url_prefix='/')


# 4. TESTING IN POSTMAN
# -------------------
# 1. First login using your auth endpoint to get a session

# 2. Test adding a score:
# POST http://localhost:5000/add-score
# Headers:
#   Content-Type: application/json
# Body:
# {
#     "score": 100
# }

# 3. Get leaderboard with filters:
# GET http://localhost:5000/get-leaderboard?period=all&limit=10
# GET http://localhost:5000/get-leaderboard?period=daily
# GET http://localhost:5000/get-leaderboard?period=weekly
# GET http://localhost:5000/get-leaderboard?period=monthly

# 4. Get your personal scores:
# GET http://localhost:5000/my-scores?limit=10

# 5. Get leaderboard statistics:
# GET http://localhost:5000/stats


# 5. ERROR HANDLING
# ---------------
# The API handles these cases:
# - Invalid score values
# - Missing required fields
# - Database errors
# - Authentication errors
# - Invalid query parameters

# Each error returns appropriate HTTP status codes:
# - 200: Success
# - 400: Bad Request (invalid input)
# - 401: Unauthorized (not logged in)
# - 500: Server Error

# Remember to always test:
# 1. Adding scores with invalid values
# 2. Accessing protected endpoints without login
# 3. Using invalid period filters
# 4. Using invalid limit values
# 5. Checking error messages are helpful