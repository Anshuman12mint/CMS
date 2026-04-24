import {
    apiRequest,
    asArray,
    buildHref,
    escapeHtml,
    formatDate,
    formatNumber,
    renderEmptyState,
    renderErrorState,
    requireSession,
    sortByDateDesc
} from "./core.js";
import { mountAppShell, updateShellNotifications } from "./components/layout.js";
import { renderListCard, renderStatCard } from "./components/card.js";
import { renderFormGrid, serializeForm } from "./components/form.js";
import { openModal, closeModal } from "./components/modal.js";
import { registerAssistantContext } from "./components/chatbot.js";

let pageRoot = null;
let marks = [];
let students = [];
let subjects = [];
let filteredMarks = [];

function studentName(student) {
    return [student?.firstName, student?.lastName].filter(Boolean).join(" ") || "Student";
}

function subjectName(subject) {
    return subject?.subjectName || subject?.subjectCode || "Subject";
}

function studentLookup() {
    return new Map(students.map(function (student) {
        return [student.studentId, studentName(student)];
    }));
}

function subjectLookup() {
    return new Map(subjects.map(function (subject) {
        return [subject.subjectId, subjectName(subject)];
    }));
}

function normalizePayload(values) {
    return {
        studentId: values.studentId ? Number(values.studentId) : null,
        subjectId: values.subjectId ? Number(values.subjectId) : null,
        semester: values.semester ? Number(values.semester) : null,
        examType: values.examType || null,
        marksObtained: values.marksObtained ? Number(values.marksObtained) : null,
        maxMarks: values.maxMarks ? Number(values.maxMarks) : null,
        grade: values.grade || null,
        examDate: values.examDate || null
    };
}

