import { escapeHtml, formatDateTime, renderEmptyState, renderStatusBadge } from "../core.js";
import { renderChatThread } from "./chatbox.js";
import { icon } from "./icons.js";

function escapeAttr(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function buildFrameDoc(meeting) {
    const title = escapeHtml(meeting?.title || "Meeting room preview");
    const course = escapeHtml(meeting?.courseCode || meeting?.audienceType || "Open room");
    const provider = escapeHtml(meeting?.provider || "Integrated provider");
    const start = escapeHtml(formatDateTime(meeting?.scheduledStartAt));

    return [
        "<!doctype html><html><head><meta charset=\"utf-8\"><style>",
        "body{margin:0;background:#09111b;color:#edf4ff;font-family:Segoe UI,Arial,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;}",
        ".frame{width:min(92%,640px);padding:28px;border:1px solid #233146;border-radius:18px;background:linear-gradient(180deg,#101826,#0d1523);box-shadow:0 24px 60px rgba(0,0,0,.28);}",
        ".eyebrow{display:inline-flex;padding:6px 10px;border-radius:999px;background:rgba(119,168,255,.16);color:#77a8ff;font-size:12px;font-weight:600;}",
        "h1{margin:16px 0 8px;font-size:28px;line-height:1.1;}p{margin:0 0 8px;color:#92a4bc;}strong{color:#edf4ff;}",
        "</style></head><body><div class=\"frame\"><span class=\"eyebrow\">Meeting Room</span><h1>",
        title,
        "</h1><p><strong>Provider:</strong> ",
        provider,
        "</p><p><strong>Audience:</strong> ",
        course,
        "</p><p><strong>Scheduled:</strong> ",
        start,
        "</p><p>This iframe is the in-product room surface. Use the provider action to open the live external session.</p></div></body></html>"
    ].join("");
}

export function renderMeetingRoom(options) {
    const {
        meeting,
        messages = [],
        currentUsername = ""
    } = options;

    if (!meeting) {
        return renderEmptyState("Choose a meeting to open its room, participants, and chat.");
    }

    const participants = meeting.participants || [];
    const frameDoc = escapeAttr(buildFrameDoc(meeting));
    const participantMarkup = participants.length ? participants.map(function (participant) {
        return '<div class="participant-chip"><strong>' + escapeHtml(participant.displayName || participant.username || "Participant") + '</strong><span>' + escapeHtml(participant.role || "--") + "</span></div>";
    }).join("") : renderEmptyState("No participants have joined yet.");

    return [
        '<section class="meeting-room-shell"><header class="meeting-detail-head"><div><span class="section-kicker">Meeting room</span><h3>',
        escapeHtml(meeting.title || "Untitled meeting"),
        '</h3><p class="muted">',
        escapeHtml(meeting.description || "Open the provider room or use the embedded preview."),
        "</p></div>",
        renderStatusBadge(meeting.status),
        "</header>",
        '<div class="mini-grid">',
        '<article class="mini-card elevated"><div class="mini-card-head"><span class="mini-icon">',
        icon("video"),
        '</span></div><h4>Provider</h4><p class="strong">',
        escapeHtml(meeting.provider || "--"),
        '</p><p class="muted">Primary room connection</p></article>',
        '<article class="mini-card elevated"><div class="mini-card-head"><span class="mini-icon">',
        icon("calendar"),
        '</span></div><h4>Start Time</h4><p class="strong">',
        escapeHtml(formatDateTime(meeting.scheduledStartAt)),
        '</p><p class="muted">Scheduled session start</p></article>',
        '<article class="mini-card elevated"><div class="mini-card-head"><span class="mini-icon">',
        icon("users"),
        '</span></div><h4>Audience</h4><p class="strong">',
        escapeHtml(meeting.courseCode || meeting.audienceType || "Open"),
        '</p><p class="muted">Visible participants</p></article>',
        '<article class="mini-card elevated"><div class="mini-card-head"><span class="mini-icon">',
        icon("home"),
        '</span></div><h4>Host</h4><p class="strong">',
        escapeHtml(meeting.hostUsername || "--"),
        '</p><p class="muted">Room owner</p></article>',
        "</div>",
        '<div class="meeting-stage"><div class="meeting-embed"><div class="toolbar"><div><span class="section-kicker">Room surface</span><h4 class="page-panel-title">Embedded meeting preview</h4></div><div class="toolbar-actions" id="meeting-actions"></div></div><iframe class="meeting-frame" title="Meeting room preview" srcdoc="',
        frameDoc,
        '"></iframe></div><aside class="page-panel participants-panel"><span class="section-kicker">Participants</span><h4 class="page-panel-title">Live roster</h4><div id="meeting-participants" class="participants-stack">',
        participantMarkup,
        "</div></aside></div>",
        renderChatThread({
            title: "Meeting chat",
            meta: "Messages in this room are shared with everyone who can access the meeting.",
            messages,
            currentUsername
        }),
        "</section>"
    ].join("");
}
