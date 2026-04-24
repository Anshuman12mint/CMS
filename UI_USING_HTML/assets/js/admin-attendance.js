import {
    apiRequest,
    asArray,
    buildHref,
    escapeHtml,
    formatDate,
    formatNumber,
    renderEmptyState,
    renderErrorState,
    renderStatusBadge,
    requireSession,
    sortByDateDesc
} from "./core.js";
import { mountAppShell, updateShellNotifications } from "./components/layout.js";
import { renderListCard, renderStatCard } from "./components/card.js";
import { renderFormGrid, serializeForm } from "./components/form.js";
import { openModal, closeModal } from "./components/modal.js";
import { registerAssistantContext } from "./components/chatbot.js";

let pageRoot = null;
let attendance = [];
let students = [];
let filteredAttendance = [];

function studentName(student) {
    return [student?.firstName, student?.lastName].filter(Boolean).join(" ") || "Student";
}

function studentMap() {
    return new Map(students.map(function (student) {
        return [student.studentId, studentName(student)];
    }));
}

function normalizePayload(values) {
    return {
        studentId: values.studentId ? Number(values.studentId) : null,
        date: values.date || null,
        status: values.status || null
    };
}

function renderTrend(records) {
    const recent = sortByDateDesc(records, "date").slice(0, 20).reduce(function (accumulator, record) {
        const key = record.date || "Unknown";
        const bucket = accumulator[key] || { label: formatDate(key), present: 0, absent: 0 };
        if (String(record.status || "").toLowerCase() === "present") {
            bucket.present += 1;
        } else {
            bucket.absent += 1;
        }
        accumulator[key] = bucket;
        return accumulator;
    }, {});

    const items = Object.values(recent).slice(0, 6);
    if (!items.length) {
        return renderEmptyState("Attendance trends will appear once records are available.");
    }

    const maxValue = Math.max(...items.map(function (item) {
        return item.present + item.absent;
    }), 1);

    return '<div class="dashboard-chart"><div class="chart-bars">' + items.map(function (item) {
        const total = item.present + item.absent;
        return '<div class="chart-row"><div class="chart-head"><strong>' + escapeHtml(item.label) + '</strong><span class="muted">' + escapeHtml(String(total)) + ' records</span></div><div class="chart-track"><div class="chart-fill success" style="width:' + Math.max(8, Math.round((item.present / maxValue) * 100)) + '%"></div></div><div class="chart-track"><div class="chart-fill warning" style="width:' + Math.max(8, Math.round((item.absent / maxValue) * 100)) + '%"></div></div></div>';
    }).join("") + "</div></div>";
}

function openAttendanceModal(record = null) {
    openModal({
        title: record ? "Edit Attendance Record" : "Add Attendance Record",
        description: record
            ? "Update the student attendance status for the selected day."
            : "Create a new attendance entry linked to a student profile.",
        body: [
            '<form id="attendance-form" class="field-grid">',
            renderFormGrid([
                { name: "studentId", label: "Student", type: "select", value: record?.studentId || "", required: true, options: [{ value: "", label: "Select student" }].concat(students.map(function (student) { return { value: student.studentId, label: studentName(student) + " (" + student.studentId + ")" }; })) },
                { name: "date", label: "Date", type: "date", value: record?.date || "", required: true },
                { name: "status", label: "Status", type: "select", value: record?.status || "", required: true, options: [{ value: "", label: "Select status" }, "Present", "Absent"] }
            ]),
            '<div id="attendance-form-status" class="status-banner info compact">Save to update the attendance register.</div>',
            '<div class="button-row"><button class="button" type="submit">',
            record ? "Save Record" : "Create Record",
            '</button><button class="button-quiet" type="button" id="cancel-attendance-form">Cancel</button></div></form>'
        ].join(""),
        onOpen: function () {
            document.getElementById("cancel-attendance-form").addEventListener("click", closeModal);
            document.getElementById("attendance-form").addEventListener("submit", async function (event) {
                event.preventDefault();
                const status = document.getElementById("attendance-form-status");
                status.textContent = "Saving attendance...";
                status.className = "status-banner info compact";

                try {
                    const payload = normalizePayload(serializeForm(event.currentTarget));
                    await apiRequest(record ? "/api/attendance/" + record.attendanceId : "/api/attendance", {
                        method: record ? "PUT" : "POST",
                        body: payload
                    });
                    status.textContent = "Attendance saved.";
                    status.className = "status-banner success compact";
                    await loadPageData();
                    closeModal();
                } catch (error) {
                    status.textContent = error.message;
                    status.className = "status-banner error compact";
                }
            });
        }
    });
}

