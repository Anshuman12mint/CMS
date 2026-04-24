import {
    byId,
    requireSession,
    hydrateShell,
    apiRequest,
    renderErrorState,
    renderEmptyState,
    renderStatusBadge,
    formatDate,
    formatCurrency,
    setLoading,
    escapeHtml,
    asArray,
    sortByDateDesc
} from "./core.js";

let allStudents = [];
let filteredStudents = [];
let selectedStudentId = null;

function getStudentName(student) {
    return [student.firstName, student.lastName].filter(Boolean).join(" ") || "Unnamed student";
}

function computeAttendanceLabel(records) {
    const total = records.length;
    if (!total) {
        return "No records";
    }
    const present = records.filter(function (item) {
        return String(item.status || "").toLowerCase() === "present";
    }).length;
    return Math.round((present / total) * 100) + "% Present";
}

function computeFeeLabel(fees) {
    const pending = fees.filter(function (item) {
        return String(item.status || "").toLowerCase() === "pending";
    });
    if (!pending.length) {
        return "Paid";
    }
    return formatCurrency(pending.reduce(function (sum, fee) {
        return sum + Number(fee.amount || 0);
    }, 0)) + " Pending";
}

async function fetchStudentDetails(studentId) {
    return Promise.all([
        apiRequest("/api/students/" + studentId),
        apiRequest("/api/attendance?studentId=" + studentId),
        apiRequest("/api/fees?studentId=" + studentId),
        apiRequest("/api/marks?studentId=" + studentId)
    ]);
}

function renderStudentTable() {
    const body = byId("students-table");
    if (!filteredStudents.length) {
        body.innerHTML = '<tr><td colspan="6">' + renderEmptyState("No students match the current filters.") + "</td></tr>";
        return;
    }

    body.innerHTML = filteredStudents.map(function (student) {
        return [
            "<tr data-student-row=\"",
            escapeHtml(student.studentId),
            '">',
            "<td><strong>",
            escapeHtml(getStudentName(student)),
            "</strong><br><span class=\"muted\">",
            escapeHtml(student.email || "--"),
            "</span></td>",
            "<td>",
            escapeHtml(student.courseCode || "--"),
            "</td>",
            "<td>",
            escapeHtml(student.guardianName || "--"),
            "<br><span class=\"muted\">",
            escapeHtml(student.guardianContact || "--"),
            "</span></td>",
            "<td>",
            escapeHtml(formatDate(student.admissionDate)),
            "</td>",
            "<td>",
            renderStatusBadge(student.feeLabel),
            "</td>",
            "<td>",
            renderStatusBadge(student.attendanceLabel),
            "</td>",
            "</tr>"
        ].join("");
    }).join("");

    body.querySelectorAll("[data-student-row]").forEach(function (row) {
        row.addEventListener("click", function () {
            selectedStudentId = Number(row.getAttribute("data-student-row"));
            loadDetail(selectedStudentId);
        });
    });
}

function applyFilters() {
    const courseValue = byId("course-filter").value;
    const searchValue = byId("student-search").value.trim().toLowerCase();
    filteredStudents = allStudents.filter(function (student) {
        const matchesCourse = !courseValue || courseValue === "ALL" || student.courseCode === courseValue;
        const haystack = [
            getStudentName(student),
            student.email,
            student.guardianName,
            student.courseCode,
            student.studentId
        ].join(" ").toLowerCase();
        const matchesSearch = !searchValue || haystack.includes(searchValue);
        return matchesCourse && matchesSearch;
    });
    renderStudentTable();
}

function renderCourseFilter() {
    const select = byId("course-filter");
    const uniqueCourses = [...new Set(allStudents.map(function (student) {
        return student.courseCode;
    }).filter(Boolean))];
    select.innerHTML = '<option value="ALL">All Courses</option>' + uniqueCourses.map(function (courseCode) {
        return '<option value="' + escapeHtml(courseCode) + '">' + escapeHtml(courseCode) + "</option>";
    }).join("");
}

function renderRecentList(targetId, items, renderItem, emptyMessage) {
    const target = byId(targetId);
    if (!items.length) {
        target.innerHTML = renderEmptyState(emptyMessage);
        return;
    }
    target.innerHTML = items.map(renderItem).join("");
}

