from flask import Flask, jsonify, request, send_from_directory
from storage_manager import load_data

app = Flask(__name__, static_folder="frontend", static_url_path="")

USERS_FILE = "data/users.json"

# Route to serve the frontend Login page
@app.route("/")
def index():
    return send_from_directory("frontend", "login_page.html")

# Route to serve your existing dashboard page
@app.route("/dashboard")
def dashboard():
    return send_from_directory("frontend", "dashboard.html")

# Authentication API
@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.get_json()
    
    if not credentials or "email" not in credentials or "password" not in credentials:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    email = credentials["email"]
    password = credentials["password"]

    users = load_data(USERS_FILE)
    matched_user = next((u for u in users if u["email"] == email and u["password"] == password), None)

    if not matched_user:
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    return jsonify({
        "status": "success",
        "message": "Login successful!",
        "user": {
            "id": matched_user["id"],
            "email": matched_user["email"],
            "role": matched_user["role"]
        }
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)