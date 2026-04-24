import { buildHref, escapeHtml, getRoleName, logout } from "../core.js";
import { icon } from "./icons.js";
import { mountAssistant } from "./chatbot.js";

const SIDEBAR_KEY = "cms_ui_sidebar_collapsed_v1";

function buildNav(role) {
    const normalized = String(role || "").toUpperCase();

    if (normalized === "ADMIN" || normalized === "STAFF") {
        return [
            {
                label: "Core",
                items: [
                    { key: "dashboard", label: "Dashboard", href: buildHref("admin/dashboard.html"), iconName: "dashboard" },
                    { key: "students", label: "Students", href: buildHref("admin/students.html"), iconName: "users" },
                    { key: "academics", label: "Courses & Subjects", href: buildHref("admin/academics.html"), iconName: "book" },
                    { key: "attendance", label: "Attendance", href: buildHref("admin/attendance.html"), iconName: "calendar" },
                    { key: "fees", label: "Fees", href: buildHref("admin/fees.html"), iconName: "wallet" },
                    { key: "marks", label: "Marks", href: buildHref("admin/marks.html"), iconName: "award" }
                ]
            },
            {
                label: "Communication",
                items: [
                    { key: "meetings", label: "Meetings", href: buildHref("meetings.html"), iconName: "video" },
                    { key: "chat", label: "Chat", href: buildHref("chat.html"), iconName: "message" }
                ]
            }
        ];
    }

    if (normalized === "TEACHER") {
        return [
            {
                label: "Workspace",
                items: [
                    { key: "teacher", label: "Dashboard", href: buildHref("teacher/workspace.html"), iconName: "dashboard" },
                    { key: "meetings", label: "Meetings", href: buildHref("meetings.html"), iconName: "video" },
                    { key: "chat", label: "Chat", href: buildHref("chat.html"), iconName: "message" }
                ]
            }
        ];
    }

    return [
        {
            label: "Workspace",
            items: [
                { key: "student", label: "Dashboard", href: buildHref("student/portal.html"), iconName: "dashboard" },
                { key: "meetings", label: "Meetings", href: buildHref("meetings.html"), iconName: "video" },
                { key: "chat", label: "Chat", href: buildHref("chat.html"), iconName: "message" }
            ]
        }
    ];
}

function renderNav(groups, currentKey) {
    return groups.map(function (group) {
        return [
            '<nav class="nav-group"><span class="nav-label">',
            escapeHtml(group.label),
            "</span>",
            group.items.map(function (item) {
                const activeClass = item.key === currentKey ? " active" : "";
                return '<a class="nav-link' + activeClass + '" href="' + escapeHtml(item.href) + '"><span class="nav-link-icon">' + icon(item.iconName) + "</span><span>" + escapeHtml(item.label) + "</span></a>";
            }).join(""),
            "</nav>"
        ].join("");
    }).join("");
}

function renderQuickActions(actions) {
    return (actions || []).map(function (action) {
        if (action.href) {
            return '<a class="' + escapeHtml(action.variant || "button-secondary") + '" href="' + escapeHtml(action.href) + '">' + (action.iconName ? '<span class="button-icon">' + icon(action.iconName) + "</span>" : "") + "<span>" + escapeHtml(action.label) + "</span></a>";
        }

        return '<button class="' + escapeHtml(action.variant || "button-secondary") + '" type="button" data-quick-action="' + escapeHtml(action.action || "") + '">' + (action.iconName ? '<span class="button-icon">' + icon(action.iconName) + "</span>" : "") + "<span>" + escapeHtml(action.label) + "</span></button>";
    }).join("");
}

function renderNotifications(notifications) {
    const items = notifications && notifications.length ? notifications : [{
        title: "Workspace ready",
        description: "Your dashboard shell, quick actions, and assistant are ready.",
        tone: "info"
    }];

    return items.map(function (item) {
        return '<article class="notification-item"><strong>' + escapeHtml(item.title) + '</strong><p>' + escapeHtml(item.description) + "</p></article>";
    }).join("");
}

export function updateShellNotifications(notifications) {
    const list = document.getElementById("notification-list");
    const badge = document.getElementById("notification-count");
    if (list) {
        list.innerHTML = renderNotifications(notifications);
    }
    if (badge) {
        badge.textContent = String((notifications || []).length);
    }
}

