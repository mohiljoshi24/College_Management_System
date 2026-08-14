from flask import Flask, jsonify, request, send_from_directory
from storage_manager import load_data, save_data

app = Flask(__name__, static_folder="frontend", static_url_path="")

USERS_FILE = "data/users.json"
ROOMS_FILE = "data/rooms.json"

# Serve Pages
@app.route("/")
def index():
    return send_from_directory("frontend", "login_page.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory("frontend", "dashboard.html")

@app.route("/timetable")
def timetable():
    return send_from_directory("frontend", "timetable.html")

@app.route("/faculties")
def faculties():
    return send_from_directory("frontend", "faculties.html")

# Both routes point to room_allocation.html
@app.route("/room_allocation")
@app.route("/rooms")
def rooms():
    return send_from_directory("frontend", "room_allocation.html")

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

# Room API
@app.route("/api/rooms", methods=["GET", "POST"])
def api_rooms():
    if request.method == "POST":
        new_room = request.get_json()
        if not new_room:
            return jsonify({"status": "error", "message": "Invalid room data"}), 400
        
        rooms = load_data(ROOMS_FILE)
        rooms.append(new_room)
        save_data(ROOMS_FILE, rooms)
        return jsonify({"status": "success", "room": new_room}), 201
    
    rooms = load_data(ROOMS_FILE)
    return jsonify(rooms), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)