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
    "Mathematics": "yellow-card",
    "Humanities": "orange-card"
}

def generate_schedule():
    faculties = load_data(FACULTIES_FILE) or []
    rooms = load_data(ROOMS_FILE) or []
    subjects = load_data(SUBJECTS_FILE) or []
    sections = load_data(SECTIONS_FILE) or []

    # Helper: Normalize subject code lookup
    def clean_code(code):
        return str(code or "").replace(" ", "").upper()

    # Map subjects by semester & department
    def get_eligible_subjects(dept, sem):
        matched = []
        for s in subjects:
            s_sem = s.get("semester")
            s_dept = s.get("department")
            if s_sem != sem:
                continue
            # Main department
            if s_dept == dept:
                matched.append(s)
            # Cross-department common subjects (Math, Humanities, Basic Electronics for 1st sem)
            elif s_dept in ["Mathematics", "Humanities"]:
                matched.append(s)
            elif sem == 1 and s_dept == "Electronics & Comm":
                matched.append(s)
        return matched if matched else [s for s in subjects if s.get("semester") == sem]

    def get_eligible_faculty(subj_code, subj_dept):
        clean_target = clean_code(subj_code)
        # 1. Exact competency array match
        exact_matched = [
            f for f in faculties 
            if any(clean_code(c) == clean_target for c in (f.get("subjects_can_teach") or f.get("active_courses") or []))
        ]
        if exact_matched:
            return exact_matched
        
        # 2. Department match fallback
        dept_matched = [f for f in faculties if f.get("department") == subj_dept]
        if dept_matched:
            return dept_matched
        
        return faculties

    def get_eligible_rooms(subj_type, dept):
        matched_type = [r for r in rooms if r.get("type", "LECTURE").upper() == subj_type.upper()]
        dept_matched = [r for r in matched_type if r.get("department") == dept or r.get("department") == "General"]
        return dept_matched if dept_matched else matched_type

    master_schedule = {}

    # Tracking booked resources: (day, slot) -> set of IDs
    booked_faculty = {}
    booked_rooms = {}
    
    # Tracking daily faculty workloads: (faculty_id, day) -> count
    faculty_daily_load = {}

    for sec in sections:
        sec_id = sec["id"]
        master_schedule[sec_id] = {slot: {day: None for day in DAYS} for slot in TIME_SLOTS}
        sec_dept = sec.get("department", "Computer Science")
        sec_sem = sec.get("semester", 1)

        available_subjects = get_eligible_subjects(sec_dept, sec_sem)
        if not available_subjects:
            available_subjects = subjects

        # Track weekly subject usage to balance credit distribution
        subj_weekly_count = {s.get("code"): 0 for s in available_subjects}

        for day in DAYS:
            daily_lecture_count = 0
            daily_subjects_assigned = set()
            daily_max_slots = 4 if day == "Sat" else 5  # Sat is half day (4 slots), Mon-Fri 5 slots

            for slot_idx, slot in enumerate(TIME_SLOTS):
                if daily_lecture_count >= daily_max_slots:
                    break

                slot_key = (day, slot)
                if slot_key not in booked_faculty:
                    booked_faculty[slot_key] = set()
                if slot_key not in booked_rooms:
                    booked_rooms[slot_key] = set()

                # Prioritize subjects that haven't been taught today and have lower weekly count
                candidate_subjects = [
                    s for s in available_subjects 
                    if s.get("code") not in daily_subjects_assigned
                ]
                
                # If all subjects have been taught today, fall back to any available subject
                if not candidate_subjects:
                    candidate_subjects = list(available_subjects)

                # Sort candidate subjects: least used this week first
                candidate_subjects.sort(key=lambda s: subj_weekly_count.get(s.get("code"), 0))

                chosen_subject = None
                chosen_faculty = None
                chosen_room = None

                for subj in candidate_subjects:
                    s_code = subj.get("code")
                    s_type = subj.get("type", "LECTURE").upper()
                    s_dept = subj.get("department", sec_dept)

                    # Find available eligible faculty
                    eligible_facs = get_eligible_faculty(s_code, s_dept)
                    avail_facs = [
                        f for f in eligible_facs 
                        if f["id"] not in booked_faculty[slot_key]
                        and faculty_daily_load.get((f["id"], day), 0) < f.get("max_workload_hrs", 5.0)
                    ]
                    if not avail_facs:
                        continue

                    # Find available eligible room
                    eligible_rms = get_eligible_rooms(s_type, sec_dept)
                    avail_rms = [r for r in eligible_rms if r["id"] not in booked_rooms[slot_key]]
                    if not avail_rms:
                        continue

                    # Viable assignment found
                    chosen_subject = subj
                    avail_facs.sort(key=lambda f: faculty_daily_load.get((f["id"], day), 0))
                    chosen_faculty = avail_facs[0]
                    chosen_room = random.choice(avail_rms)
                    break

                if not chosen_subject or not chosen_faculty or not chosen_room:
                    continue

                # Lock assignments
                f_id = chosen_faculty["id"]
                r_id = chosen_room["id"]
                s_code = chosen_subject.get("code")
                s_type = chosen_subject.get("type", "LECTURE").upper()

                booked_faculty[slot_key].add(f_id)
                booked_rooms[slot_key].add(r_id)
                faculty_daily_load[(f_id, day)] = faculty_daily_load.get((f_id, day), 0) + 1
                subj_weekly_count[s_code] = subj_weekly_count.get(s_code, 0) + 1
                daily_subjects_assigned.add(s_code)
                daily_lecture_count += 1

                card_color = COLOR_MAP.get(chosen_subject.get("department"), "purple-card")
                if s_type == "LAB":
                    card_color = "red-card"

                master_schedule[sec_id][slot][day] = {
                    "subject": s_code,
                    "subject_name": chosen_subject.get("name"),
                    "type": s_type,
                    "professor": chosen_faculty.get("name"),
                    "faculty_id": f_id,
                    "room": chosen_room.get("name"),
                    "room_id": r_id,
                    "color": card_color
                }

    save_data(TIMETABLE_FILE, master_schedule)
    return master_schedule