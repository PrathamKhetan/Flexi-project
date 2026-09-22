"""
Sample User Authentication and Profile Service built with Flask.
Demonstrates route decorators, HTTP methods, route parameters, and error handling.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/api/v1/auth/login", methods=["POST"])
def user_login():
    """
    Authenticate User Credentials.
    Receives email and password payload, validates against hashed secrets, and yields a signed JWT.
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing credentials"}), 400
    return jsonify({"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "expires_in": 3600}), 200


@app.route("/api/v1/users", methods=["GET"])
def list_all_users():
    """
    List Registered Users.
    Returns account records with support for role filtering.
    """
    role = request.args.get("role", "all")
    page = int(request.args.get("page", 1))
    return jsonify({"page": page, "users": []}), 200


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    """
    Fetch User Profile Record.
    Retrieves public attributes for a user account identifier.
    """
    return jsonify({"id": user_id, "username": "alice", "email": "alice@example.com"}), 200


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
def update_user_profile(user_id):
    """
    Update User Attributes.
    Updates contact preferences or username.
    """
    return jsonify({"id": user_id, "updated": True}), 200
