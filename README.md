# SSIT College Management System (CMS) & Automated Timetable Engine

An enterprise-grade Academic Operations and Automated Resource Scheduling platform. The system implements a heuristic Constraint Satisfaction Problem (CSP) solver in Python to generate conflict-free academic timetables across multiple engineering cohorts, departments, classrooms, and laboratories while monitoring faculty workloads in real time.

---

## Key Features

- **Heuristic Constraint Solver Engine:** Generates conflict-free academic schedules across all student cohorts, eliminating professor double-booking and room collisions.
- **Infrastructural Room Allocation:** Differentiates between standard lecture halls and specialized computing/hardware labs with real-time capacity and occupancy metrics.
- **Faculty & Workload Governance:** Manages faculty qualifications, departmental assignments, teaching competency arrays, and enforces daily 5-hour workload ceilings.
- **Interactive Multi-Cohort Timetable:** Dynamic schedule matrix supporting real-time filtering by Branch, Semester Cohort, Professor, and Classroom with native print-to-PDF support.
- **Live Metrics Dashboard:** Aggregates real-time statistics including room utilization percentages, active lectures, and department-wise compliance indicators.
- **Native In-Browser Modals:** In-place data creation and deletion (CRUD) directly synced with the datastore via dedicated REST endpoints.

---

## Technology Stack

- **Frontend:**   Vanilla Semantic HTML5, CSS3 (CSS Variables, Grid & Flexbox), Modern JavaScript (ES6+ Fetch API)
- **Backend:**    Python 3.x, Flask Micro-Framework
- **Data Layer:** Atomic JSON Datastores (DAO Architecture)
- **Icons:**      FontAwesome 6 (CDN)

---

### Architectural Decisions

- **No Heavy Frontend Frameworks (React/Vue/Tailwind):** Built using native web standards to eliminate heavy node dependency trees, avoid complex Webpack/Vite build pipelines, ensure instant initial page rendering, and maintain low-level control over the Document Object Model (DOM) lifecycle[cite: 1, 2, 3].
- **Flask REST Architecture:** A lightweight WSGI implementation delivering clear separation of concerns between client-side asynchronous HTTP operations and backend business logic[cite: 1, 2, 3].
- **Atomic File-Based Storage:** Safe local persistence using a custom storage manager with automatic directory creation and robust JSON decoding error handling.

---

## System Architecture & Data Flow

[ Client Browser (HTML5 / ES6 Fetch) ]
│
▼  (HTTP GET / POST / DELETE)
[ Flask Router (app.py) ]
├── Page Routing (Static File Serving)
└── REST API Layer
│
┌────────┴─────────────────────────┐
▼                                  ▼
[ Heuristic Engine ]              [ Storage Manager ]
(scheduler_engine.py)             (storage_manager.py)
│                                  │
▼                                  ▼
[ Dynamic Schedule Matrix ]        [ JSON Datastores (/data) ]

---

## REST API Specification

