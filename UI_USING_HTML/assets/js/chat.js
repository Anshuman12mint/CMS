import {
    apiRequest,
    asArray,
    buildHref,
    escapeHtml,
    formatDateTime,
    formatNumber,
    readQueryParam,
    renderEmptyState,
    renderErrorState,
    requireSession
} from "./core.js";
import { mountAppShell, updateShellNotifications } from "./components/layout.js";
import { renderStatCard } from "./components/card.js";
import { renderConversationList, renderChatThread } from "./components/chatbox.js";
import { registerAssistantContext } from "./components/chatbot.js";

let session = null;
let pageRoot = null;
let meetings = [];
let selectedMeetingId = null;

function bucket(meeting) {
    const status = String(meeting.status || "").toLowerCase();
    if (status.includes("ended") || status.includes("past")) {
        return "Past";
    }
    if (status.includes("live") || status.includes("active") || status.includes("ongoing")) {
        return "Ongoing";
    }
    return "Upcoming";
}

function renderConversationSidebar() {
    const target = document.getElementById("conversation-list-root");
    const search = document.getElementById("conversation-search").value.trim().toLowerCase();
    const visible = meetings.filter(function (meeting) {
        return !search || [meeting.title, meeting.description, meeting.courseCode, meeting.status].join(" ").toLowerCase().includes(search);
    });

    target.innerHTML = renderConversationList({
        items: visible,
        selectedId: selectedMeetingId,
        getId: function (meeting) { return meeting.meetingId; },
        getTitle: function (meeting) { return meeting.title || "Untitled room"; },
        getMeta: function (meeting) { return formatDateTime(meeting.scheduledStartAt); },
        getStatus: function (meeting) { return meeting.status; }
    });

    target.querySelectorAll("[data-conversation-id]").forEach(function (button) {
        button.addEventListener("click", function () {
            selectedMeetingId = Number(button.getAttribute("data-conversation-id"));
            renderConversationSidebar();
            loadThread();
        });
    });
}

async function loadThread() {
    const target = document.getElementById("conversation-thread-root");

    if (!selectedMeetingId) {
        target.innerHTML = renderEmptyState("Select a conversation to open the message thread.");
        return;
    }

    target.innerHTML = '<div class="loading-state">Loading conversation...</div>';

    try {
        const [meeting, messages] = await Promise.all([
            apiRequest("/api/meetings/" + selectedMeetingId),
            apiRequest("/api/meetings/" + selectedMeetingId + "/messages")
        ]);

        target.innerHTML = renderChatThread({
            title: meeting.title || "Untitled room",
            meta: (meeting.courseCode || meeting.audienceType || "Open audience") + " | " + formatDateTime(meeting.scheduledStartAt),
            messages,
            currentUsername: session.username
        });

        const head = target.querySelector(".chat-thread-head");
        head.insertAdjacentHTML("beforeend", '<div class="toolbar-actions">' + (meeting.canJoin ? '<button class="button-secondary compact-button" type="button" id="join-thread-room">Join Room</button>' : "") + '<a class="button-quiet compact-button" href="' + escapeHtml(buildHref("meetings.html?meetingId=" + meeting.meetingId)) + '">Open Meeting</a></div>');

        const joinButton = document.getElementById("join-thread-room");
        if (joinButton) {
            joinButton.addEventListener("click", async function () {
                await apiRequest("/api/meetings/" + meeting.meetingId + "/join", { method: "POST" });
                await refreshData();
                await loadThread();
            });
        }

        const form = document.getElementById("chat-form");
        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            const input = document.getElementById("message-text");
            const status = document.getElementById("chat-status");
            const value = input.value.trim();
            if (!value) {
                return;
            }

            status.textContent = "Sending message...";
            status.className = "status-banner info compact";

            try {
                await apiRequest("/api/meetings/" + meeting.meetingId + "/messages", {
                    method: "POST",
                    body: { messageText: value }
                });
                input.value = "";
                status.textContent = "Message sent.";
                status.className = "status-banner success compact";
                await loadThread();
            } catch (error) {
                status.textContent = error.message;
                status.className = "status-banner error compact";
            }
        });

        updateShellNotifications([
            {
                title: "Chat room active",
                description: (meeting.title || "Untitled room") + " is open in the conversation thread."
            },
            {
                title: "Messages loaded",
                description: formatNumber(messages.length) + " room messages are visible in the current thread."
            },
            {
                title: "Meeting actions",
                description: "Use Join Room or Open Meeting for the full meeting experience."
            }
        ]);
    } catch (error) {
        target.innerHTML = renderErrorState(error.message);
    }
}

