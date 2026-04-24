const SESSION_KEY = "cms_ui_session_v2";
const API_BASE_KEY = "cms_ui_api_base_v2";
const DEFAULT_API_BASE = "http://localhost:8000";

export function byId(id) {
    return document.getElementById(id);
}

export function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

export function normalizeApiBase(value) {
    const normalized = String(value || DEFAULT_API_BASE).trim();
    return normalized.endsWith("/") ? normalized.slice(0, -1) : normalized;
}

export function getStoredApiBase() {
    return normalizeApiBase(localStorage.getItem(API_BASE_KEY) || DEFAULT_API_BASE);
}

export function setStoredApiBase(value) {
    const normalized = normalizeApiBase(value);
    localStorage.setItem(API_BASE_KEY, normalized);
    return normalized;
}

export function getSession() {
    try {
        const raw = localStorage.getItem(SESSION_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (_) {
        return null;
    }
}

export function saveSession(session) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
    localStorage.removeItem(SESSION_KEY);
}

export function getRoleName(role) {
    const normalized = String(role || "").trim().toUpperCase();
    if (normalized === "ADMIN") {
        return "Admin";
    }
    if (normalized === "STAFF") {
        return "Staff";
    }
    if (normalized === "TEACHER") {
        return "Teacher";
    }
    if (normalized === "STUDENT") {
        return "Student";
    }
    return "User";
}

export function getPathPrefix() {
    return /\/(admin|teacher|student)\//.test(window.location.pathname) ? "../" : "./";
}

export function getRoleHomeHref(role) {
    const prefix = getPathPrefix();
    const normalized = String(role || "").trim().toUpperCase();
    if (normalized === "ADMIN" || normalized === "STAFF") {
        return prefix + "admin/dashboard.html";
    }
    if (normalized === "TEACHER") {
        return prefix + "teacher/workspace.html";
    }
    if (normalized === "STUDENT") {
        return prefix + "student/portal.html";
    }
    return prefix + "index.html";
}

export function getMeetingsHref(meetingId = null) {
    const prefix = getPathPrefix();
    if (!meetingId) {
        return prefix + "meetings.html";
    }
    return prefix + "meetings.html?meetingId=" + encodeURIComponent(meetingId);
}

export function redirectToIndex() {
    window.location.href = getPathPrefix() + "index.html";
}

export function logout() {
    clearSession();
    redirectToIndex();
}

export function attachLogoutHandlers() {
    document.querySelectorAll("[data-logout]").forEach(function (button) {
        button.addEventListener("click", function () {
            logout();
        });
    });
}

function getAuthHeaders(headers = {}, auth = true) {
    const finalHeaders = { Accept: "application/json", ...headers };
    if (auth) {
        const session = getSession();
        if (session?.token) {
            finalHeaders.Authorization = "Bearer " + session.token;
        }
    }
    return finalHeaders;
}

export async function apiRequest(path, options = {}) {
    const {
        method = "GET",
        body = undefined,
        auth = true,
        headers = {}
    } = options;

    const requestHeaders = getAuthHeaders(headers, auth);
    const requestOptions = {
        method,
        headers: requestHeaders
    };

    if (body !== undefined) {
        requestHeaders["Content-Type"] = "application/json";
        requestOptions.body = JSON.stringify(body);
    }

    const response = await fetch(getStoredApiBase() + path, requestOptions);
    const contentType = response.headers.get("content-type") || "";
    let payload = null;

    if (contentType.includes("application/json")) {
        payload = await response.json();
    } else if (response.status !== 204) {
        payload = await response.text();
    }

    if (!response.ok) {
        const message = payload?.detail || payload?.error || (typeof payload === "string" && payload) || "Request failed";
        if (response.status === 401) {
            clearSession();
        }
        throw new Error(message);
    }

    return payload;
}

export async function login(username, password, apiBase) {
    const normalizedBase = setStoredApiBase(apiBase);
    const payload = await apiRequest("/api/auth/login", {
        method: "POST",
        auth: false,
        body: { username, password }
    });
    const session = { ...payload, apiBase: normalizedBase };
    saveSession(session);
    return session;
}

export function requireSession(allowedRoles = []) {
    const session = getSession();
    if (!session?.token) {
        redirectToIndex();
        return null;
    }

    if (allowedRoles.length > 0) {
        const currentRole = String(session.role || "").trim().toUpperCase();
        const allowed = allowedRoles.map(function (role) {
            return String(role).trim().toUpperCase();
        });

        if (!allowed.includes(currentRole)) {
            window.location.href = getRoleHomeHref(session.role);
            return null;
        }
    }

    return session;
}

export function hydrateShell(session, options = {}) {
    const {
        pageTitle = "",
        pageDescription = ""
    } = options;

    document.querySelectorAll("[data-current-user]").forEach(function (node) {
        node.textContent = session.displayName || session.username || session.email || "Authenticated User";
    });

    document.querySelectorAll("[data-current-role]").forEach(function (node) {
        node.textContent = getRoleName(session.role);
    });

    document.querySelectorAll("[data-api-base]").forEach(function (node) {
        node.textContent = getStoredApiBase();
    });

    document.querySelectorAll("[data-home-link]").forEach(function (node) {
        node.setAttribute("href", getRoleHomeHref(session.role));
    });

    document.querySelectorAll("[data-meetings-link]").forEach(function (node) {
        node.setAttribute("href", getMeetingsHref());
    });

    if (pageTitle) {
        document.title = pageTitle;
    }

    if (pageDescription) {
        document.querySelectorAll("[data-page-description]").forEach(function (node) {
            node.textContent = pageDescription;
        });
    }

    attachLogoutHandlers();
}

export function formatDate(value) {
    if (!value) {
        return "--";
    }
    return new Date(value).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

export function formatDateTime(value) {
    if (!value) {
        return "--";
    }
    return new Date(value).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

export function formatCurrency(value) {
    const parsed = Number(value || 0);
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    }).format(Number.isFinite(parsed) ? parsed : 0);
}

export function computeStatusTone(value) {
    const normalized = String(value || "").trim().toLowerCase();
    if (["paid", "present", "live", "completed", "active", "joined"].some(function (token) { return normalized.includes(token); })) {
        return "success";
    }
    if (["pending", "scheduled", "review", "warning", "clear"].some(function (token) { return normalized.includes(token); })) {
        return "warning";
    }
    if (["ended", "absent", "overdue", "denied", "escalated", "unassigned"].some(function (token) { return normalized.includes(token); })) {
        return "danger";
    }
    return "info";
}

export function renderStatusBadge(label) {
    const safeLabel = escapeHtml(label || "Unknown");
    return '<span class="status-badge ' + computeStatusTone(label) + '">' + safeLabel + "</span>";
}

export function renderEmptyState(message) {
    return '<div class="empty-state"><h4>No data yet</h4><p>' + escapeHtml(message) + "</p></div>";
}

export function renderErrorState(message) {
    return '<div class="empty-state error-state"><h4>Could not load data</h4><p>' + escapeHtml(message) + "</p></div>";
}

export function setLoading(target, label = "Loading data...") {
    if (target) {
        target.innerHTML = '<div class="loading-state">' + escapeHtml(label) + "</div>";
    }
}

export function asArray(value) {
    return Array.isArray(value) ? value : [];
}

export function sortByDateDesc(items, fieldName) {
    return [...asArray(items)].sort(function (left, right) {
        const leftValue = new Date(left?.[fieldName] || 0).getTime();
        const rightValue = new Date(right?.[fieldName] || 0).getTime();
        return rightValue - leftValue;
    });
}

export function toLocalDateTimeInput(value) {
    if (!value) {
        return "";
    }
    const date = new Date(value);
    const pad = function (part) {
        return String(part).padStart(2, "0");
    };
    return date.getFullYear()
        + "-"
        + pad(date.getMonth() + 1)
        + "-"
        + pad(date.getDate())
        + "T"
        + pad(date.getHours())
        + ":"
        + pad(date.getMinutes());
}

export function fromLocalDateTimeInput(value) {
    if (!value) {
        return null;
    }
    return new Date(value).toISOString();
}

export function readQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}
