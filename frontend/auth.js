/**
 * SSIT CMS - Role-Based Access Control (RBAC) & Session Manager
 * Handles user authentication, role checks, dynamic header injection, and role-based navigation.
 */

const SSIT_AUTH = {
    STORAGE_KEY: "ssit_user",

    getUser() {
        try {
            const raw = localStorage.getItem(this.STORAGE_KEY) || sessionStorage.getItem(this.STORAGE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            console.error("Error reading auth session:", e);
            return null;
        }
    },

    setUser(user, remember = true) {
        const str = JSON.stringify(user);
        if (remember) {
            localStorage.setItem(this.STORAGE_KEY, str);
        } else {
            sessionStorage.setItem(this.STORAGE_KEY, str);
        }
    },

    logout() {
        localStorage.removeItem(this.STORAGE_KEY);
        sessionStorage.removeItem(this.STORAGE_KEY);
        window.location.href = "/";
    },

    requireAuth(allowedRoles = []) {
        const user = this.getUser();
        const currentPath = window.location.pathname;

        // If not logged in and not on login page, redirect to login
        if (!user && currentPath !== "/" && !currentPath.includes("login")) {
            window.location.href = "/";
            return null;
        }

        // If logged in and role is restricted for this page
        if (user && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
            alert("Access Restricted: This module requires " + allowedRoles.join(" or ") + " privileges.");
            window.location.href = "/dashboard";
            return null;
        }

        return user;
    },

    initPage(allowedRoles = []) {
        const user = this.requireAuth(allowedRoles);
        if (!user) return null;

        this.injectAuthStyles();
        this.renderHeader(user);
        this.renderSidebar(user);
        return user;
    },

    renderHeader(user) {
        const userInfoContainer = document.querySelector(".user-info");
        if (!userInfoContainer) return;

        // Role badge styling config
        const roleBadges = {
            admin: { text: "ADMIN", bg: "#e0e7ff", color: "#3730a3", border: "#c7d2fe" },
            faculty: { text: "FACULTY", bg: "#dcfce7", color: "#166534", border: "#bbf7d0" },
            student: { text: "STUDENT", bg: "#fef3c7", color: "#92400e", border: "#fde68a" }
        };
        const roleInfo = roleBadges[user.role] || roleBadges.admin;

        userInfoContainer.classList.add("ssit-profile-dropdown-wrapper");
        const semTag = user.semester ? " • Sem " + user.semester : "";
        
        userInfoContainer.innerHTML = `
            <img src="${user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'}"
                 alt="${user.name}" class="user-avatar" style="border: 2px solid ${roleInfo.border};">
            <div style="display: flex; flex-direction: column; text-align: left;">
                <span style="font-weight: 600; font-size: 13px; color: #1e293b; line-height: 1.2;">${user.name || 'User'}</span>
                <span style="font-size: 10px; font-weight: 700; color: ${roleInfo.color}; background: ${roleInfo.bg}; padding: 1px 6px; border-radius: 4px; display: inline-block; width: fit-content; margin-top: 2px;">
                    ${roleInfo.text}
                </span>
            </div>
            <i class="fa-solid fa-chevron-down" style="font-size: 10px; color: #64748b; margin-left: 4px;"></i>

            <!-- Dropdown Menu -->
            <div class="ssit-dropdown-menu" id="ssitUserDropdown">
                <div class="dropdown-header">
                    <div style="font-weight: 700; color: #0f172a; font-size: 13px;">${user.name}</div>
                    <div style="font-size: 11px; color: #64748b;">${user.email}</div>
                    <div style="font-size: 11px; color: #3b82f6; margin-top: 4px; font-weight: 500;">
                        <i class="fa-solid fa-building-columns"></i> ${user.department || 'SSIT'}${semTag}
                    </div>
                </div>
                <div class="dropdown-divider"></div>
                <a href="/dashboard" class="dropdown-item"><i class="fa-solid fa-gauge-high"></i> Dashboard</a>
                <a href="/timetable" class="dropdown-item"><i class="fa-regular fa-calendar-days"></i> Timetable</a>
                <div class="dropdown-divider"></div>
                <button onclick="SSIT_AUTH.logout()" class="dropdown-item logout-btn">
                    <i class="fa-solid fa-arrow-right-from-bracket"></i> Sign Out
                </button>
            </div>
        `;

        // Toggle Dropdown logic
        userInfoContainer.addEventListener("click", (e) => {
            e.stopPropagation();
            const dropdown = document.getElementById("ssitUserDropdown");
            if (dropdown) {
                dropdown.classList.toggle("show");
            }
        });

        document.addEventListener("click", () => {
            const dropdown = document.getElementById("ssitUserDropdown");
            if (dropdown) dropdown.classList.remove("show");
        });
    },

    renderSidebar(user) {
        const navList = document.querySelector(".nav-list");
        if (!navList) return;

        const path = window.location.pathname;

        // Navigation configurations per role
        const menus = {
            admin: [
                { href: "/dashboard", icon: "fa-solid fa-chart-line", label: "Dashboard" },
                { href: "/timetable", icon: "fa-regular fa-calendar-days", label: "Timetable View" },
                { href: "/faculties", icon: "fa-solid fa-user-group", label: "Faculty Manager" },
                { href: "/room_allocation", icon: "fa-solid fa-door-open", label: "Room Allocation" },
                { href: "/attendance", icon: "fa-solid fa-clipboard-user", label: "Attendance Portal" },
                { href: "/reports", icon: "fa-regular fa-file-lines", label: "Reports & Analytics" },
                { href: "/settings", icon: "fa-solid fa-gear", label: "Settings" }
            ],
            faculty: [
                { href: "/dashboard", icon: "fa-solid fa-chart-line", label: "Faculty Dashboard" },
                { href: "/timetable", icon: "fa-regular fa-calendar-days", label: "My Teaching Schedule" },
                { href: "/faculties", icon: "fa-solid fa-user-group", label: "Faculty Directory" },
                { href: "/room_allocation", icon: "fa-solid fa-door-open", label: "Classrooms & Labs" },
                { href: "/attendance", icon: "fa-solid fa-clipboard-user", label: "Mark Attendance" },
                { href: "/reports", icon: "fa-regular fa-file-lines", label: "Academic Reports" },
                { href: "/settings", icon: "fa-solid fa-gear", label: "Settings" }
            ],
            student: [
                { href: "/dashboard", icon: "fa-solid fa-chart-line", label: "Student Dashboard" },
                { href: "/timetable", icon: "fa-regular fa-calendar-days", label: "Class Timetable" },
                { href: "/attendance", icon: "fa-solid fa-clipboard-user", label: "My Attendance" },
                { href: "/settings", icon: "fa-solid fa-gear", label: "My Profile" }
            ]
        };

        const activeMenu = menus[user.role] || menus.admin;

        navList.innerHTML = activeMenu.map(item => {
            const isActive = path === item.href || (item.href !== "/dashboard" && path.includes(item.href));
            return `
                <li class="nav-item ${isActive ? 'active' : ''}">
                    <a href="${item.href}">
                        <i class="${item.icon}"></i>
                        <span>${item.label}</span>
                    </a>
                </li>
            `;
        }).join("");
    },

    injectAuthStyles() {
        if (document.getElementById("ssit-auth-injected-styles")) return;
        const style = document.createElement("style");
        style.id = "ssit-auth-injected-styles";
        style.innerHTML = `
            .ssit-profile-dropdown-wrapper {
                position: relative;
                cursor: pointer;
                user-select: none;
            }
            .ssit-dropdown-menu {
                display: none;
                position: absolute;
                top: calc(100% + 10px);
                right: 0;
                background: #ffffff;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.06);
                border: 1px solid #e2e8f0;
                width: 220px;
                z-index: 1000;
                overflow: hidden;
                animation: fadeInDown 0.15s ease-out;
            }
            .ssit-dropdown-menu.show {
                display: block;
            }
            @keyframes fadeInDown {
                from { opacity: 0; transform: translateY(-6px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .dropdown-header {
                padding: 12px 16px;
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }
            .dropdown-divider {
                height: 1px;
                background: #f1f5f9;
                margin: 4px 0;
            }
            .dropdown-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 16px;
                color: #334155;
                text-decoration: none;
                font-size: 12px;
                font-weight: 500;
                transition: background 0.15s;
                background: none;
                border: none;
                width: 100%;
                text-align: left;
                cursor: pointer;
            }
            .dropdown-item:hover {
                background: #f1f5f9;
                color: #0284c7;
            }
            .dropdown-item.logout-btn {
                color: #dc2626;
            }
            .dropdown-item.logout-btn:hover {
                background: #fee2e2;
                color: #b91c1c;
            }
            .role-badge-pill {
                font-size: 11px;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: 9999px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        `;
        document.head.appendChild(style);
    }
};

window.SSIT_AUTH = SSIT_AUTH;
