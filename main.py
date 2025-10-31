from back_end import create_app
from flask_cors import CORS, cross_origin


app=create_app()

# Allow the frontend dev server (Vite/webpack/etc) to call Flask endpoints.
# The original configuration only opened /api/ and used a trailing slash
# which does not match routes like /sign-up. Also enable credentials so
# cookies/session-based auth works across origins when the frontend uses
# `fetch(..., { credentials: 'include' })`.
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
    supports_credentials=True)

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