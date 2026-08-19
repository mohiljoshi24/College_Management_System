import random
from storage_manager import load_data, save_data

TIMETABLE_FILE = "data/timetable.json"
FACULTIES_FILE = "data/faculties.json"
ROOMS_FILE = "data/rooms.json"
SUBJECTS_FILE = "data/subjects.json"
SECTIONS_FILE = "data/sections.json"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

TIME_SLOTS = [
    "09:00 AM - 10:00 AM",
    "10:00 AM - 11:00 AM",
    "11:20 AM - 12:10 PM",
    "12:10 PM - 01:00 PM",
    "01:50 PM - 02:40 PM",
    "02:40 PM - 03:30 PM"
]

COLOR_MAP = {
    "Computer Science": "purple-card",
    "Information Technology": "blue-card",
    "Electronics & Comm": "green-card",
    "Mathematics": "yellow-card"
}

def generate_schedule():
    faculties = load_data(FACULTIES_FILE) or []
    rooms = load_data(ROOMS_FILE) or []
    subjects = load_data(SUBJECTS_FILE) or []
    sections = load_data(SECTIONS_FILE) or []

    # Map subjects by semester & department
    def get_eligible_subjects(dept, sem):
        return [s for s in subjects if s.get("semester") == sem and (s.get("department") == dept or s.get("department") == "Mathematics")]

    def get_eligible_faculty(subj_code):
        eligible = [f for f in faculties if subj_code in f.get("subjects_can_teach", [])]
        return eligible if eligible else faculties

    def get_eligible_rooms(subj_type, dept):
        matched = [r for r in rooms if r.get("type") == subj_type]
        dept_matched = [r for r in matched if r.get("department") == dept or r.get("department") == "General"]
        return dept_matched if dept_matched else matched

    # Master structure: { section_id: { time_slot: { day: item } } }
    master_schedule = {}

    # Tracking booked resources: (day, slot) -> set of IDs
    booked_faculty = {}
    booked_rooms = {}

    for sec in sections:
        sec_id = sec["id"]
        master_schedule[sec_id] = {slot: {day: None for day in DAYS} for slot in TIME_SLOTS}
        sec_dept = sec.get("department", "Computer Science")
        sec_sem = sec.get("semester", 1)

        available_subjects = get_eligible_subjects(sec_dept, sec_sem)
        if not available_subjects:
            available_subjects = subjects

        for day in DAYS:
            daily_lecture_count = 0
            for slot in TIME_SLOTS:
                slot_key = (day, slot)
                if slot_key not in booked_faculty:
                    booked_faculty[slot_key] = set()
                if slot_key not in booked_rooms:
                    booked_rooms[slot_key] = set()

                # Cap lectures to max 4-5 per day per cohort
                if daily_lecture_count >= 5 or random.random() < 0.20:
                    continue

                subj = random.choice(available_subjects)
                subj_type = subj.get("type", "LECTURE")

                # Find available faculty
                faculty_candidates = [f for f in get_eligible_faculty(subj.get("code")) if f["id"] not in booked_faculty[slot_key]]
                if not faculty_candidates:
                    continue
                chosen_faculty = random.choice(faculty_candidates)

                # Find available room
                room_candidates = [r for r in get_eligible_rooms(subj_type, sec_dept) if r["id"] not in booked_rooms[slot_key]]
                if not room_candidates:
                    continue
                chosen_room = random.choice(room_candidates)

                # Lock resource assignments
                booked_faculty[slot_key].add(chosen_faculty["id"])
                booked_rooms[slot_key].add(chosen_room["id"])
                daily_lecture_count += 1

                card_color = COLOR_MAP.get(subj.get("department"), "orange-card")
                if subj_type == "LAB":
                    card_color = "red-card"

                master_schedule[sec_id][slot][day] = {
                    "subject": subj.get("code"),
                    "subject_name": subj.get("name"),
                    "type": subj_type,
                    "professor": chosen_faculty.get("name"),
                    "faculty_id": chosen_faculty.get("id"),
                    "room": chosen_room.get("name"),
                    "room_id": chosen_room.get("id"),
                    "color": card_color
                }

    save_data(TIMETABLE_FILE, master_schedule)
    return master_schedule