function openMarkModal(mark = null) {
    openModal({
        title: mark ? "Edit Mark Entry" : "Add Mark Entry",
        description: mark
            ? "Update exam details, score, or grade for the selected assessment."
            : "Create a new subject-wise assessment record linked to a student.",
        body: [
            '<form id="mark-form" class="field-grid">',
            renderFormGrid([
                { name: "studentId", label: "Student", type: "select", value: mark?.studentId || "", required: true, options: [{ value: "", label: "Select student" }].concat(students.map(function (student) { return { value: student.studentId, label: studentName(student) + " (" + student.studentId + ")" }; })) },
                { name: "subjectId", label: "Subject", type: "select", value: mark?.subjectId || "", required: true, options: [{ value: "", label: "Select subject" }].concat(subjects.map(function (subject) { return { value: subject.subjectId, label: subjectName(subject) + " (" + (subject.subjectCode || subject.subjectId) + ")" }; })) },
                { name: "semester", label: "Semester", type: "number", value: mark?.semester || "", min: "1", step: "1" },
                { name: "examType", label: "Exam Type", value: mark?.examType || "", required: true },
                { name: "marksObtained", label: "Marks Obtained", type: "number", value: mark?.marksObtained || "", required: true, min: "0", step: "0.01" },
                { name: "maxMarks", label: "Max Marks", type: "number", value: mark?.maxMarks || "", required: true, min: "1", step: "0.01" },
                { name: "grade", label: "Grade", value: mark?.grade || "" },
                { name: "examDate", label: "Exam Date", type: "date", value: mark?.examDate || "", required: true }
            ]),
            '<div id="mark-form-status" class="status-banner info compact">Save to update the marks register.</div>',
            '<div class="button-row"><button class="button" type="submit">',
            mark ? "Save Mark" : "Create Mark",
            '</button><button class="button-quiet" type="button" id="cancel-mark-form">Cancel</button></div></form>'
        ].join(""),
        onOpen: function () {
            document.getElementById("cancel-mark-form").addEventListener("click", closeModal);
            document.getElementById("mark-form").addEventListener("submit", async function (event) {
                event.preventDefault();
                const status = document.getElementById("mark-form-status");
                status.textContent = "Saving mark entry...";
                status.className = "status-banner info compact";

                try {
                    const payload = normalizePayload(serializeForm(event.currentTarget));
                    await apiRequest(mark ? "/api/marks/" + mark.markId : "/api/marks", {
                        method: mark ? "PUT" : "POST",
                        body: payload
                    });
                    status.textContent = "Mark saved.";
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
    const search = document.getElementById("mark-search").value.trim().toLowerCase();
    const subjectFilter = document.getElementById("mark-subject-filter").value;
    const examFilter = document.getElementById("mark-exam-filter").value.trim().toLowerCase();
    const studentsById = studentLookup();
    const subjectsById = subjectLookup();

    filteredMarks = marks.filter(function (mark) {
        const matchesSubject = !subjectFilter || String(mark.subjectId) === subjectFilter;
        const matchesExam = !examFilter || String(mark.examType || "").toLowerCase().includes(examFilter);
        const haystack = [
            studentsById.get(mark.studentId),
            subjectsById.get(mark.subjectId),
            mark.examType,
            mark.grade,
            mark.studentId
        ].join(" ").toLowerCase();
        const matchesSearch = !search || haystack.includes(search);
        return matchesSubject && matchesExam && matchesSearch;
    });

    renderMarksTable();
}

function renderMarksTable() {
    const target = document.getElementById("marks-table");
    const studentsById = studentLookup();
    const subjectsById = subjectLookup();

    if (!filteredMarks.length) {
        target.innerHTML = '<tr><td colspan="7">' + renderEmptyState("No mark entries match the current filters.") + "</td></tr>";
        return;
    }

    target.innerHTML = filteredMarks.map(function (mark) {
        return [
            "<tr><td>",
            escapeHtml(studentsById.get(mark.studentId) || ("Student " + mark.studentId)),
            '</td><td>',
            escapeHtml(subjectsById.get(mark.subjectId) || ("Subject " + mark.subjectId)),
            '</td><td>',
            escapeHtml(mark.examType || "--"),
            '</td><td>',
            escapeHtml(mark.marksObtained || "--"),
            " / ",
            escapeHtml(mark.maxMarks || "--"),
            '</td><td>',
            escapeHtml(mark.grade || "--"),
            '</td><td>',
            escapeHtml(formatDate(mark.examDate)),
            '</td><td><button class="button-quiet compact-button" type="button" data-mark-edit="',
            escapeHtml(mark.markId),
            '">Edit</button></td></tr>'
        ].join("");
    }).join("");

    target.querySelectorAll("[data-mark-edit]").forEach(function (button) {
        button.addEventListener("click", function () {
            const markId = Number(button.getAttribute("data-mark-edit"));
            const mark = marks.find(function (item) {
                return item.markId === markId;
            });
            openMarkModal(mark);
        });
    });
}

function renderLayout() {
    const scoreRatios = marks.map(function (mark) {
        const obtained = Number(mark.marksObtained || 0);
        const maximum = Number(mark.maxMarks || 0);
        return maximum > 0 ? (obtained / maximum) * 100 : 0;
    });
    const averageScore = scoreRatios.length
        ? Math.round(scoreRatios.reduce(function (sum, score) { return sum + score; }, 0) / scoreRatios.length)
        : 0;
    const aGrades = marks.filter(function (mark) {
        return String(mark.grade || "").toUpperCase().startsWith("A");
    }).length;
    const subjectsById = subjectLookup();
    const topSubjects = Object.entries(marks.reduce(function (accumulator, mark) {
        const key = mark.subjectId;
        accumulator[key] = (accumulator[key] || 0) + 1;
        return accumulator;
    }, {})).sort(function (left, right) {
        return right[1] - left[1];
    }).slice(0, 5);

    pageRoot.innerHTML = [
        '<section class="page-header"><div><span class="section-kicker">Marks</span><h3>Assessment records and grade tracking</h3><p>Manage subject-wise marks, grades, exam metadata, and searchable assessment history in a dedicated module.</p></div><div class="toolbar-actions"><button class="button" type="button" id="add-mark-button">Add Mark</button><a class="button-secondary" href="',
        buildHref("admin/academics.html"),
        '">Academics</a></div></section>',
        '<section class="stats-grid">',
        renderStatCard({ label: "Mark Entries", value: formatNumber(marks.length), note: "Assessment records in the live marks register.", iconName: "award" }),
        renderStatCard({ label: "Average Score", value: averageScore ? averageScore + "%" : "--", note: "Across all visible assessments.", iconName: "chart", accent: "success" }),
        renderStatCard({ label: "Subjects", value: formatNumber(new Set(marks.map(function (mark) { return mark.subjectId; })).size), note: "Subjects represented in the mark feed.", iconName: "book", accent: "info" }),
        renderStatCard({ label: "A Grades", value: formatNumber(aGrades), note: "Entries with grade A or above labels.", iconName: "dashboard", accent: "warning" }),
        '</section><section class="panel-grid"><article class="page-panel"><span class="section-kicker">Top subjects</span><h4 class="page-panel-title">Assessment volume by subject</h4><div class="list-stack">',
        (topSubjects.length ? topSubjects.map(function (entry) {
            return renderListCard({
                title: subjectsById.get(Number(entry[0])) || ("Subject " + entry[0]),
                description: formatNumber(entry[1]) + " assessments recorded for this subject.",
                status: "Active",
                iconName: "book"
            });
        }).join("") : renderEmptyState("Subject insights will appear once marks are recorded.")),
        '</div></article><article class="page-panel"><span class="section-kicker">Recent assessments</span><h4 class="page-panel-title">Latest marks added</h4><div class="list-stack">',
        (marks.length ? sortByDateDesc(marks, "examDate").slice(0, 5).map(function (mark) {
            return renderListCard({
                title: subjectsById.get(mark.subjectId) || ("Subject " + mark.subjectId),
                description: "Score " + mark.marksObtained + "/" + mark.maxMarks + " with grade " + (mark.grade || "--") + ".",
                meta: formatDate(mark.examDate),
                status: mark.examType,
                iconName: "award"
            });
        }).join("") : renderEmptyState("Recent assessments appear here once the marks register is active.")),
        '</div></article></section><section class="page-panel filter-panel"><div class="toolbar"><div><span class="section-kicker">Filters</span><h4 class="page-panel-title">Assessment controls</h4></div><span class="tag">Student, subject, exam</span></div><div class="field-grid two"><div class="field"><label for="mark-search">Search</label><input id="mark-search" type="search" placeholder="Search by student, subject, exam, grade, or ID"></div><div class="field"><label for="mark-subject-filter">Subject</label><select id="mark-subject-filter"><option value="">All subjects</option>',
        subjects.map(function (subject) {
            return '<option value="' + escapeHtml(subject.subjectId) + '">' + escapeHtml(subjectName(subject)) + "</option>";
        }).join(""),
        '</select></div><div class="field span-2"><label for="mark-exam-filter">Exam Type</label><input id="mark-exam-filter" type="search" placeholder="Filter by exam type"></div></div></section>',
        '<section class="page-panel scroll"><div class="toolbar"><div><span class="section-kicker">Marks register</span><h4 class="page-panel-title">Assessment table</h4></div><span class="tag">',
        escapeHtml(formatNumber(marks.length)),
        ' entries</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Student</th><th>Subject</th><th>Exam</th><th>Score</th><th>Grade</th><th>Date</th><th>Action</th></tr></thead><tbody id="marks-table"></tbody></table></div></section>'
    ].join("");

    document.getElementById("add-mark-button").addEventListener("click", function () {
        openMarkModal();
    });

    const quickAction = document.querySelector('[data-quick-action="create-mark"]');
    if (quickAction) {
        quickAction.addEventListener("click", function () {
            openMarkModal();
        });
    }

    document.getElementById("mark-search").addEventListener("input", applyFilters);
    document.getElementById("mark-subject-filter").addEventListener("change", applyFilters);
    document.getElementById("mark-exam-filter").addEventListener("input", applyFilters);
    applyFilters();
}

async function loadPageData() {
    const [markRecords, studentRecords, subjectRecords] = await Promise.all([
        apiRequest("/api/marks"),
        apiRequest("/api/students"),
        apiRequest("/api/subjects")
    ]);

    marks = asArray(markRecords);
    students = asArray(studentRecords);
    subjects = asArray(subjectRecords);
    renderLayout();

    updateShellNotifications([
        {
            title: "Marks register loaded",
            description: formatNumber(marks.length) + " mark entries are available for review."
        },
        {
            title: "Live assessment forms",
            description: "Use Add Mark or Edit to update the subject-wise assessment register."
        },
        {
            title: "Academic linkage",
            description: "Marks are mapped to live student and subject records."
        }
    ]);

    registerAssistantContext({
        pageTitle: "marks management",
        summary: [
            "This module contains " + formatNumber(marks.length) + " assessment records.",
            "The marks form is wired to live student and subject data for consistent entry.",
            "Top subjects and recent assessments surface the busiest academic areas."
        ],
        suggestions: [
            "Summarize marks",
            "What is the average score?",
            "How many A grades are there?",
            "How do I add a mark entry?"
        ],
        metrics: {
            marks: formatNumber(marks.length) + " mark entries",
            marksNote: "Use the subject and exam filters to narrow the register."
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
        currentKey: "marks",
        workspaceLabel: "Assessments",
        brandTitle: "Marks Register",
        brandCopy: "Reusable CRUD for assessment scores, grades, and subject-linked results.",
        title: "Marks",
        subtitle: "Subject-wise assessment history with searchable live updates",
        searchPlaceholder: "Search marks, grades, or subjects",
        quickActions: [
            { label: "Add Mark", action: "create-mark", iconName: "plus", variant: "button" },
            { label: "Academics", href: buildHref("admin/academics.html"), iconName: "book", variant: "button-secondary" }
        ],
        notifications: [
            { title: "Loading marks", description: "Fetching assessments, students, and subject references." }
        ]
    });

    pageRoot.innerHTML = '<div class="loading-state">Loading marks...</div>';

    try {
        await loadPageData();
    } catch (error) {
        pageRoot.innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
