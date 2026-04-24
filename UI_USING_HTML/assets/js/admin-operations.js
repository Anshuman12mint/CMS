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
    setLoading,
    escapeHtml,
    sortByDateDesc,
    getMeetingsHref
} from "./core.js";

function buildLookup(items, idField, labelField) {
    return new Map(items.map(function (item) {
        const label = labelField(item);
        return [item[idField], label];
    }));
}

async function init() {
    const session = requireSession(["Admin", "Staff"]);
    if (!session) {
        return;
    }
    hydrateShell(session, { pageTitle: "CMS Operations" });

    setLoading(byId("attendance-table"), "Loading attendance...");
    setLoading(byId("marks-table"), "Loading marks...");
    setLoading(byId("meetings-ops"), "Loading meetings...");

    try {
        const [attendance, feeSummary, marks, meetings, students, subjects] = await Promise.all([
            apiRequest("/api/attendance"),
            apiRequest("/api/reports/fees/summary"),
            apiRequest("/api/marks"),
            apiRequest("/api/meetings"),
            apiRequest("/api/students"),
            apiRequest("/api/subjects")
        ]);

        byId("paid-count").textContent = feeSummary.paidCount;
        byId("pending-count").textContent = feeSummary.pendingCount;
        byId("paid-amount").textContent = formatCurrency(feeSummary.paidAmount);
        byId("pending-amount").textContent = formatCurrency(feeSummary.pendingAmount);

        const studentNames = buildLookup(students, "studentId", function (student) {
            return [student.firstName, student.lastName].filter(Boolean).join(" ") || "Student " + student.studentId;
        });
        const subjectNames = buildLookup(subjects, "subjectId", function (subject) {
            return subject.subjectName || subject.subjectCode || "Subject " + subject.subjectId;
        });

        const recentAttendance = sortByDateDesc(attendance, "date").slice(0, 8);
        if (!recentAttendance.length) {
            byId("attendance-table").innerHTML = '<tr><td colspan="4">' + renderEmptyState("No attendance entries yet.") + "</td></tr>";
        } else {
            byId("attendance-table").innerHTML = recentAttendance.map(function (record) {
                return [
                    "<tr>",
                    "<td>",
                    escapeHtml(studentNames.get(record.studentId) || "Student " + record.studentId),
                    "</td>",
                    "<td>",
                    escapeHtml(record.studentId || "--"),
                    "</td>",
                    "<td>",
                    escapeHtml(formatDate(record.date)),
                    "</td>",
                    "<td>",
                    renderStatusBadge(record.status),
                    "</td>",
                    "</tr>"
                ].join("");
            }).join("");
        }

        const recentMarks = sortByDateDesc(marks, "examDate").slice(0, 8);
        if (!recentMarks.length) {
            byId("marks-table").innerHTML = '<tr><td colspan="5">' + renderEmptyState("No marks are recorded yet.") + "</td></tr>";
        } else {
            byId("marks-table").innerHTML = recentMarks.map(function (mark) {
                return [
                    "<tr>",
                    "<td>",
                    escapeHtml(studentNames.get(mark.studentId) || "Student " + mark.studentId),
                    "</td>",
                    "<td>",
                    escapeHtml(subjectNames.get(mark.subjectId) || "Subject " + mark.subjectId),
                    "</td>",
                    "<td>",
                    escapeHtml(mark.examType || "--"),
                    "</td>",
                    "<td>",
                    escapeHtml(mark.marksObtained || "--"),
                    " / ",
                    escapeHtml(mark.maxMarks || "--"),
                    "</td>",
                    "<td>",
                    escapeHtml(mark.grade || "--"),
                    "</td>",
                    "</tr>"
                ].join("");
            }).join("");
        }

        if (!meetings.length) {
            byId("meetings-ops").innerHTML = renderEmptyState("No meetings available.");
        } else {
            byId("meetings-ops").innerHTML = meetings.slice(0, 4).map(function (meeting) {
                return [
                    '<article class="list-item"><div class="list-item-header"><h4>',
                    escapeHtml(meeting.title || "Untitled meeting"),
                    "</h4>",
                    renderStatusBadge(meeting.status),
                    '</div><p>',
                    escapeHtml(formatDateTime(meeting.scheduledStartAt)),
                    '</p><div class="meta-row"><a class="inline-link" href="',
                    getMeetingsHref(meeting.meetingId),
                    '">Open meeting room</a></div></article>'
                ].join("");
            }).join("");
        }
    } catch (error) {
        byId("attendance-table").innerHTML = '<tr><td colspan="4">' + renderErrorState(error.message) + "</td></tr>";
        byId("marks-table").innerHTML = '<tr><td colspan="5">' + renderErrorState(error.message) + "</td></tr>";
        byId("meetings-ops").innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
