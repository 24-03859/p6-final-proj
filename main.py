from back_end import create_app
from flask_cors import CORS, cross_origin


app=create_app()

cors = CORS(app, resources={r"/api/": {"origins": "http://localhost:5173/"}})
app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(debug=True)


# Modification:
# sa user ang attributes nalang ay username, password & password confirmation
# note -> feedback

# Dagdag:
# Leaderboards (LIVE)

#ang magagamit ay:
# all about user

#pag aaralan:
#TOKEN