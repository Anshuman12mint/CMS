import {
    byId,
    requireSession,
    hydrateShell,
    apiRequest,
    renderErrorState,
    renderEmptyState,
    renderStatusBadge,
    formatDateTime,
    setLoading,
    escapeHtml,
    getMeetingsHref
} from "./core.js";

function teacherName(teacher) {
    return [teacher.firstName, teacher.lastName].filter(Boolean).join(" ") || "Teacher";
}

async function init() {
    const session = requireSession(["Teacher"]);
    if (!session) {
        return;
    }

    hydrateShell(session, { pageTitle: "CMS Teacher Workspace" });
    setLoading(byId("teacher-main"), "Loading your teaching workspace...");

    try {
        const [teachers, courses, subjects, marks, meetings] = await Promise.all([
            apiRequest("/api/teachers"),
            apiRequest("/api/courses"),
            apiRequest("/api/subjects"),
            apiRequest("/api/marks"),
            apiRequest("/api/meetings")
        ]);

        const teacher = teachers.find(function (item) {
            return String(item.email || "").toLowerCase() === String(session.email || "").toLowerCase();
        });

        if (!teacher) {
            byId("teacher-main").innerHTML = renderEmptyState("This user is authenticated, but no teacher profile is linked by email.");
            return;
        }

        const assignedCourses = courses.filter(function (course) {
            return teacher.courseCodes.includes(course.courseCode);
        });
        const assignedSubjects = subjects.filter(function (subject) {
            return teacher.subjectIds.includes(subject.subjectId);
        });
        const relevantMarks = marks.filter(function (mark) {
            return teacher.subjectIds.includes(mark.subjectId);
        }).slice(0, 8);

        const courseStudentCounts = await Promise.all(teacher.courseCodes.map(async function (courseCode) {
            const students = await apiRequest("/api/students?courseCode=" + encodeURIComponent(courseCode));
            return { courseCode, count: students.length };
        }));

        byId("teacher-main").innerHTML = [
            '<section class="page-header"><div><h3>Welcome back, ',
            escapeHtml(teacherName(teacher)),
            '</h3><p data-page-description>Your assigned courses, subjects, meetings, and recent marks are loaded from the backend.</p></div><div class="toolbar-actions"><a class="button" href="',
            getMeetingsHref(),
            '">Open Meetings</a></div></section>',
            '<section class="stats-grid">',
            '<article class="stat-card"><p class="stat-label">Assigned Courses</p><p class="stat-value">',
            escapeHtml(assignedCourses.length),
            '</p><p class="stat-note">Mapped through teacher-course assignments.</p></article>',
            '<article class="stat-card"><p class="stat-label">Assigned Subjects</p><p class="stat-value">',
            escapeHtml(assignedSubjects.length),
            '</p><p class="stat-note">Mapped through teacher-subject assignments.</p></article>',
            '<article class="stat-card"><p class="stat-label">Students Covered</p><p class="stat-value">',
            escapeHtml(courseStudentCounts.reduce(function (sum, item) { return sum + item.count; }, 0)),
            '</p><p class="stat-note">Across the assigned course list.</p></article>',
            '<article class="stat-card"><p class="stat-label">Meetings Visible</p><p class="stat-value">',
            escapeHtml(meetings.length),
            '</p><p class="stat-note">Available for join or management.</p></article>',
            "</section>",
            '<section class="panel-grid"><article class="page-panel"><span class="section-kicker">Courses</span><h4 class="page-panel-title">Assigned courses</h4><div id="teacher-courses"></div></article>',
            '<article class="page-panel"><span class="section-kicker">Subjects</span><h4 class="page-panel-title">Assigned subjects</h4><div id="teacher-subjects"></div></article></section>',
            '<section class="section-grid"><article class="page-panel scroll"><span class="section-kicker">Recent marks</span><h4 class="page-panel-title">Recent assessments on your subjects</h4><table class="data-table"><thead><tr><th>Student ID</th><th>Subject</th><th>Exam</th><th>Score</th></tr></thead><tbody id="teacher-marks"></tbody></table></article>',
            '<article class="page-panel"><span class="section-kicker">Meetings</span><h4 class="page-panel-title">Meetings you can open</h4><div id="teacher-meetings"></div></article></section>'
        ].join("");

        byId("teacher-courses").innerHTML = assignedCourses.length ? assignedCourses.map(function (course) {
            const match = courseStudentCounts.find(function (item) {
                return item.courseCode === course.courseCode;
            });
            return [
                '<article class="list-item"><div class="list-item-header"><h4>',
                escapeHtml(course.courseCode),
                "</h4>",
                renderStatusBadge((match?.count || 0) + " students"),
                '</div><p>',
                escapeHtml(course.courseName || "--"),
                "</p></article>"
            ].join("");
        }).join("") : renderEmptyState("No course assignments are currently mapped.");

        byId("teacher-subjects").innerHTML = assignedSubjects.length ? assignedSubjects.map(function (subject) {
            return [
                '<article class="list-item"><div class="list-item-header"><h4>',
                escapeHtml(subject.subjectName || "--"),
                "</h4>",
                renderStatusBadge(subject.subjectCode || "Subject"),
                '</div><p>',
                escapeHtml(subject.subjectDescription || "No description"),
                "</p></article>"
            ].join("");
        }).join("") : renderEmptyState("No subject assignments are currently mapped.");

        byId("teacher-marks").innerHTML = relevantMarks.length ? relevantMarks.map(function (mark) {
            const subject = assignedSubjects.find(function (item) {
                return item.subjectId === mark.subjectId;
            });
            return [
                "<tr><td>",
                escapeHtml(mark.studentId || "--"),
                "</td><td>",
                escapeHtml(subject?.subjectName || subject?.subjectCode || "Subject " + mark.subjectId),
                "</td><td>",
                escapeHtml(mark.examType || "--"),
                "</td><td>",
                escapeHtml(mark.marksObtained || "--"),
                " / ",
                escapeHtml(mark.maxMarks || "--"),
                "</td></tr>"
            ].join("");
        }).join("") : '<tr><td colspan="4">' + renderEmptyState("No marks are recorded yet for your assigned subjects.") + "</td></tr>";

        byId("teacher-meetings").innerHTML = meetings.length ? meetings.map(function (meeting) {
            return [
                '<article class="list-item"><div class="list-item-header"><h4>',
                escapeHtml(meeting.title || "Untitled meeting"),
                "</h4>",
                renderStatusBadge(meeting.status),
                '</div><p>',
                escapeHtml(formatDateTime(meeting.scheduledStartAt)),
                '</p><div class="meta-row"><a class="inline-link" href="',
                getMeetingsHref(meeting.meetingId),
                '">Join and chat</a></div></article>'
            ].join("");
        }).join("") : renderEmptyState("No meetings are available.");
    } catch (error) {
        byId("teacher-main").innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