| Endpoint | Method | Payload / Query | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/login` | `POST` | `{ "email": "...", "password": "..." }` | `200`, `401`   Authenticates administrator credentials. |
| `/api/faculties` | `GET` | *None* | `200` | Retrieves all registered faculty profiles and workload parameters[cite: 2]. |
| `/api/faculties` | `POST` | Faculty Object (`JSON`) | `201`, `400` | Creates a new faculty record and persists to disk[cite: 2]. |
| `/api/faculties` | `DELETE` | `?id=FAxxx` | `200`, `400` | Removes a faculty record by identifier[cite: 2]. |
| `/api/rooms` | `GET` | *None* | `200` | Fetches all classrooms, labs, capacities, and department tags[cite: 3]. |
| `/api/rooms` | `POST` | Room Object (`JSON`) | `201`, `400` | Adds a new classroom or specialized laboratory[cite: 3]. |
| `/api/rooms` | `DELETE` | `?id=Rxxx` | `200`, `400` | Deletes a classroom or laboratory record by identifier[cite: 3]. |
| `/api/sections` | `GET` | *None* | `200` | Retrieves defined student cohorts and batch sizes. |
| `/api/timetable` | `GET` | *None* | `200` | Fetches the current master multi-cohort timetable matrix[cite: 1]. |
| `/api/generate-timetable` | `POST` | *None* | `200` | Triggers the heuristic constraint satisfaction solver[cite: 1]. |
| `/api/dashboard-stats` | `GET` | *None* | `200` | Returns live room occupancy and departmental workload compliance. |

---

## Scheduling Engine & Constraint Specifications

The scheduling engine (`scheduler_engine.py`) models timetable synthesis as a multi-variable Constraint Satisfaction Problem (CSP) across 6 institutional lecture slots:

* **Slot 1:** 09:00 AM – 10:00 AM
* **Slot 2:** 10:00 AM – 11:00 AM
* **Break:** 11:00 AM – 11:20 AM *(Short Break)*
* **Slot 3:** 11:20 AM – 12:10 PM
* **Slot 4:** 12:10 PM – 01:00 PM
* **Break:** 01:00 PM – 01:50 PM *(Lunch Break)*
* **Slot 5:** 01:50 PM – 02:40 PM
* **Slot 6:** 02:40 PM – 03:30 PM

### Constraints Enforced

1. **Faculty Collision Prevention (Hard Constraint):** Tracks assigned instructor states via `(day, slot)` sets to guarantee no professor is double-booked across different cohorts or rooms.
2. **Facility Collision Prevention (Hard Constraint):** Ensures physical classrooms and laboratories can host at most one section per time slot.
3. **Infrastructural Domain Compatibility (Hard Constraint):** Strictly routes laboratory courses (`type: "LAB"`) to dedicated computer or hardware labs, while lecture courses are allocated to lecture halls.
4. **Subject Competency Validation (Hard Constraint):** Assigns instructors strictly based on their verified `subjects_can_teach` competency lists.
5. **Workload Distribution (Soft Constraint):** Caps daily lectures per cohort to prevent student and faculty fatigue.

---

## Directory Structure

College_Management_System/
├── app.py                     # Core Flask application, API endpoints & page routes
├── scheduler_engine.py        # Heuristic constraint solver & timetable synthesizer
├── storage_manager.py         # File I/O handler with atomic JSON persistence
├── requirements.txt           # Python dependency manifest
├── data/                      # JSON persistence datastores
│   ├── faculties.json         # Faculty profiles, qualifications & teaching allowances
│   ├── rooms.json             # Classroom and laboratory infrastructure records
│   ├── sections.json          # Academic cohorts partitioned by branch and semester
│   ├── subjects.json          # Multi-semester curriculum and credit hours
│   ├── timetable.json         # Generated master weekly schedule matrix
│   └── users.json             # Administrative authentication credentials
└── frontend/                  # Static client-side assets
├── dashboard.html         # Analytics dashboard, KPIs and mini schedule preview
├── faculties.html         # Faculty workload manager with interactive modals[cite: 
├── login_page.html        # Authentication entry gateway
├── room_allocation.html   # Room & Lab infrastructure manager[cite: 3]
└── timetable.html         # Filterable master schedule view with PDF export styling[cite: 1]

---

## Engineering Challenges Overcome

**Circular Dependency Resolution:** Isolated storage_manager.py into a pure utility module to eliminate runtime circular self-imports on server initialization.

**REST Method Normalization:** Standardized Flask route decorators with explicit methods=["GET", "POST", "DELETE"] allowances to prevent HTTP 405 Method Not Allowed exceptions.

**Multi-Cohort Data Overwriting:** Refactored a flat schedule matrix into a multi-dimensional key-value store partitioned by Section IDs (SEC-CS-SEM1-A, SEC-IT-SEM3-A), allowing independent multi-cohort filtering.

**Modal Input Validation:** Replaced primitive browser prompt inputs with accessible HTML5 modal overlay dialogs to prevent malformed JSON schemas from entering the datastore[cite: 2, 3].

---

## Future Roadmap

**[ ] Role-Based Access Control (RBAC):** JWT-secured role routing for Administrators, Faculty, and Students.

**[ ] Advanced Optimization:** Genetic Algorithm (GA) integration to minimize faculty idle gap periods between classes.

**[ ] Database Migration:** Migration to PostgreSQL with SQLAlchemy ORM for higher transactional concurrency.

**[ ] Direct Vector PDF Rendering:** Native server-side vector PDF generation for administrative printouts.

---

## last but not the least: 
**its my very first project that to as a sem-1 CSE student.**
