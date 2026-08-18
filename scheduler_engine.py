import random
from storage_manager import load_data, save_data

TIMETABLE_FILE = "data/timetable.json"
FACULTIES_FILE = "data/faculties.json"
ROOMS_FILE = "data/rooms.json"
SUBJECTS_FILE = "data/subjects.json"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

# College 6 Lecture Slots
TIME_SLOTS = [
    "09:00 AM - 10:00 AM",
    "10:00 AM - 11:00 AM",
    "11:20 AM - 12:10 PM",
    "12:10 PM - 01:00 PM",
    "01:50 PM - 02:40 PM",
    "02:40 PM - 03:30 PM"
]

COLOR_PALETTE = ["purple-card", "yellow-card", "blue-card", "green-card", "red-card", "orange-card"]

def generate_schedule():
    faculties = load_data(FACULTIES_FILE) or []
    rooms = load_data(ROOMS_FILE) or []
    subjects = load_data(SUBJECTS_FILE) or []

    # Fallback seed data if files are empty
    if not faculties:
        faculties = [
            {"id": "FA001", "name": "Dr. Aditi Sharma"},
            {"id": "FA002", "name": "Prof. Rajesh Kumar"},
            {"id": "FA003", "name": "Dr. Sneha Patel"}
        ]
    if not rooms:
        rooms = [
            {"id": "R101", "name": "Lecture Hall 1", "type": "LECTURE"},
            {"id": "R102", "name": "Lecture Hall 2", "type": "LECTURE"},
            {"id": "L201", "name": "Computer Lab 1", "type": "LAB"}
        ]
    if not subjects:
        subjects = [
            {"code": "CS202", "name": "Data Structures"},
            {"code": "MA101", "name": "Calculus"},
            {"code": "EE101", "name": "Basic Electronics"},
            {"code": "CS301", "name": "Database Systems"}
        ]

    schedule = {}

    for slot in TIME_SLOTS:
        schedule[slot] = {}
        for day in DAYS:
            # 75% probability to schedule a lecture
            if random.random() < 0.75:
                sub = random.choice(subjects)
                fac = random.choice(faculties)
                room = random.choice(rooms)
                color = random.choice(COLOR_PALETTE)

                schedule[slot][day] = {
                    "subject": sub.get("code") or sub.get("name", "CS101"),
                    "professor": fac.get("name", "Faculty"),
                    "room": room.get("name", "Room 101"),
                    "color": color
                }
            else:
                schedule[slot][day] = None

    save_data(TIMETABLE_FILE, schedule)
    return schedule