function applyFilters() {
    const search = document.getElementById("attendance-search").value.trim().toLowerCase();
    const statusFilter = document.getElementById("attendance-status-filter").value;
    const dateFilter = document.getElementById("attendance-date-filter").value;
    const names = studentMap();

    filteredAttendance = attendance.filter(function (record) {
        const matchesStatus = !statusFilter || String(record.status || "").toLowerCase() === statusFilter.toLowerCase();
        const matchesDate = !dateFilter || record.date === dateFilter;
        const haystack = [names.get(record.studentId), record.studentId, record.date, record.status].join(" ").toLowerCase();
        const matchesSearch = !search || haystack.includes(search);
        return matchesStatus && matchesDate && matchesSearch;
    });

    renderAttendanceTable();
}

function renderAttendanceTable() {
    const target = document.getElementById("attendance-table");
    const names = studentMap();

    if (!filteredAttendance.length) {
        target.innerHTML = '<tr><td colspan="5">' + renderEmptyState("No attendance records match the current filters.") + "</td></tr>";
        return;
    }

    target.innerHTML = filteredAttendance.map(function (record) {
        return [
            "<tr><td>",
            escapeHtml(names.get(record.studentId) || ("Student " + record.studentId)),
            '</td><td>',
            escapeHtml(record.studentId || "--"),
            '</td><td>',
            escapeHtml(formatDate(record.date)),
            '</td><td>',
            renderStatusBadge(record.status),
            '</td><td><button class="button-quiet compact-button" type="button" data-attendance-edit="',
            escapeHtml(record.attendanceId),
            '">Edit</button></td></tr>'
        ].join("");
    }).join("");

    target.querySelectorAll("[data-attendance-edit]").forEach(function (button) {
        button.addEventListener("click", function () {
            const recordId = Number(button.getAttribute("data-attendance-edit"));
            const record = attendance.find(function (item) {
                return item.attendanceId === recordId;
            });
            openAttendanceModal(record);
        });
    });
}

function renderLayout() {
    const presentCount = attendance.filter(function (record) {
        return String(record.status || "").toLowerCase() === "present";
    }).length;
    const absentCount = attendance.filter(function (record) {
        return String(record.status || "").toLowerCase() === "absent";
    }).length;
    const attendanceHealth = attendance.length ? Math.round((presentCount / attendance.length) * 100) + "%" : "--";
    const recentAbsences = sortByDateDesc(attendance.filter(function (record) {
        return String(record.status || "").toLowerCase() === "absent";
    }), "date").slice(0, 4);
    const names = studentMap();

    pageRoot.innerHTML = [
        '<section class="page-header"><div><span class="section-kicker">Attendance</span><h3>Daily attendance register</h3><p>Track present and absent status, manage records, and keep attendance history in a dedicated operational module.</p></div><div class="toolbar-actions"><button class="button" type="button" id="add-attendance-button">Add Record</button><a class="button-secondary" href="',
        buildHref("admin/students.html"),
        '">Student Center</a></div></section>',
        '<section class="stats-grid">',
        renderStatCard({ label: "Total Records", value: formatNumber(attendance.length), note: "Entries currently available in the register.", iconName: "calendar" }),
        renderStatCard({ label: "Present", value: formatNumber(presentCount), note: "Students marked present in visible records.", iconName: "dashboard", accent: "success" }),
        renderStatCard({ label: "Absent", value: formatNumber(absentCount), note: "Attendance entries requiring follow-up.", iconName: "users", accent: "warning" }),
        renderStatCard({ label: "Attendance Health", value: attendanceHealth, note: "Presence rate across the loaded register.", iconName: "chart", accent: "info" }),
        '</section><section class="panel-grid"><article class="page-panel"><div class="toolbar"><div><span class="section-kicker">Trend</span><h4 class="page-panel-title">Recent attendance mix</h4></div><span class="tag">Daily signal</span></div>',
        renderTrend(attendance),
        '</article><article class="page-panel"><span class="section-kicker">Absence watchlist</span><h4 class="page-panel-title">Recent absences</h4><div class="list-stack">',
        (recentAbsences.length ? recentAbsences.map(function (record) {
            return renderListCard({
                title: names.get(record.studentId) || ("Student " + record.studentId),
                description: "Absent entry recorded in the daily register.",
                meta: formatDate(record.date),
                status: "Absent",
                iconName: "calendar"
            });
        }).join("") : renderEmptyState("No recent absences are visible.")),
        '</div></article></section><section class="page-panel filter-panel"><div class="toolbar"><div><span class="section-kicker">Filters</span><h4 class="page-panel-title">Attendance controls</h4></div><span class="tag">Table view</span></div><div class="field-grid two"><div class="field"><label for="attendance-search">Search</label><input id="attendance-search" type="search" placeholder="Search by student name, ID, date, or status"></div><div class="field"><label for="attendance-status-filter">Status</label><select id="attendance-status-filter"><option value="">All statuses</option><option value="Present">Present</option><option value="Absent">Absent</option></select></div><div class="field span-2"><label for="attendance-date-filter">Date</label><input id="attendance-date-filter" type="date"></div></div></section>',
        '<section class="page-panel scroll"><div class="toolbar"><div><span class="section-kicker">Register</span><h4 class="page-panel-title">Attendance table</h4></div><span class="tag">',
        escapeHtml(formatNumber(attendance.length)),
        ' records</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Student</th><th>Student ID</th><th>Date</th><th>Status</th><th>Action</th></tr></thead><tbody id="attendance-table"></tbody></table></div></section>'
    ].join("");

    document.getElementById("add-attendance-button").addEventListener("click", function () {
        openAttendanceModal();
    });

    const quickAction = document.querySelector('[data-quick-action="create-attendance"]');
    if (quickAction) {
        quickAction.addEventListener("click", function () {
            openAttendanceModal();
        });
    }

    document.getElementById("attendance-search").addEventListener("input", applyFilters);
    document.getElementById("attendance-status-filter").addEventListener("change", applyFilters);
    document.getElementById("attendance-date-filter").addEventListener("change", applyFilters);

    applyFilters();
}