export function mountAppShell(options) {
    const {
        session,
        currentKey,
        workspaceLabel,
        brandTitle,
        brandCopy,
        title,
        subtitle,
        searchPlaceholder = "Search",
        quickActions = [],
        notifications = []
    } = options;

    const nav = buildNav(session.role);
    const collapsed = localStorage.getItem(SIDEBAR_KEY) === "true";
    document.body.className = "app-page";
    document.body.classList.toggle("sidebar-collapsed", collapsed);
    document.title = title;
    document.body.innerHTML = [
        '<div class="app-shell"><aside class="sidebar"><div class="sidebar-brand"><div class="sidebar-brand-copy"><span class="role-chip">',
        escapeHtml(workspaceLabel || getRoleName(session.role) + " Workspace"),
        '</span><h1>',
        escapeHtml(brandTitle),
        '</h1><p>',
        escapeHtml(brandCopy),
        '</p></div><button class="icon-button collapse-button" type="button" id="sidebar-collapse" aria-label="Collapse sidebar">',
        icon("chevron"),
        '</button></div>',
        renderNav(nav, currentKey),
        '<div class="sidebar-footer"><a class="nav-link" href="',
        escapeHtml(buildHref("index.html")),
        '"><span class="nav-link-icon">',
        icon("home"),
        '</span><span>Entry Screen</span></a><div class="sidebar-note">Modular components are shared across this workspace: sidebar, navbar, cards, tables, forms, modal, meeting room, chat, and assistant.</div></div></aside><div class="app-content"><header class="topbar"><div class="topbar-left"><button class="icon-button mobile-only" type="button" id="sidebar-toggle" aria-label="Toggle menu">',
        icon("menu"),
        '</button><div class="topbar-title"><span class="section-kicker">',
        escapeHtml(workspaceLabel || getRoleName(session.role)),
        '</span><h2>',
        escapeHtml(title),
        '</h2><p class="muted">',
        escapeHtml(subtitle),
        '</p></div></div><div class="topbar-actions"><div class="search-wrap"><span class="search-icon">',
        icon("search"),
        '</span><input class="search-input" id="global-search" type="search" placeholder="',
        escapeHtml(searchPlaceholder),
        '"></div><div class="quick-actions">',
        renderQuickActions(quickActions),
        '</div><div class="topbar-menu"><button class="icon-button notification-button" type="button" id="notification-toggle" aria-label="Open notifications">',
        icon("bell"),
        '<span class="notification-badge" id="notification-count">',
        escapeHtml((notifications || []).length),
        '</span></button><div class="dropdown" id="notification-dropdown"><div class="dropdown-head"><strong>Notifications</strong></div><div class="notification-list" id="notification-list">',
        renderNotifications(notifications),
        '</div></div></div><div class="topbar-user"><span class="avatar">',
        escapeHtml((session.username || "U").charAt(0).toUpperCase()),
        '</span><div><strong>',
        escapeHtml(session.displayName || session.username || session.email || "User"),
        "</strong><span>",
        escapeHtml(getRoleName(session.role)),
        '</span></div></div><button class="icon-button" type="button" id="logout-action" aria-label="Log out">',
        icon("logout"),
        '</button></div></header><main class="content-wrap" id="page-root"></main></div></div><div id="modal-root"></div><div id="assistant-root"></div>'
    ].join("");

    const dropdown = document.getElementById("notification-dropdown");
    document.getElementById("logout-action").addEventListener("click", logout);
    document.getElementById("notification-toggle").addEventListener("click", function () {
        dropdown.classList.toggle("open");
    });
    document.getElementById("sidebar-toggle").addEventListener("click", function () {
        document.body.classList.toggle("sidebar-open");
    });
    document.getElementById("sidebar-collapse").addEventListener("click", function () {
        const nextState = !document.body.classList.contains("sidebar-collapsed");
        document.body.classList.toggle("sidebar-collapsed", nextState);
        localStorage.setItem(SIDEBAR_KEY, String(nextState));
    });

    document.addEventListener("click", function (event) {
        const insideMenu = event.target.closest(".topbar-menu");
        if (!insideMenu) {
            dropdown.classList.remove("open");
        }
    });

    mountAssistant(session);
    return document.getElementById("page-root");
}
