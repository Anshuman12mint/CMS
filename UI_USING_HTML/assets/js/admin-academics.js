import {
    byId,
    requireSession,
    hydrateShell,
    apiRequest,
    renderErrorState,
    renderEmptyState,
    setLoading,
    escapeHtml
} from "./core.js";

let courses = [];

function renderCourses() {
    const target = byId("courses-table");
    if (!courses.length) {
        target.innerHTML = '<tr><td colspan="4">' + renderEmptyState("No course records exist yet.") + "</td></tr>";
        return;
    }

    target.innerHTML = courses.map(function (course) {
        return [
            '<tr data-course-code="',
            escapeHtml(course.courseCode),
            '">',
            "<td><strong>",
            escapeHtml(course.courseCode || "--"),
            "</strong></td>",
            "<td>",
            escapeHtml(course.courseName || "--"),
            "</td>",
            "<td>",
            escapeHtml(course.courseDescription || "--"),
            "</td>",
            "<td><button class=\"button-secondary compact-button\" type=\"button\">View Subjects</button></td>",
            "</tr>"
        ].join("");
    }).join("");

    target.querySelectorAll("[data-course-code]").forEach(function (row) {
        row.addEventListener("click", function () {
            loadSubjects(row.getAttribute("data-course-code"));
        });
    });
}

async function loadSubjects(courseCode) {
    byId("subject-heading").textContent = courseCode ? "Subjects for " + courseCode : "Subjects";
    setLoading(byId("subjects-table"), "Loading subjects...");
    try {
        const subjects = await apiRequest("/api/subjects?courseCode=" + encodeURIComponent(courseCode));
        if (!subjects.length) {
            byId("subjects-table").innerHTML = '<tr><td colspan="4">' + renderEmptyState("No subjects are mapped to this course yet.") + "</td></tr>";
            return;
        }

        byId("subjects-table").innerHTML = subjects.map(function (subject) {
            return [
                "<tr>",
                "<td><strong>",
                escapeHtml(subject.subjectCode || "--"),
                "</strong></td>",
                "<td>",
                escapeHtml(subject.subjectName || "--"),
                "</td>",
                "<td>",
                escapeHtml(subject.courseCode || "--"),
                "</td>",
                "<td>",
                escapeHtml(subject.subjectDescription || "--"),
                "</td>",
                "</tr>"
            ].join("");
        }).join("");
    } catch (error) {
        byId("subjects-table").innerHTML = '<tr><td colspan="4">' + renderErrorState(error.message) + "</td></tr>";
    }
}

async function init() {
    const session = requireSession(["Admin", "Staff"]);
    if (!session) {
        return;
    }
    hydrateShell(session, { pageTitle: "CMS Academics" });

    setLoading(byId("courses-table"), "Loading courses...");
    setLoading(byId("subjects-table"), "Loading subjects...");

    try {
        courses = await apiRequest("/api/courses");
        renderCourses();
        byId("course-count").textContent = courses.length;
        if (courses.length) {
            loadSubjects(courses[0].courseCode);
        } else {
            byId("subjects-table").innerHTML = '<tr><td colspan="4">' + renderEmptyState("Subjects will appear after courses are created.") + "</td></tr>";
        }
    } catch (error) {
        byId("courses-table").innerHTML = '<tr><td colspan="4">' + renderErrorState(error.message) + "</td></tr>";
        byId("subjects-table").innerHTML = '<tr><td colspan="4">' + renderErrorState(error.message) + "</td></tr>";
    }
}

document.addEventListener("DOMContentLoaded", init);
