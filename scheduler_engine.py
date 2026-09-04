import random
from storage_manager import load_data, save_data

TIMETABLE_FILE = "data/timetable.json"
FACULTIES_FILE = "data/faculties.json"
ROOMS_FILE = "data/rooms.json"
SUBJECTS_FILE = "data/subjects.json"
SECTIONS_FILE = "data/sections.json"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
INSTRUCTIONAL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

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
    "Humanities": "orange-card",
    "SPORTS": "sports-card",
    "LIBRARY": "library-card",
    "ASSIGNMENT": "assignment-card"
}

def generate_schedule():
    faculties = load_data(FACULTIES_FILE) or []
    rooms = load_data(ROOMS_FILE) or []
    subjects = load_data(SUBJECTS_FILE) or []
    sections = load_data(SECTIONS_FILE) or []

    def clean_code(code):
        return str(code or "").replace(" ", "").upper()

    # Core academic subjects for department & semester
    def get_academic_subjects(dept, sem):
        matched = []
        for s in subjects:
            if s.get("type") in ["LIBRARY", "SPORTS", "ASSIGNMENT"]:
                continue
            s_sem = s.get("semester")
            s_dept = s.get("department")
            if s_sem != sem:
                continue
            if s_dept == dept:
                matched.append(s)
            elif s_dept in ["Mathematics", "Humanities"]:
                matched.append(s)
            elif sem == 1 and s_dept == "Electronics & Comm":
                matched.append(s)
        return matched if matched else [s for s in subjects if s.get("semester") == sem and s.get("type") not in ["LIBRARY", "SPORTS", "ASSIGNMENT"]]

    # Weekly institutional activity subjects
    activity_subjects = {
        "LIB": next((s for s in subjects if s.get("code") == "LIB101"), {"code": "LIB101", "name": "Library", "type": "LIBRARY", "department": "General"}),
        "ASG": next((s for s in subjects if s.get("code") == "ASG101"), {"code": "ASG101", "name": "Assignment", "type": "ASSIGNMENT", "department": "General"}),
        "SPT": next((s for s in subjects if s.get("code") == "SPT101"), {"code": "SPT101", "name": "Sports", "type": "SPORTS", "department": "General"})
    }

    def get_eligible_faculty(subj_code, subj_type, subj_dept):
        clean_target = clean_code(subj_code)
        
        # 1. Exact competency array match
        exact_matched = [
            f for f in faculties 
            if any(clean_code(c) == clean_target for c in (f.get("subjects_can_teach") or f.get("active_courses") or []))
        ]
        if exact_matched:
            return exact_matched

        # 2. Activity / Type based matches
        if subj_type == "SPORTS":
            sports_fac = [f for f in faculties if f.get("id") == "FA_SPORTS" or "Sports" in f.get("department", "")]
            if sports_fac: return sports_fac
        elif subj_type == "LIBRARY":
            lib_fac = [f for f in faculties if f.get("id") == "FA_LIB" or "Library" in f.get("department", "")]
            if lib_fac: return lib_fac
        elif subj_type == "ASSIGNMENT":
            dept_fac = [f for f in faculties if f.get("department") == subj_dept]
            if dept_fac: return dept_fac

        # 3. Department match fallback
        dept_matched = [f for f in faculties if f.get("department") == subj_dept]
        if dept_matched:
            return dept_matched

        # 4. General fallback (excluding dedicated sports/lib coaches for regular academic classes)
        general_facs = [f for f in faculties if f.get("id") not in ["FA_SPORTS", "FA_LIB"]]
        return general_facs if general_facs else faculties

    def get_eligible_rooms(subj_type, dept):
        matched_type = [r for r in rooms if r.get("type", "LECTURE").upper() == subj_type.upper()]
        if not matched_type:
            if subj_type == "ASSIGNMENT":
                matched_type = [r for r in rooms if r.get("type") in ["LECTURE", "ASSIGNMENT"]]
            else:
                matched_type = [r for r in rooms if r.get("type") == "LECTURE"]
        dept_matched = [r for r in matched_type if r.get("department") == dept or r.get("department") == "General"]
        return dept_matched if dept_matched else matched_type

    master_schedule = {}

    # Tracking booked resources per (day, slot)
    booked_faculty = {}
    booked_rooms = {}

    # Tracking daily faculty workloads: (faculty_id, day) -> count
    faculty_daily_load = {}

    # Tracking previous slot assignment for faculty rest gap heuristic: (faculty_id, day) -> last_slot_idx
    faculty_last_slot = {}

    for sec in sections:
        sec_id = sec["id"]
        # Master schedule template has all DAYS (including Saturday as None)
        master_schedule[sec_id] = {slot: {day: None for day in DAYS} for slot in TIME_SLOTS}
        sec_dept = sec.get("department", "Computer Science")
        sec_sem = sec.get("semester", 1)

        academic_subjects = get_academic_subjects(sec_dept, sec_sem)
        if not academic_subjects:
            academic_subjects = [s for s in subjects if s.get("type") not in ["LIBRARY", "SPORTS", "ASSIGNMENT"]]

        # 1. Schedule the 3 mandatory weekly activity sessions across 3 distinct days
        chosen_act_days = random.sample(INSTRUCTIONAL_DAYS, 3)
        activity_plan = [
            (chosen_act_days[0], activity_subjects["SPT"]),
            (chosen_act_days[1], activity_subjects["LIB"]),
            (chosen_act_days[2], activity_subjects["ASG"])
        ]

        activity_slots_assigned = {}
        for act_day, act_subj in activity_plan:
            possible_slots = [TIME_SLOTS[4], TIME_SLOTS[5], TIME_SLOTS[3], TIME_SLOTS[2]]
            random.shuffle(possible_slots)
            for cand_slot in possible_slots:
                slot_key = (act_day, cand_slot)
                if slot_key not in booked_faculty: booked_faculty[slot_key] = set()
                if slot_key not in booked_rooms: booked_rooms[slot_key] = set()

                act_facs = [
                    f for f in get_eligible_faculty(act_subj["code"], act_subj["type"], sec_dept)
                    if f["id"] not in booked_faculty[slot_key]
                    and faculty_daily_load.get((f["id"], act_day), 0) < f.get("max_workload_hrs", 5.0)
                ]
                act_rms = [r for r in get_eligible_rooms(act_subj["type"], sec_dept) if r["id"] not in booked_rooms[slot_key]]

                if act_facs and act_rms:
                    chosen_f = act_facs[0]
                    chosen_r = random.choice(act_rms)
                    f_id = chosen_f["id"]
                    r_id = chosen_r["id"]

                    booked_faculty[slot_key].add(f_id)
                    booked_rooms[slot_key].add(r_id)
                    faculty_daily_load[(f_id, act_day)] = faculty_daily_load.get((f_id, act_day), 0) + 1

                    color_key = act_subj["type"]
                    card_color = COLOR_MAP.get(color_key, "purple-card")

                    master_schedule[sec_id][cand_slot][act_day] = {
                        "subject": act_subj["code"],
                        "subject_name": act_subj["name"],
                        "type": act_subj["type"],
                        "professor": chosen_f.get("name"),
                        "faculty_id": f_id,
                        "room": chosen_r.get("name"),
                        "room_id": r_id,
                        "color": card_color
                    }
                    activity_slots_assigned[act_day] = cand_slot
                    break

        # 2. Fill the remaining academic slots across Monday through Friday (all 6 periods per day)
        subj_weekly_count = {s.get("code"): 0 for s in academic_subjects}

        for day in INSTRUCTIONAL_DAYS:
            daily_subjects_assigned = set()
            if day in activity_slots_assigned:
                daily_subjects_assigned.add("ACTIVITY")

            for slot_idx, slot in enumerate(TIME_SLOTS):
                if master_schedule[sec_id][slot][day] is not None:
                    continue

                slot_key = (day, slot)
                if slot_key not in booked_faculty: booked_faculty[slot_key] = set()
                if slot_key not in booked_rooms: booked_rooms[slot_key] = set()

                candidate_subjects = [
                    s for s in academic_subjects 
                    if s.get("code") not in daily_subjects_assigned
                ]
                if not candidate_subjects:
                    candidate_subjects = list(academic_subjects)

                # Balance distribution while breaking deterministic slot patterns
                random.shuffle(candidate_subjects)
                candidate_subjects.sort(key=lambda s: subj_weekly_count.get(s.get("code"), 0))

                chosen_subject = None
                chosen_faculty = None
                chosen_room = None

                for subj in candidate_subjects:
                    s_code = subj.get("code")
                    s_type = subj.get("type", "LECTURE").upper()
                    s_dept = subj.get("department", sec_dept)

                    eligible_facs = get_eligible_faculty(s_code, s_type, s_dept)
                    avail_facs = [
                        f for f in eligible_facs
                        if f["id"] not in booked_faculty[slot_key]
                        and faculty_daily_load.get((f["id"], day), 0) < f.get("max_workload_hrs", 5.0)
                    ]
                    if not avail_facs:
                        continue

                    eligible_rms = get_eligible_rooms(s_type, sec_dept)
                    avail_rms = [r for r in eligible_rms if r["id"] not in booked_rooms[slot_key]]
                    if not avail_rms:
                        continue

                    # STAFF-ROOM BREAK / REST GAP HEURISTIC:
                    # Penalize faculty who taught in the immediately preceding slot today
                    def faculty_rest_score(f):
                        f_id = f["id"]
                        last_slot = faculty_last_slot.get((f_id, day), -99)
                        is_consecutive = (last_slot == slot_idx - 1)
                        load = faculty_daily_load.get((f_id, day), 0)
                        return (1 if is_consecutive else 0, load, random.random())

                    avail_facs.sort(key=faculty_rest_score)

                    chosen_subject = subj
                    chosen_faculty = avail_facs[0]
                    chosen_room = random.choice(avail_rms)
                    break

                # Robust fallback across all academic subjects and department faculties
                if not chosen_subject or not chosen_faculty or not chosen_room:
                    for subj in academic_subjects:
                        s_code = subj.get("code")
                        s_type = subj.get("type", "LECTURE").upper()
                        s_dept = subj.get("department", sec_dept)

                        eligible_facs = get_eligible_faculty(s_code, s_type, s_dept)
                        avail_facs = [
                            f for f in eligible_facs
                            if f["id"] not in booked_faculty[slot_key]
                            and faculty_daily_load.get((f["id"], day), 0) < f.get("max_workload_hrs", 5.0)
                        ]
                        if not avail_facs:
                            # Try any available faculty in department/college
                            avail_facs = [
                                f for f in faculties
                                if f.get("id") not in ["FA_SPORTS", "FA_LIB"]
                                and f["id"] not in booked_faculty[slot_key]
                                and faculty_daily_load.get((f["id"], day), 0) < f.get("max_workload_hrs", 5.0)
                            ]

                        if not avail_facs: continue

                        eligible_rms = get_eligible_rooms(s_type, sec_dept)
                        avail_rms = [r for r in eligible_rms if r["id"] not in booked_rooms[slot_key]]
                        if not avail_rms: continue

                        chosen_subject = subj
                        chosen_faculty = random.choice(avail_facs)
                        chosen_room = random.choice(avail_rms)
                        break

                if not chosen_subject or not chosen_faculty or not chosen_room:
                    continue

                f_id = chosen_faculty["id"]
                r_id = chosen_room["id"]
                s_code = chosen_subject.get("code")
                s_type = chosen_subject.get("type", "LECTURE").upper()

                booked_faculty[slot_key].add(f_id)
                booked_rooms[slot_key].add(r_id)
                faculty_daily_load[(f_id, day)] = faculty_daily_load.get((f_id, day), 0) + 1
                faculty_last_slot[(f_id, day)] = slot_idx
                subj_weekly_count[s_code] = subj_weekly_count.get(s_code, 0) + 1
                daily_subjects_assigned.add(s_code)

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