async function loadPageData() {
    const [attendanceRecords, studentRecords] = await Promise.all([
        apiRequest("/api/attendance"),
        apiRequest("/api/students")
    ]);

    attendance = asArray(attendanceRecords);
    students = asArray(studentRecords);
    renderLayout();

    updateShellNotifications([
        {
            title: "Attendance loaded",
            description: formatNumber(attendance.length) + " register records are available."
        },
        {
            title: "Live edits enabled",
            description: "Use Add Record or Edit to update attendance through the backend."
        },
        {
            title: "Trend panel ready",
            description: "Recent presence and absence patterns are summarized above the table."
        }
    ]);

    registerAssistantContext({
        pageTitle: "attendance management",
        summary: [
            "This page holds " + formatNumber(attendance.length) + " attendance records in a dedicated table view.",
            "You can add or edit records from modal forms backed by the attendance endpoint.",
            "The trend panel and absence watchlist summarize recent movement in the register."
        ],
        suggestions: [
            "Summarize attendance",
            "How many absences are there?",
            "How do I add an attendance record?",
            "What does the trend panel show?"
        ],
        metrics: {
            attendance: attendance.length
                ? Math.round((attendance.filter(function (record) { return String(record.status || "").toLowerCase() === "present"; }).length / attendance.length) * 100) + "% present overall"
                : "No attendance records",
            attendanceNote: "Use filters to isolate date and status.",
            students: formatNumber(students.length),
            studentNote: "Student profiles are available for attendance mapping."
        }
    });
}

async function init() {
    const session = requireSession(["Admin", "Staff"]);
    if (!session) {
        return;
    }

    pageRoot = mountAppShell({
        session,
        currentKey: "attendance",
        workspaceLabel: "Attendance",
        brandTitle: "Attendance Register",
        brandCopy: "A focused operational module for daily attendance records, trends, and status review.",
        title: "Attendance",
        subtitle: "Dedicated table, filters, and real edit flows for present or absent status",
        searchPlaceholder: "Search attendance or students",
        quickActions: [
            { label: "Add Record", action: "create-attendance", iconName: "plus", variant: "button" },
            { label: "Students", href: buildHref("admin/students.html"), iconName: "users", variant: "button-secondary" }
        ],
        notifications: [
            { title: "Loading attendance", description: "Fetching register history and student links." }
        ]
    });

    pageRoot.innerHTML = '<div class="loading-state">Loading attendance records...</div>';

    try {
        await loadPageData();
    } catch (error) {
        pageRoot.innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
