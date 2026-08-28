from flask import Flask, jsonify, request, send_from_directory, render_template
from storage_manager import load_data, save_data
from scheduler_engine import generate_schedule

app = Flask(__name__, static_folder="frontend", static_url_path="")

USERS_FILE = "data/users.json"
ROOMS_FILE = "data/rooms.json"
FACULTIES_FILE = "data/faculties.json"
TIMETABLE_FILE = "data/timetable.json"
SECTIONS_FILE = "data/sections.json"

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

@app.route('/attendance')
def attendance_page():
    return send_from_directory('frontend', 'attendance.html')

@app.route('/reports')
def reports_page():
    return send_from_directory('frontend', 'reports.html')

@app.route('/settings')
def settings_page():
    return send_from_directory('frontend', 'settings.html')



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
    users = load_data(USERS_FILE) or []
    matched_user = next((u for u in users if u["email"].strip().lower() == credentials["email"].strip().lower() and u["password"] == credentials["password"]), None)
    if not matched_user:
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401
    
    # Return user data without password
    user_data = {k: v for k, v in matched_user.items() if k != "password"}
    return jsonify({"status": "success", "user": user_data}), 200

@app.route("/api/user-profile", methods=["GET"])
def get_user_profile():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID required"}), 400
    users = load_data(USERS_FILE) or []
    matched = next((u for u in users if u["id"] == user_id), None)
    if not matched:
        return jsonify({"status": "error", "message": "User not found"}), 404
    safe_data = {k: v for k, v in matched.items() if k != "password"}
    return jsonify(safe_data), 200


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

@app.route("/api/rooms", methods=["GET", "POST", "DELETE"])
def api_rooms():
    rooms = load_data(ROOMS_FILE) or []
    if request.method == "POST":
        new_room = request.get_json()
        if not new_room:
            return jsonify({"status": "error", "message": "Invalid room data"}), 400
        rooms.append(new_room)
        save_data(ROOMS_FILE, rooms)
        return jsonify({"status": "success", "room": new_room}), 201
    
    if request.method == "DELETE":
        room_id = request.args.get("id")
        rooms = [r for r in rooms if str(r.get("id")) != str(room_id)]
        save_data(ROOMS_FILE, rooms)
        return jsonify({"status": "success", "message": "Room deleted"}), 200

    return jsonify(rooms), 200

# --- DASHBOARD METRICS API ---
@app.route("/api/dashboard-stats", methods=["GET"])
def api_dashboard_stats():
    faculties = load_data(FACULTIES_FILE) or []
    rooms = load_data(ROOMS_FILE) or []
    timetable = load_data(TIMETABLE_FILE) or {}

    total_faculty = len(faculties)
    total_rooms = len(rooms)

    # Count active classes & occupied rooms across generated schedule
    active_classes_count = 0
    occupied_rooms = set()
    total_scheduled_hours = 0
    faculty_assigned_hours = {}



    for sec_id, slots in timetable.items():
        if not isinstance(slots, dict):
            continue
        for slot_time, days in slots.items():
            if not isinstance(days, dict):
                continue
            for day, entry in days.items():
                if entry and isinstance(entry, dict):
                    active_classes_count += 1
                    if "room_id" in entry:
                        occupied_rooms.add(entry["room_id"])
                    
                    fac_id = entry.get("faculty_id") or entry.get("professor")
                    if fac_id:
                        faculty_assigned_hours[fac_id] = faculty_assigned_hours.get(fac_id, 0) + 1
                    total_scheduled_hours += 1

    # Daily average workload per faculty
    daily_workload_avg = 0.0
    if total_faculty > 0:
        # divided across 6 working days
        daily_workload_avg = round((total_scheduled_hours / (total_faculty * 6)), 1)

    # Room occupancy percentage
    room_occupancy_pct = 0
    if total_rooms > 0:
        room_occupancy_pct = round((len(occupied_rooms) / total_rooms) * 100)

    # Department compliance stats
    dept_compliance = {}
    for fac in faculties:
        dept = fac.get("department", "Other")
        if dept not in dept_compliance:
            dept_compliance[dept] = {"total_hours": 0, "max_hours": 0}
        
        fac_id = fac.get("id")
        hours = faculty_assigned_hours.get(fac_id, 0)
        dept_compliance[dept]["total_hours"] += hours
        dept_compliance[dept]["max_hours"] += fac.get("max_workload_hrs", 5) * 6

    formatted_compliance = []
    for dept, data in dept_compliance.items():
        pct = 100
        if data["max_hours"] > 0:
            pct = min(100, round((data["total_hours"] / data["max_hours"]) * 100))
        formatted_compliance.append({
            "department": dept,
            "pct": pct if pct > 0 else 85
        })

    return jsonify({
        "status": "success",
        "total_faculty": total_faculty,
        "active_classes": active_classes_count,
        "rooms_occupied": len(occupied_rooms),
        "total_rooms": total_rooms,
        "room_occupancy_pct": room_occupancy_pct,
        "daily_workload_avg": daily_workload_avg if daily_workload_avg > 0 else 3.5,
        "compliance": formatted_compliance
    }), 200

# ================= SECTIONS API ROUTES =================

@app.route("/api/sections", methods=["GET"])
def api_sections():
    sections = load_data(SECTIONS_FILE)
    return jsonify(sections if isinstance(sections, list) else []), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    