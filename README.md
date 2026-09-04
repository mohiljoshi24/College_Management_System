# 🎓 SSIT College Management System (CMS) & Automated Timetable Engine

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Microframework-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/Vanilla_ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active_Development-blue?style=for-the-badge)]()

An enterprise-grade Academic Operations and Automated Resource Scheduling platform designed for **Shree Swaminarayan Institute of Technology (SSIT)**. 

The system couples a heuristic **Constraint Satisfaction Problem (CSP)** solver in Python with a comprehensive **Role-Based Access Control (RBAC)** architecture—automating conflict-free academic timetables across engineering cohorts, classrooms, and specialized laboratories while monitoring real-time faculty workloads.

---

## 📌 Table of Contents

1. [Key Features & Modules](#-key-features--modules)
2. [Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
3. [Scheduling Engine & CSP Constraints](#-scheduling-engine--csp-constraints)
4. [System Architecture & Data Flow](#-system-architecture--data-flow)
5. [Technology Stack & Decisions](#-technology-stack--decisions)
6. [REST API Specification](#-rest-api-specification)
7. [Directory Structure](#-directory-structure)
8. [Getting Started & Local Setup](#-getting-started--local-setup)
9. [Engineering Highlights & Design Decisions](#-engineering-highlights--design-decisions)
10. [Roadmap](#-roadmap)

---

## 🚀 Key Features & Modules

### 🧠 1. Heuristic Constraint Satisfaction Solver
- Synthesizes conflict-free master schedules across multiple engineering departments and semesters in under a second.
- Eliminates instructor double-booking, classroom collisions, and cohort overlaps.
- Enforces strict lab-vs-lecture room routing and faculty competency validations.

### 🔐 2. Role-Based Access Control (RBAC)
- Distinct authentication flows and personalized user experiences for **Administrators**, **Faculty**, and **Students**.
- Dynamic navigation generation and client-side route guardrails (`auth.js`).
- Profile dropdown with instant sign-out and active role badges.

### 📊 3. Live Operational Dashboard
- **Executive Campus View:** Real-time KPI cards for active lectures, room occupancy percentages, and faculty counts.
- **Departmental Workload Compliance:** Dynamic visual progress bars tracking faculty hours against 5-hour daily ceilings.
- **Personalized Previews:** Tailored mini-schedules for logged-in students and professors.

### 👨‍🏫 4. Faculty & Workload Governance
- Manages instructor qualifications, departmental assignments, and verified subject competency arrays.
- Real-time visual workload indicators to prevent faculty burnout and satisfy institutional compliance.
- Interactive modal-based CRUD operations syncing atomically with backend JSON datastores.

### 🏛️ 5. Classroom & Laboratory Infrastructure Manager
- Categorizes physical rooms into standard Lecture Halls and specialized Computer/Hardware Labs.
- Tracks seating capacity, departmental ownership, and occupancy states.

### 📅 6. Multi-Cohort Filterable Timetable
- Multi-dimensional matrix view with real-time filtering by **Branch / Section Cohort**, **Professor**, and **Room**.
- High-contrast, pastel color-coding per department and laboratory course.
- Clean print-to-PDF layout with dedicated print media stylesheets.

---

## 🔐 Role-Based Access Control (RBAC)

The platform enforces a granular permission matrix across all views:

| Feature / Capability | Administrator (`admin`) | Faculty (`faculty`) | Student (`student`) |
| :--- | :---: | :---: | :---: |
| **Authentication & Profile** | Full Admin Profile | Faculty ID & Dept Mapped | Cohort & Section Mapped |
| **Dashboard Experience** | Campus-wide Analytics | Department Load & Schedule | Cohort Standing & Schedule |
| **Timetable View** | Full Matrix (All Cohorts) | Auto-Filtered to Self | Locked to Enrolled Section |
| **Trigger Solver Synthesis** | ✅ Enabled | ❌ Hidden / Read-only | ❌ Hidden / Read-only |
| **Faculty Management** | Full CRUD (Add / Delete) | Directory View (Read-only) | 🚫 Access Restricted |
| **Room Allocation** | Full CRUD (Add / Delete) | Directory View (Read-only) | 🚫 Access Restricted |
| **Attendance Portal** | Administrative Auditing | Mark Class Attendance | View Personal Attendance |
| **Institutional Reports** | Full Campus Reports | Departmental Reports | 🚫 Access Restricted |

---

## ⚙️ Scheduling Engine & CSP Constraints

The scheduling engine (`scheduler_engine.py`) models timetable generation as a multi-variable **Constraint Satisfaction Problem (CSP)** across 6 institutional lecture slots:

```
┌─────────────────────────────────────────────────────────────┐
│ 09:00 AM - 10:00 AM  │ Lecture Slot 1                       │
│ 10:00 AM - 11:00 AM  │ Lecture Slot 2                       │
│ 11:00 AM - 11:20 AM  │ ☕ SHORT BREAK                       │
│ 11:20 AM - 12:10 PM  │ Lecture Slot 3                       │
│ 12:10 PM - 01:00 PM  │ Lecture Slot 4                       │
│ 01:00 PM - 01:50 PM  │ 🍽️ LUNCH BREAK                       │
│ 01:50 PM - 02:40 PM  │ Lecture Slot 5                       │
│ 02:40 PM - 03:30 PM  │ Lecture Slot 6                       │
└─────────────────────────────────────────────────────────────┘
```

### Constraints & Heuristics Enforced

1. **5-Day Academic Week Model:** Mon–Fri operational curriculum with Saturday preserved in the UI palette as a scheduled institutional off-day.
2. **Fixed Weekly Activity Invariants:** Injects exactly **1 Library**, **1 Assignment/Tutorial**, and **1 Sports** period per cohort across distinct days.
3. **Faculty Collision Prevention (Hard):** Tracks instructor allocations via `(day, slot)` sets to guarantee zero double-booking across cohorts or classrooms.
4. **Facility Collision Prevention (Hard):** Ensures physical rooms host at most one section per time slot.
5. **Infrastructural Domain Compatibility (Hard):** Routes laboratory courses strictly to specialized labs (`LAB-CS1`, `LAB-IT1`, `LAB-EC1`, `LAB-AI`) and lecture courses to standard halls.
6. **Subject Competency Validation (Hard):** Assigns instructors strictly based on verified `subjects_can_teach` competency lists.
7. **Morning Slot Randomization (Soft):** Distributes 09:00 AM period 1 assignments across faculty to avoid repetitive locks.
8. **Staff-Room Break Interval Heuristic (Soft):** Penalizes consecutive back-to-back lecture assignments for the same professor to mitigate cognitive fatigue while complying with 5.0-hour daily caps.

---

## 🏗️ System Architecture & Data Flow

```
                     [ Client Browser (HTML5 / ES6 Vanilla) ]
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
    [ Admin View ]              [ Faculty View ]              [ Student View ]
           │                            │                            │
           └────────────────────────────┬────────────────────────────┘
                                        │  HTTP REST (Fetch API)
                                        ▼
                            [ Flask Router (app.py) ]
                          ┌─────────────┴─────────────┐
                          ▼                           ▼
                 [ Static Page Router ]       [ REST API Layer ]
                                              ┌───────┴───────┐
                                              ▼               ▼
                                    [ CSP Solver Engine ]   [ Storage DAO ]
                                    (scheduler_engine.py)  (storage_manager.py)
                                              │               │
                                              ▼               ▼
                                      [ Master Schedule ]   [ JSON Datastores ]
                                      (timetable.json)      (/data/*.json)
```

---

## 🛠️ Technology Stack & Decisions

- **Backend:** Python 3.x, Flask Micro-Framework (WSGI)
- **Frontend:** Semantic HTML5, Modern CSS3 (CSS Variables, Flexbox & CSS Grid), Vanilla JavaScript (ES6+ Fetch API)
- **Security & Session:** Client-side RBAC Session Controller (`auth.js`), Parameter Sanitization
- **Data Persistence:** Atomic JSON Datastore (DAO Pattern)
- **Iconography:** FontAwesome 6 (CDN)

### Architectural Decisions
- **Zero Heavy Frontend Dependencies:** Eliminates complex Node.js build pipelines (Webpack/Vite/Babel) to deliver instantaneous initial page loads and low-overhead DOM operations.
- **RESTful Decoupling:** Complete separation of concerns between client-side asynchronous HTTP operations and backend business logic.
- **Atomic File Storage:** File I/O operations with UTF-8 encoding and robust JSON decoding error fallback.

---

## 📡 REST API Specification

| Endpoint | Method | Payload / Query | Status Codes | Description |
| :--- | :---: | :--- | :---: | :--- |
| `/api/login` | `POST` | `{ "email": "...", "password": "..." }` | `200`, `400`, `401` | Authenticates user and returns sanitized session profile. |
| `/api/user-profile` | `GET` | `?id=Uxxx` | `200`, `400`, `404` | Retrieves public user profile without sensitive fields. |
| `/api/faculties` | `GET` | *None* | `200` | Fetches all faculty profiles and teaching competency arrays. |
| `/api/faculties` | `POST` | Faculty Object (`JSON`) | `201`, `400` | Registers a new faculty record and persists to disk. |
| `/api/faculties` | `DELETE` | `?id=FAxxx` | `200`, `400` | Removes a faculty record by identifier. |
| `/api/rooms` | `GET` | *None* | `200` | Returns all classrooms, labs, capacities, and department tags. |
| `/api/rooms` | `POST` | Room Object (`JSON`) | `201`, `400` | Creates a new classroom or laboratory record. |
| `/api/rooms` | `DELETE` | `?id=Rxxx` | `200`, `400` | Deletes a classroom or laboratory record by identifier. |
| `/api/sections` | `GET` | *None* | `200` | Retrieves academic cohort partitions and batch identifiers. |
| `/api/timetable` | `GET` | *None* | `200` | Returns the current master multi-cohort schedule matrix. |
| `/api/generate-timetable` | `POST` | *None* | `200` | Triggers the heuristic CSP solver to synthesize a new schedule. |
| `/api/dashboard-stats` | `GET` | *None* | `200` | Returns aggregated metrics, room occupancies, and compliance stats. |

---

## 📁 Directory Structure

```
College_Management_System/
├── app.py                     # Flask application, REST endpoints & static routes
├── scheduler_engine.py        # Heuristic Constraint Satisfaction (CSP) engine
├── storage_manager.py         # Atomic JSON persistence handler (DAO pattern)
├── requirements.txt           # Python dependency manifest
├── data/                      # Persistent JSON Datastores
│   ├── faculties.json         # Faculty profiles, qualifications & teaching allowances
│   ├── rooms.json             # Classroom and laboratory infrastructure records
│   ├── sections.json          # Academic cohorts partitioned by branch and semester
│   ├── subjects.json          # Multi-semester curriculum and credit requirements
│   ├── timetable.json         # Master weekly multi-cohort schedule matrix
│   └── users.json             # User accounts and RBAC role assignments
└── frontend/                  # Client-Side Web Application
    ├── auth.js                # Shared RBAC session controller & route guard
    ├── dashboard.html         # Executive campus metrics & personalized previews
    ├── faculties.html         # Faculty workload manager & staff directory
    ├── login_page.html        # Secure authentication entry gateway
    ├── room_allocation.html   # Classroom and laboratory infrastructure manager
    ├── timetable.html         # Dynamic schedule matrix with print-ready PDF styling
    ├── attendance.html        # Attendance portal interface (in development)
    ├── reports.html           # Institutional analytics hub (in development)
    └── settings.html          # System and profile configuration view
```

---

## 💻 Getting Started & Local Setup

### Prerequisites
- **Python 3.8+** installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/mohiljoshi24/College_Management_System.git
cd College_Management_System
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 💡 Engineering Highlights & Design Decisions

- **Circular Dependency Elimination:** Isolated file storage into a pure utility module (`storage_manager.py`), preventing circular imports on Flask server bootstrap.
- **REST Method Normalization:** Standardized Flask decorators with explicit HTTP method allowances (`GET`, `POST`, `DELETE`) to avoid `405 Method Not Allowed` exceptions.
- **Multi-Cohort Data Partitioning:** Structured the schedule matrix as a keyed multi-dimensional dictionary partitioned by Section IDs (`SEC-CS-SEM1-A`, `SEC-IT-SEM3-A`), enabling independent cohort filtering.
- **Modal Input Validation:** Implemented HTML5 modal dialogs with client validation to enforce structured JSON schemas before saving to disk.

---

## 🗺️ Roadmap

- [x] **Automated CSP Timetable Engine** (Conflict-free multi-cohort generator)
- [x] **Role-Based Access Control (RBAC)** (Admin, Faculty, and Student workflows)
- [ ] **Student Management System** (Student directory, enrollment & batch assignments)
- [ ] **Timetable-Linked Attendance Portal** (Roster attendance marking & calculation)
- [ ] **Defaulter Analytics & Reports Hub** (Attendance < 75% alerts with CSV/PDF export)
- [ ] **PostgreSQL Migration** (SQLAlchemy ORM integration for high-concurrency deployments)

---

## 👨‍💻 Author & Notes

Developed by **Mohil Joshi** — Computer Science & Engineering.

> *Built from the ground up as a foundational full-stack software engineering project, focusing on clean architecture, algorithmic scheduling, and pragmatic system design.*