async function loadDetail(studentId) {
    const panel = byId("student-detail");
    setLoading(panel, "Loading student detail...");

    try {
        const [student, attendance, fees, marks] = await fetchStudentDetails(studentId);
        const recentAttendance = sortByDateDesc(attendance, "date").slice(0, 3);
        const recentFees = sortByDateDesc(fees, "dueDate").slice(0, 3);
        const recentMarks = sortByDateDesc(marks, "examDate").slice(0, 3);
        const pendingFees = fees.filter(function (fee) {
            return String(fee.status || "").toLowerCase() === "pending";
        });

        panel.innerHTML = [
            '<div><span class="section-kicker">Selected student</span><h4>',
            escapeHtml(getStudentName(student)),
            "</h4><p class=\"muted\">",
            escapeHtml(student.courseCode || "--"),
            " | ",
            escapeHtml(student.email || "--"),
            "</p></div>",
            '<div class="detail-grid">',
            '<div class="detail-pair"><span>Date of Birth</span><strong>',
            escapeHtml(formatDate(student.dob)),
            '</strong></div>',
            '<div class="detail-pair"><span>Gender</span><strong>',
            escapeHtml(student.gender || "--"),
            '</strong></div>',
            '<div class="detail-pair"><span>Guardian</span><strong>',
            escapeHtml(student.guardianName || "--"),
            '</strong></div>',
            '<div class="detail-pair"><span>Guardian Contact</span><strong>',
            escapeHtml(student.guardianContact || "--"),
            '</strong></div>',
            '<div class="detail-pair"><span>Phone</span><strong>',
            escapeHtml(student.phoneNumber || "--"),
            '</strong></div>',
            '<div class="detail-pair"><span>Address</span><strong>',
            escapeHtml(student.address || "--"),
            "</strong></div></div>",
            '<div class="mini-grid">',
            '<article class="mini-card"><h4>Attendance</h4><p class="strong">',
            escapeHtml(computeAttendanceLabel(attendance)),
            '</p><p class="muted">',
            escapeHtml(attendance.length),
            ' records</p></article>',
            '<article class="mini-card"><h4>Fees</h4><p class="strong">',
            escapeHtml(computeFeeLabel(fees)),
            '</p><p class="muted">',
            escapeHtml(pendingFees.length),
            ' pending records</p></article>',
            '<article class="mini-card"><h4>Marks</h4><p class="strong">',
            escapeHtml(marks.length),
            '</p><p class="muted">Recorded assessments</p></article>',
            '<article class="mini-card"><h4>Admission Date</h4><p class="strong">',
            escapeHtml(formatDate(student.admissionDate)),
            '</p><p class="muted">Student profile created</p></article>',
            "</div>",
            '<div class="detail-section"><span class="section-kicker">Recent attendance</span><div id="detail-attendance"></div></div>',
            '<div class="detail-section"><span class="section-kicker">Recent fees</span><div id="detail-fees"></div></div>',
            '<div class="detail-section"><span class="section-kicker">Recent marks</span><div id="detail-marks"></div></div>'
        ].join("");

        renderRecentList("detail-attendance", recentAttendance, function (entry) {
            return '<div class="detail-line"><strong>' + escapeHtml(formatDate(entry.date)) + '</strong><span>' + renderStatusBadge(entry.status) + "</span></div>";
        }, "No attendance entries yet.");

        renderRecentList("detail-fees", recentFees, function (entry) {
            return '<div class="detail-line"><strong>' + escapeHtml(formatCurrency(entry.amount)) + '</strong><span>' + renderStatusBadge(entry.status) + " due " + escapeHtml(formatDate(entry.dueDate)) + "</span></div>";
        }, "No fee records yet.");

        renderRecentList("detail-marks", recentMarks, function (entry) {
            return '<div class="detail-line"><strong>' + escapeHtml(entry.examType || "Assessment") + '</strong><span>' + escapeHtml(entry.grade || "--") + " | " + escapeHtml(entry.marksObtained || "--") + "/" + escapeHtml(entry.maxMarks || "--") + "</span></div>";
        }, "No marks recorded yet.");
    } catch (error) {
        panel.innerHTML = renderErrorState(error.message);
    }
}

async function init() {
    const session = requireSession(["Admin", "Staff"]);
    if (!session) {
        return;
    }

    hydrateShell(session, {
        pageTitle: "CMS Students"
    });

    setLoading(byId("students-table"), "Loading students...");
    setLoading(byId("student-detail"), "Loading student detail...");

    try {
        const [students, attendance, fees] = await Promise.all([
            apiRequest("/api/students"),
            apiRequest("/api/attendance"),
            apiRequest("/api/fees")
        ]);

        const attendanceByStudent = new Map();
        asArray(attendance).forEach(function (record) {
            const list = attendanceByStudent.get(record.studentId) || [];
            list.push(record);
            attendanceByStudent.set(record.studentId, list);
        });

        const feesByStudent = new Map();
        asArray(fees).forEach(function (fee) {
            const list = feesByStudent.get(fee.studentId) || [];
            list.push(fee);
            feesByStudent.set(fee.studentId, list);
        });

        allStudents = asArray(students).map(function (student) {
            return {
                ...student,
                attendanceLabel: computeAttendanceLabel(attendanceByStudent.get(student.studentId) || []),
                feeLabel: computeFeeLabel(feesByStudent.get(student.studentId) || [])
            };
        });

        renderCourseFilter();
        applyFilters();

        if (allStudents.length) {
            selectedStudentId = allStudents[0].studentId;
            loadDetail(selectedStudentId);
        } else {
            byId("student-detail").innerHTML = renderEmptyState("Student details will appear here after records exist.");
        }
    } catch (error) {
        byId("students-table").innerHTML = '<tr><td colspan="6">' + renderErrorState(error.message) + "</td></tr>";
        byId("student-detail").innerHTML = renderErrorState(error.message);
    }

    byId("course-filter").addEventListener("change", applyFilters);
    byId("student-search").addEventListener("input", applyFilters);
}

document.addEventListener("DOMContentLoaded", init);