async function refreshData() {
    meetings = asArray(await apiRequest("/api/meetings"));
    const queryMeetingId = Number(readQueryParam("meetingId") || 0);
    if (queryMeetingId && meetings.some(function (meeting) { return meeting.meetingId === queryMeetingId; })) {
        selectedMeetingId = queryMeetingId;
    }
    if (!selectedMeetingId && meetings[0]) {
        selectedMeetingId = meetings[0].meetingId;
    }
    renderConversationSidebar();
    renderSummaryCards();
}

function renderSummaryCards() {
    const target = document.getElementById("chat-summary");
    const ongoing = meetings.filter(function (meeting) { return bucket(meeting) === "Ongoing"; });
    const participants = meetings.reduce(function (sum, meeting) {
        return sum + asArray(meeting.participants).length;
    }, 0);

    target.innerHTML = [
        renderStatCard({ label: "Conversations", value: formatNumber(meetings.length), note: "Meeting rooms available as message threads.", iconName: "message" }),
        renderStatCard({ label: "Ongoing Rooms", value: formatNumber(ongoing.length), note: "Rooms currently marked active or live.", iconName: "video", accent: "success" }),
        renderStatCard({ label: "Participants", value: formatNumber(participants), note: "Visible participant entries across all rooms.", iconName: "users", accent: "info" }),
        renderStatCard({ label: "Chat Ready", value: selectedMeetingId ? "Yes" : "No", note: "Select a room to post messages.", iconName: "bot", accent: "warning" })
    ].join("");

    registerAssistantContext({
        pageTitle: "the chat workspace",
        summary: [
            formatNumber(meetings.length) + " meeting conversations are available in the sidebar.",
            formatNumber(ongoing.length) + " rooms are currently ongoing.",
            "Selecting a conversation opens the live meeting-message thread and room actions."
        ],
        suggestions: [
            "Summarize chat",
            "How many conversations are available?",
            "How many rooms are ongoing?",
            "How do I send a message?"
        ],
        metrics: {
            meetings: formatNumber(meetings.length) + " conversation rooms",
            meetingNote: formatNumber(ongoing.length) + " rooms are ongoing right now."
        }
    });
}

function renderLayout() {
    pageRoot.innerHTML = [
        '<section class="page-header"><div><span class="section-kicker">Chat system</span><h3>Room conversations and direct thread workflow</h3><p>The chat workspace is powered by live meeting conversations, giving you a sidebar of rooms and a focused thread view for messaging.</p></div><div class="toolbar-actions"><a class="button" href="',
        buildHref("meetings.html"),
        '">Meetings</a><a class="button-secondary" href="',
        buildHref("index.html"),
        '">Home</a></div></section><section class="stats-grid" id="chat-summary"></section><section class="chat-layout"><aside class="chat-sidebar"><div class="toolbar"><div><span class="section-kicker">Conversations</span><h4 class="page-panel-title">Meeting rooms</h4></div><span class="tag">',
        escapeHtml(formatNumber(meetings.length)),
        ' rooms</span></div><div class="field"><label for="conversation-search">Search rooms</label><input id="conversation-search" type="search" placeholder="Search by title, course, or status"></div><div id="conversation-list-root"></div></aside><div id="conversation-thread-root"></div></section>'
    ].join("");

    document.getElementById("conversation-search").addEventListener("input", renderConversationSidebar);
}

async function init() {
    session = requireSession(["Admin", "Staff", "Teacher", "Student"]);
    if (!session) {
        return;
    }

    pageRoot = mountAppShell({
        session,
        currentKey: "chat",
        workspaceLabel: "Chat",
        brandTitle: "Conversation Hub",
        brandCopy: "Reusable chat thread UI over live meeting-room conversations and message history.",
        title: "Chat",
        subtitle: "Conversation sidebar, message thread, and meeting-aware actions",
        searchPlaceholder: "Search chats or rooms",
        quickActions: [
            { label: "Meetings", href: buildHref("meetings.html"), iconName: "video", variant: "button" }
        ],
        notifications: [
            { title: "Loading chat", description: "Fetching meeting conversations and room messages." }
        ]
    });

    pageRoot.innerHTML = '<div class="loading-state">Loading chat workspace...</div>';

    try {
        meetings = asArray(await apiRequest("/api/meetings"));
        selectedMeetingId = Number(readQueryParam("meetingId") || 0);
        if (!selectedMeetingId && meetings[0]) {
            selectedMeetingId = meetings[0].meetingId;
        }
        renderLayout();
        renderConversationSidebar();
        renderSummaryCards();
        await loadThread();
    } catch (error) {
        pageRoot.innerHTML = renderErrorState(error.message);
    }
}

document.addEventListener("DOMContentLoaded", init);
