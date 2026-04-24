import {
    byId,
    requireSession,
    hydrateShell,
    apiRequest,
    renderErrorState,
    renderEmptyState,
    renderStatusBadge,
    formatCurrency,
    formatDate,
    formatDateTime,
    escapeHtml,
    getMeetingsHref
} from "./core.js";

function studentName(student) {
    return [student.firstName, student.lastName].filter(Boolean).join(" ") || "Student";
}

async function init() {
    const session = requireSession(["Student"]);
    if (!session) {
        return;
    }

    hydrateShell(session, { pageTitle: "CMS Student Portal" });
    const root = byId("student-main");
    root.innerHTML = '<div class="loading-state">Loading your student data...</div>';

    if (!session.studentId) {
        root.innerHTML = renderErrorState("This user is logged in as Student, but no linked studentId was found.");
        return;
    }

    try {
        const [student, attendance, fees, marks, meetings, subjects] = await Promise.all([
            apiRequest("/api/students/" + session.studentId),
            apiRequest("/api/attendance?studentId=" + session.studentId),
            apiRequest("/api/fees?studentId=" + session.studentId),
            apiRequest("/api/marks?studentId=" + session.studentId),
            apiRequest("/api/meetings"),
            apiRequest("/api/subjects")
        ]);

        const subjectNames = new Map(subjects.map(function (subject) {
            return [subject.subjectId, subject.subjectName || subject.subjectCode || ("Subject " + subject.subjectId)];
        }));

        const presentDays = attendance.filter(function (record) {
            return String(record.status || "").toLowerCase() === "present";
        }).length;
        const totalFees = fees.reduce(function (sum, fee) {
            return sum + Number(fee.amount || 0);
        }, 0);
        const pendingFees = fees.filter(function (fee) {
            return String(fee.status || "").toLowerCase() === "pending";
        });
        const recentAttendance = [...attendance].sort(function (left, right) {
            return new Date(right.date || 0) - new Date(left.date || 0);
        }).slice(0, 3);
        const recentFees = [...fees].sort(function (left, right) {
            return new Date(right.dueDate || 0) - new Date(left.dueDate || 0);
        }).slice(0, 3);
        const recentMarks = [...marks].sort(function (left, right) {
            return new Date(right.examDate || 0) - new Date(left.examDate || 0);
        }).slice(0, 6);

        root.innerHTML = [
            '<section class="page-header"><div><h3>Hello, ',
            escapeHtml(studentName(student)),
            '</h3><p data-page-description>Your attendance, fee records, marks, and accessible meetings are loaded from the backend.</p></div><div class="toolbar-actions"><a class="button" href="',
            getMeetingsHref(),
            '">Meetings</a></div></section>',
            '<section class="stats-grid">',
            '<article class="stat-card"><p class="stat-label">Present Days</p><p class="stat-value">',
            escapeHtml(presentDays),
            '</p><p class="stat-note">',
            escapeHtml(attendance.length - presentDays),
            ' absences in the visible history.</p></article>',
            '<article class="stat-card"><p class="stat-label">Total Fees</p><p class="stat-value">',
            escapeHtml(formatCurrency(totalFees)),
            '</p><p class="stat-note">Visible fee records for your account.</p></article>',
            '<article class="stat-card"><p class="stat-label">Pending Fees</p><p class="stat-value">',
            escapeHtml(formatCurrency(pendingFees.reduce(function (sum, fee) { return sum + Number(fee.amount || 0); }, 0))),
            '</p><p class="stat-note">',
            escapeHtml(pendingFees.length),
            ' pending records.</p></article>',
            '<article class="stat-card"><p class="stat-label">Marks Recorded</p><p class="stat-value">',
            escapeHtml(marks.length),
            '</p><p class="stat-note">Assessments available in the system.</p></article>',
            "</section>",
            '<section class="panel-grid"><article class="page-panel"><span class="section-kicker">Recent attendance</span><h4 class="page-panel-title">Attendance feed</h4><div id="student-attendance"></div></article>',
            '<article class="page-panel"><span class="section-kicker">Fees</span><h4 class="page-panel-title">Finance summary</h4><div id="student-fees"></div></article></section>',
            '<section class="section-grid"><article class="page-panel scroll"><span class="section-kicker">Recent marks</span><h4 class="page-panel-title">Assessment history</h4><table class="data-table"><thead><tr><th>Subject</th><th>Exam Type</th><th>Score</th><th>Grade</th></tr></thead><tbody id="student-marks"></tbody></table></article>',
            '<article class="page-panel"><span class="section-kicker">Meetings</span><h4 class="page-panel-title">Meetings you can join</h4><div id="student-meetings"></div></article></section>'
        ].join("");

        byId("student-attendance").innerHTML = recentAttendance.length ? recentAttendance.map(function (record) {
            return '<article class="timeline-item"><strong>' + escapeHtml(formatDate(record.date)) + '</strong><span class="meta">' + renderStatusBadge(record.status) + "</span></article>";
        }).join("") : renderEmptyState("No attendance history is available yet.");

        byId("student-fees").innerHTML = recentFees.length ? recentFees.map(function (fee) {
            return '<article class="list-item"><div class="list-item-header"><h4>' + escapeHtml(formatCurrency(fee.amount)) + "</h4>" + renderStatusBadge(fee.status) + '</div><p>Due ' + escapeHtml(formatDate(fee.dueDate)) + "</p></article>";
        }).join("") : renderEmptyState("No fee entries are available yet.");

        byId("student-marks").innerHTML = recentMarks.length ? recentMarks.map(function (mark) {
            return "<tr><td>" + escapeHtml(subjectNames.get(mark.subjectId) || ("Subject " + mark.subjectId)) + "</td><td>" + escapeHtml(mark.examType || "--") + "</td><td>" + escapeHtml(mark.marksObtained || "--") + " / " + escapeHtml(mark.maxMarks || "--") + "</td><td>" + escapeHtml(mark.grade || "--") + "</td></tr>";
        }).join("") : '<tr><td colspan="4">' + renderEmptyState("No marks are available yet.") + "</td></tr>";

        byId("student-meetings").innerHTML = meetings.length ? meetings.map(function (meeting) {
            return '<article class="list-item"><div class="list-item-header"><h4>' + escapeHtml(meeting.title || "Untitled meeting") + "</h4>" + renderStatusBadge(meeting.status) + '</div><p>' + escapeHtml(formatDateTime(meeting.scheduledStartAt)) + '</p><div class="meta-row"><a class="inline-link" href="' + getMeetingsHref(meeting.meetingId) + '">Join and chat</a></div></article>';
        }).join("") : renderEmptyState("No meetings are available for your account.");
    } catch (error) {
        root.innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
