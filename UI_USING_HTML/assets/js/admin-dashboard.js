import {
    byId,
    requireSession,
    hydrateShell,
    apiRequest,
    renderErrorState,
    renderEmptyState,
    renderStatusBadge,
    formatDate,
    formatDateTime,
    formatCurrency,
    setLoading,
    getMeetingsHref,
    escapeHtml
} from "./core.js";

function renderSummary(summary, meetings) {
    const cards = [
        ["Total Students", summary.totalStudents, "Current active student records"],
        ["Total Teachers", summary.totalTeachers, "Faculty records in the system"],
        ["Total Staff", summary.totalStaff, "Operational and support staff"],
        ["Total Courses", summary.totalCourses, "Active academic programs"],
        ["Total Subjects", summary.totalSubjects, "Subjects available for allocation"],
        ["Total Users", summary.totalUsers, "Authenticated accounts"],
        ["Pending Fees", summary.pendingFeeCount, formatCurrency(summary.pendingFeeAmount) + " outstanding"],
        ["Meetings", meetings.length, "Visible sessions from the meetings module"]
    ];

    byId("dashboard-stats").innerHTML = cards.map(function (item) {
        return [
            '<article class="stat-card">',
            '<p class="stat-label">',
            escapeHtml(item[0]),
            "</p>",
            '<p class="stat-value">',
            escapeHtml(item[1]),
            "</p>",
            '<p class="stat-note">',
            escapeHtml(item[2]),
            "</p>",
            "</article>"
        ].join("");
    }).join("");
}

function renderAdmissions(admissions) {
    const target = byId("admissions-table");
    if (!admissions.length) {
        target.innerHTML = '<tr><td colspan="5">' + renderEmptyState("No admissions are available yet.") + "</td></tr>";
        return;
    }

    target.innerHTML = admissions.map(function (admission) {
        const fullName = [admission.firstName, admission.lastName].filter(Boolean).join(" ");
        return [
            "<tr>",
            "<td><strong>",
            escapeHtml(fullName || "Unknown student"),
            "</strong><br><span class=\"muted\">",
            escapeHtml(admission.email || "--"),
            "</span></td>",
            "<td>",
            escapeHtml(admission.courseCode || "--"),
            "</td>",
            "<td>",
            escapeHtml(formatDate(admission.admissionDate)),
            "</td>",
            "<td>",
            escapeHtml(admission.guardianName || "--"),
            "</td>",
            "<td>",
            renderStatusBadge("Completed"),
            "</td>",
            "</tr>"
        ].join("");
    }).join("");
}

function renderFeeSummary(summary) {
    const target = byId("fee-watchlist");
    const pendingFees = summary.pendingFees || [];
    if (!pendingFees.length) {
        target.innerHTML = renderEmptyState("No pending fee records right now.");
        return;
    }

    target.innerHTML = [
        '<article class="list-item"><div class="list-item-header"><h4>Pending amount</h4>',
        renderStatusBadge("Pending"),
        '</div><p>',
        escapeHtml(formatCurrency(summary.pendingAmount)),
        ' across ',
        escapeHtml(summary.pendingCount),
        " fee records.</p></article>",
        pendingFees.slice(0, 3).map(function (fee) {
            return [
                '<article class="list-item"><div class="list-item-header"><h4>Student ID ',
                escapeHtml(fee.studentId || "--"),
                "</h4>",
                renderStatusBadge(fee.status),
                '</div><p>',
                escapeHtml(formatCurrency(fee.amount)),
                " due on ",
                escapeHtml(formatDate(fee.dueDate)),
                "</p></article>"
            ].join("");
        }).join("")
    ].join("");
}

function renderMeetings(meetings) {
    const target = byId("meeting-overview");
    if (!meetings.length) {
        target.innerHTML = renderEmptyState("No meetings are visible for this user.");
        return;
    }

    target.innerHTML = meetings.slice(0, 4).map(function (meeting) {
        return [
            '<article class="timeline-item"><strong>',
            escapeHtml(meeting.title || "Untitled meeting"),
            "</strong>",
            '<span class="meta">',
            escapeHtml(formatDateTime(meeting.scheduledStartAt)),
            " | ",
            escapeHtml(meeting.provider || "Meeting"),
            "</span>",
            '<span class="muted">',
            escapeHtml(meeting.description || "No description"),
            "</span>",
            '<div class="meta-row"><a class="inline-link" href="',
            getMeetingsHref(meeting.meetingId),
            '">Open meeting</a></div></article>'
        ].join("");
    }).join("");
}

async function init() {
    const session = requireSession(["Admin", "Staff"]);
    if (!session) {
        return;
    }

    hydrateShell(session, {
        pageTitle: "CMS Dashboard"
    });

    setLoading(byId("dashboard-stats"));
    setLoading(byId("admissions-table"), "Loading admissions...");
    setLoading(byId("fee-watchlist"), "Loading fee summary...");
    setLoading(byId("meeting-overview"), "Loading meetings...");

    try {
        const [summary, feeSummary, meetings] = await Promise.all([
            apiRequest("/api/dashboard"),
            apiRequest("/api/reports/fees/summary"),
            apiRequest("/api/meetings")
        ]);

        renderSummary(summary, meetings);
        renderAdmissions(summary.recentAdmissions || []);
        renderFeeSummary(feeSummary);
        renderMeetings(meetings);
    } catch (error) {
        byId("dashboard-stats").innerHTML = renderErrorState(error.message);
        byId("admissions-table").innerHTML = '<tr><td colspan="5">' + renderErrorState(error.message) + "</td></tr>";
        byId("fee-watchlist").innerHTML = renderErrorState(error.message);
        byId("meeting-overview").innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
