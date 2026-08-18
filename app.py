from flask import Flask, jsonify, request, send_from_directory
from storage_manager import load_data, save_data
from scheduler_engine import generate_schedule

app = Flask(__name__, static_folder="frontend", static_url_path="")

USERS_FILE = "data/users.json"
ROOMS_FILE = "data/rooms.json"
FACULTIES_FILE = "data/faculties.json"
TIMETABLE_FILE = "data/timetable.json"

# ================= PAGE ROUTES =================

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
@app.route("/faculty_manager")
def faculties():
    return send_from_directory("frontend", "faculties.html")

@app.route("/room_allocation")
@app.route("/rooms")
def rooms():
    return send_from_directory("frontend", "room_allocation.html")


# ================= TIMETABLE API ROUTES =================

@app.route("/api/timetable", methods=["GET"])
def get_timetable():
    data = load_data(TIMETABLE_FILE)
    return jsonify(data if isinstance(data, dict) else {}), 200

@app.route("/api/generate-timetable", methods=["POST"])
def api_generate_timetable():
    new_schedule = generate_schedule()
    return jsonify({"status": "success", "schedule": new_schedule}), 200


# ================= OTHER API ROUTES =================

@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.get_json()
    if not credentials or "email" not in credentials or "password" not in credentials:
        return jsonify({"status": "error", "message": "Email and password required."}), 400
    users = load_data(USERS_FILE)
    matched_user = next((u for u in users if u["email"] == credentials["email"] and u["password"] == credentials["password"]), None)
    if not matched_user:
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401
    return jsonify({"status": "success", "user": matched_user}), 200

@app.route("/api/faculties", methods=["GET", "POST", "DELETE"])
def api_faculties():
    faculties = load_data(FACULTIES_FILE)
    if request.method == "POST":
        new_faculty = request.get_json()
        if not new_faculty:
            return jsonify({"status": "error", "message": "Invalid faculty data"}), 400
        faculties.append(new_faculty)
        save_data(FACULTIES_FILE, faculties)
        return jsonify({"status": "success", "faculty": new_faculty}), 201
    if request.method == "DELETE":
        faculty_id = request.args.get("id")
        faculties = [f for f in faculties if str(f.get("id")) != str(faculty_id)]
        save_data(FACULTIES_FILE, faculties)
        return jsonify({"status": "success", "message": "Faculty deleted"}), 200
    return jsonify(faculties), 200

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
    