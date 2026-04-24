import {
    apiRequest,
    asArray,
    buildHref,
    escapeHtml,
    formatCurrency,
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
let fees = [];
let students = [];
let filteredFees = [];

function studentName(student) {
    return [student?.firstName, student?.lastName].filter(Boolean).join(" ") || "Student";
}

function studentLookup() {
    return new Map(students.map(function (student) {
        return [student.studentId, studentName(student)];
    }));
}

function normalizePayload(values) {
    return {
        studentId: values.studentId ? Number(values.studentId) : null,
        amount: values.amount ? Number(values.amount) : null,
        status: values.status || null,
        dueDate: values.dueDate || null
    };
}

function isPending(fee) {
    return String(fee.status || "").toLowerCase() === "pending";
}

function isOverdue(fee) {
    if (!isPending(fee) || !fee.dueDate) {
        return false;
    }
    return new Date(fee.dueDate) < new Date(new Date().toISOString().slice(0, 10));
}

function openFeeModal(fee = null) {
    openModal({
        title: fee ? "Edit Fee Record" : "Add Fee Record",
        description: fee
            ? "Update payment status, due date, or amount for the selected student."
            : "Create a fee entry and assign it to the right student profile.",
        body: [
            '<form id="fee-form" class="field-grid">',
            renderFormGrid([
                { name: "studentId", label: "Student", type: "select", value: fee?.studentId || "", required: true, options: [{ value: "", label: "Select student" }].concat(students.map(function (student) { return { value: student.studentId, label: studentName(student) + " (" + student.studentId + ")" }; })) },
                { name: "amount", label: "Amount", type: "number", value: fee?.amount || "", required: true, min: "0", step: "0.01" },
                { name: "status", label: "Status", type: "select", value: fee?.status || "", required: true, options: [{ value: "", label: "Select status" }, "Pending", "Paid"] },
                { name: "dueDate", label: "Due Date", type: "date", value: fee?.dueDate || "", required: true }
            ]),
            '<div id="fee-form-status" class="status-banner info compact">Save to update the live fee ledger.</div>',
            '<div class="button-row"><button class="button" type="submit">',
            fee ? "Save Fee" : "Create Fee",
            '</button><button class="button-quiet" type="button" id="cancel-fee-form">Cancel</button></div></form>'
        ].join(""),
        onOpen: function () {
            document.getElementById("cancel-fee-form").addEventListener("click", closeModal);
            document.getElementById("fee-form").addEventListener("submit", async function (event) {
                event.preventDefault();
                const status = document.getElementById("fee-form-status");
                status.textContent = "Saving fee record...";
                status.className = "status-banner info compact";

                try {
                    const payload = normalizePayload(serializeForm(event.currentTarget));
                    await apiRequest(fee ? "/api/fees/" + fee.feeId : "/api/fees", {
                        method: fee ? "PUT" : "POST",
                        body: payload
                    });
                    status.textContent = "Fee saved.";
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

async function markPaid(fee) {
    await apiRequest("/api/fees/" + fee.feeId, {
        method: "PUT",
        body: {
            studentId: fee.studentId,
            amount: fee.amount,
            status: "Paid",
            dueDate: fee.dueDate
        }
    });
    await loadPageData();
}

function applyFilters() {
    const search = document.getElementById("fee-search").value.trim().toLowerCase();
    const statusFilter = document.getElementById("fee-status-filter").value;
    const names = studentLookup();

    filteredFees = fees.filter(function (fee) {
        const matchesStatus = !statusFilter || String(fee.status || "").toLowerCase() === statusFilter.toLowerCase();
        const haystack = [names.get(fee.studentId), fee.studentId, fee.amount, fee.status, fee.dueDate].join(" ").toLowerCase();
        const matchesSearch = !search || haystack.includes(search);
        return matchesStatus && matchesSearch;
    });

    renderFeeTable();
}

function renderFeeTable() {
    const target = document.getElementById("fees-table");
    const names = studentLookup();

    if (!filteredFees.length) {
        target.innerHTML = '<tr><td colspan="6">' + renderEmptyState("No fee records match the current filters.") + "</td></tr>";
        return;
    }

    target.innerHTML = filteredFees.map(function (fee) {
        return [
            "<tr><td>",
            escapeHtml(names.get(fee.studentId) || ("Student " + fee.studentId)),
            '</td><td>',
            escapeHtml(formatCurrency(fee.amount)),
            '</td><td>',
            escapeHtml(formatDate(fee.dueDate)),
            '</td><td>',
            renderStatusBadge(isOverdue(fee) ? "Overdue" : fee.status),
            '</td><td>',
            isOverdue(fee) ? '<span class="tag">Follow up</span>' : '<span class="tag">On track</span>',
            '</td><td><div class="button-row">',
            isPending(fee) ? '<button class="button-secondary compact-button" type="button" data-fee-paid="' + escapeHtml(fee.feeId) + '">Mark Paid</button>' : "",
            '<button class="button-quiet compact-button" type="button" data-fee-edit="' + escapeHtml(fee.feeId) + '">Edit</button>',
            "</div></td></tr>"
        ].join("");
    }).join("");

    target.querySelectorAll("[data-fee-edit]").forEach(function (button) {
        button.addEventListener("click", function () {
            const feeId = Number(button.getAttribute("data-fee-edit"));
            const fee = fees.find(function (item) {
                return item.feeId === feeId;
            });
            openFeeModal(fee);
        });
    });

    target.querySelectorAll("[data-fee-paid]").forEach(function (button) {
        button.addEventListener("click", async function () {
            const feeId = Number(button.getAttribute("data-fee-paid"));
            const fee = fees.find(function (item) {
                return item.feeId === feeId;
            });
            if (fee) {
                await markPaid(fee);
            }
        });
    });
}

function renderLayout(summary) {
    const paidCount = fees.filter(function (fee) { return String(fee.status || "").toLowerCase() === "paid"; }).length;
    const overdueFees = fees.filter(isOverdue);
    const names = studentLookup();

    pageRoot.innerHTML = [
        '<section class="page-header"><div><span class="section-kicker">Fees</span><h3>Finance ledger and payment tracking</h3><p>Track due dates, payment status, overdue exposure, and fee operations from one SaaS-style module.</p></div><div class="toolbar-actions"><button class="button" type="button" id="add-fee-button">Add Fee</button><a class="button-secondary" href="',
        buildHref("admin/students.html"),
        '">Student Center</a></div></section>',
        '<section class="stats-grid">',
        renderStatCard({ label: "Paid Amount", value: formatCurrency(summary.paidAmount), note: formatNumber(summary.paidCount) + " records cleared.", iconName: "wallet", accent: "success" }),
        renderStatCard({ label: "Pending Amount", value: formatCurrency(summary.pendingAmount), note: formatNumber(summary.pendingCount) + " records still open.", iconName: "wallet", accent: "warning" }),
        renderStatCard({ label: "Paid Count", value: formatNumber(paidCount), note: "Fee records marked paid in the ledger.", iconName: "dashboard", accent: "info" }),
        renderStatCard({ label: "Overdue", value: formatNumber(overdueFees.length), note: "Pending items with due dates already passed.", iconName: "calendar", accent: "danger" }),
        '</section><section class="panel-grid"><article class="page-panel"><span class="section-kicker">Overdue watchlist</span><h4 class="page-panel-title">Follow-up items</h4><div class="list-stack">',
        (overdueFees.length ? overdueFees.slice(0, 5).map(function (fee) {
            return renderListCard({
                title: names.get(fee.studentId) || ("Student " + fee.studentId),
                description: "Pending fee of " + formatCurrency(fee.amount) + " requires follow-up.",
                meta: "Due " + formatDate(fee.dueDate),
                status: "Overdue",
                iconName: "wallet"
            });
        }).join("") : renderEmptyState("No overdue fee records are visible right now.")),
        '</div></article><article class="page-panel"><span class="section-kicker">Recent fee activity</span><h4 class="page-panel-title">Latest ledger entries</h4><div class="list-stack">',
        (fees.length ? sortByDateDesc(fees, "dueDate").slice(0, 5).map(function (fee) {
            return renderListCard({
                title: names.get(fee.studentId) || ("Student " + fee.studentId),
                description: "Amount " + formatCurrency(fee.amount) + " with status " + (fee.status || "--") + ".",
                meta: "Due " + formatDate(fee.dueDate),
                status: fee.status,
                iconName: "wallet"
            });
        }).join("") : renderEmptyState("Fee activity appears here once records are available.")),
        '</div></article></section><section class="page-panel filter-panel"><div class="toolbar"><div><span class="section-kicker">Filters</span><h4 class="page-panel-title">Ledger controls</h4></div><span class="tag">Search + status</span></div><div class="field-grid two"><div class="field"><label for="fee-search">Search</label><input id="fee-search" type="search" placeholder="Search student name, ID, amount, or due date"></div><div class="field"><label for="fee-status-filter">Status</label><select id="fee-status-filter"><option value="">All statuses</option><option value="Pending">Pending</option><option value="Paid">Paid</option></select></div></div></section>',
        '<section class="page-panel scroll"><div class="toolbar"><div><span class="section-kicker">Fee records</span><h4 class="page-panel-title">Ledger table</h4></div><span class="tag">',
        escapeHtml(formatNumber(fees.length)),
        ' records</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Student</th><th>Amount</th><th>Due Date</th><th>Status</th><th>Risk</th><th>Action</th></tr></thead><tbody id="fees-table"></tbody></table></div></section>'
    ].join("");

    document.getElementById("add-fee-button").addEventListener("click", function () {
        openFeeModal();
    });

    const quickAction = document.querySelector('[data-quick-action="create-fee"]');
    if (quickAction) {
        quickAction.addEventListener("click", function () {
            openFeeModal();
        });
    }

    document.getElementById("fee-search").addEventListener("input", applyFilters);
    document.getElementById("fee-status-filter").addEventListener("change", applyFilters);
    applyFilters();
}

async function loadPageData() {
    const [feeRecords, studentRecords, summary] = await Promise.all([
        apiRequest("/api/fees"),
        apiRequest("/api/students"),
        apiRequest("/api/reports/fees/summary")
    ]);

    fees = asArray(feeRecords);
    students = asArray(studentRecords);
    renderLayout(summary);

    updateShellNotifications([
        {
            title: "Fee ledger loaded",
            description: formatNumber(fees.length) + " fee records are available in the live module."
        },
        {
            title: "Pending exposure",
            description: formatCurrency(summary.pendingAmount) + " remains pending across " + formatNumber(summary.pendingCount) + " records."
        },
        {
            title: "Fast actions ready",
            description: "Use Add Fee or Mark Paid to update ledger state quickly."
        }
    ]);

    registerAssistantContext({
        pageTitle: "fee management",
        summary: [
            "The fee ledger contains " + formatNumber(fees.length) + " records.",
            "Pending fees total " + formatCurrency(summary.pendingAmount) + " across " + formatNumber(summary.pendingCount) + " records.",
            "The overdue watchlist highlights pending items whose due dates have passed."
        ],
        suggestions: [
            "Summarize fees",
            "How much is pending?",
            "How many overdue fees are there?",
            "How do I add a fee?"
        ],
        metrics: {
            pendingFees: formatCurrency(summary.pendingAmount),
            pendingFeeNote: formatNumber(summary.pendingCount) + " fee records are currently pending."
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
        currentKey: "fees",
        workspaceLabel: "Finance",
        brandTitle: "Fee Ledger",
        brandCopy: "Reusable finance tables and forms for fee collection, pending balances, and due-date operations.",
        title: "Fees",
        subtitle: "Summary cards, overdue watchlists, and real payment-status updates",
        searchPlaceholder: "Search fee records or student dues",
        quickActions: [
            { label: "Add Fee", action: "create-fee", iconName: "plus", variant: "button" },
            { label: "Students", href: buildHref("admin/students.html"), iconName: "users", variant: "button-secondary" }
        ],
        notifications: [
            { title: "Loading fees", description: "Fetching fee records, students, and payment summary." }
        ]
    });

    pageRoot.innerHTML = '<div class="loading-state">Loading fees...</div>';

    try {
        await loadPageData();
    } catch (error) {
        pageRoot.innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
