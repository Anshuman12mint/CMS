import { escapeHtml, renderStatusBadge } from "../core.js";
import { icon } from "./icons.js";

export function renderStatCard(options) {
    const {
        label,
        value,
        note = "",
        iconName = "dashboard",
        accent = "primary",
        meta = ""
    } = options;

    return [
        '<article class="stat-card accent-',
        escapeHtml(accent),
        '"><div class="stat-card-head"><span class="stat-icon">',
        icon(iconName),
        '</span>',
        meta ? '<span class="tag">' + escapeHtml(meta) + "</span>" : "",
        '</div><p class="stat-label">',
        escapeHtml(label),
        '</p><p class="stat-value">',
        escapeHtml(value),
        '</p><p class="stat-note">',
        escapeHtml(note),
        "</p></article>"
    ].join("");
}

export function renderMiniCard(options) {
    const {
        title,
        value,
        note = "",
        status = "",
        iconName = "chart"
    } = options;

    return [
        '<article class="mini-card elevated"><div class="mini-card-head"><span class="mini-icon">',
        icon(iconName),
        "</span>",
        status ? renderStatusBadge(status) : "",
        '</div><h4>',
        escapeHtml(title),
        '</h4><p class="strong">',
        escapeHtml(value),
        '</p><p class="muted">',
        escapeHtml(note),
        "</p></article>"
    ].join("");
}

export function renderListCard(options) {
    const {
        title,
        description = "",
        meta = "",
        status = "",
        actions = "",
        iconName = ""
    } = options;

    return [
        '<article class="list-item">',
        iconName ? '<div class="list-item-icon">' + icon(iconName) + "</div>" : "",
        '<div class="list-item-body"><div class="list-item-header"><h4>',
        escapeHtml(title),
        "</h4>",
        status ? renderStatusBadge(status) : "",
        "</div>",
        meta ? '<span class="meta">' + escapeHtml(meta) + "</span>" : "",
        '<p>',
        escapeHtml(description),
        "</p>",
        actions ? '<div class="meta-row">' + actions + "</div>" : "",
        "</div></article>"
    ].join("");
}

export function renderActivityFeed(items) {
    if (!items.length) {
        return '<div class="empty-state"><h4>No recent activity</h4><p>Fresh updates will appear here when the backend records change.</p></div>';
    }

    return '<div class="activity-feed">' + items.map(function (item) {
        return [
            '<article class="activity-item"><span class="activity-dot"></span><div><div class="list-item-header"><h4>',
            escapeHtml(item.title),
            "</h4>",
            item.status ? renderStatusBadge(item.status) : "",
            "</div>",
            item.meta ? '<span class="meta">' + escapeHtml(item.meta) + "</span>" : "",
            '<p>',
            escapeHtml(item.description || ""),
            "</p></div></article>"
        ].join("");
    }).join("") + "</div>";
}
