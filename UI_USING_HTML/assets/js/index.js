import {
    byId,
    getSession,
    getStoredApiBase,
    login,
    logout,
    getRoleHomeHref,
    escapeHtml
} from "./core.js";

const SAMPLE_USERS = [
    { username: "admin", password: "admin123", role: "Admin" },
    { username: "rajesh", password: "teacher123", role: "Teacher" },
    { username: "rohit", password: "student123", role: "Student" },
    { username: "anjali", password: "student123", role: "Student" }
];

function renderSampleUsers() {
    const container = byId("sample-users");
    if (!container) {
        return;
    }

    container.innerHTML = SAMPLE_USERS.map(function (account) {
        return [
            '<button class="credential-card" type="button" data-username="',
            escapeHtml(account.username),
            '" data-password="',
            escapeHtml(account.password),
            '"><strong>',
            escapeHtml(account.role),
            "</strong><span>",
            escapeHtml(account.username),
            " / ",
            escapeHtml(account.password),
            "</span></button>"
        ].join("");
    }).join("");

    container.querySelectorAll(".credential-card").forEach(function (button) {
        button.addEventListener("click", function () {
            byId("username").value = button.getAttribute("data-username") || "";
            byId("password").value = button.getAttribute("data-password") || "";
        });
    });
}

function renderSessionBanner() {
    const banner = byId("active-session");
    const session = getSession();
    if (!banner || !session?.token) {
        return;
    }

    banner.innerHTML = [
        '<div class="notice-strip">',
        '<div><strong>Active session</strong><span class="muted">',
        escapeHtml(session.username),
        " is signed in as ",
        escapeHtml(session.role),
        " against ",
        escapeHtml(getStoredApiBase()),
        "</span></div>",
        '<div class="button-row">',
        '<a class="button-secondary" href="',
        getRoleHomeHref(session.role),
        '">Continue</a>',
        '<button class="button-quiet" type="button" id="clear-session">Log Out</button>',
        "</div></div>"
    ].join("");

    const clearButton = byId("clear-session");
    if (clearButton) {
        clearButton.addEventListener("click", function () {
            logout();
        });
    }
}

async function handleSubmit(event) {
    event.preventDefault();
    const status = byId("login-status");
    const username = byId("username").value.trim();
    const password = byId("password").value.trim();
    const apiBase = byId("api-base").value.trim();

    if (!username || !password) {
        status.textContent = "Enter a username and password first.";
        status.className = "status-banner error";
        return;
    }

    status.textContent = "Signing in...";
    status.className = "status-banner info";

    try {
        const session = await login(username, password, apiBase);
        status.textContent = "Login successful. Opening your workspace...";
        status.className = "status-banner success";
        window.location.href = getRoleHomeHref(session.role);
    } catch (error) {
        status.textContent = error.message;
        status.className = "status-banner error";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    byId("api-base").value = getStoredApiBase();
    renderSampleUsers();
    renderSessionBanner();
    byId("login-form").addEventListener("submit", handleSubmit);
});
