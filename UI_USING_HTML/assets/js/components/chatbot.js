import { escapeHtml } from "../core.js";
import { icon } from "./icons.js";

let sessionState = null;
let contextState = {
    pageTitle: "this workspace",
    summary: [],
    suggestions: [],
    metrics: {}
};
let messageState = [];

function ensureAssistantRoot() {
    let root = document.getElementById("assistant-root");
    if (!root) {
        root = document.createElement("div");
        root.id = "assistant-root";
        document.body.appendChild(root);
    }
    return root;
}

function formatSummary() {
    return contextState.summary && contextState.summary.length
        ? contextState.summary.slice(0, 3).join(" ")
        : "I can summarize this page, point you to the right workflow, and help interpret the live data.";
}

function buildWelcomeMessage() {
    const displayName = sessionState?.displayName || sessionState?.username || "there";
    return "Hi " + displayName + ". Ask me about " + contextState.pageTitle + ", current numbers, or where to go next.";
}

function renderMessages() {
    const root = ensureAssistantRoot();
    const suggestions = contextState.suggestions || [];
    root.innerHTML = [
        '<button class="floating-bot" type="button" id="assistant-toggle" aria-label="Open AI assistant">',
        icon("bot"),
        "</button>",
        '<section class="floating-panel" id="assistant-panel"><header class="floating-panel-head"><div><span class="section-kicker">AI chatbot</span><h4>Campus Copilot</h4></div><button class="icon-button" type="button" id="assistant-close" aria-label="Close">',
        icon("close"),
        '</button></header><div class="floating-panel-body" id="assistant-messages">',
        messageState.map(function (message) {
            return '<article class="bot-message ' + escapeHtml(message.role) + '"><p>' + escapeHtml(message.text) + "</p></article>";
        }).join(""),
        '</div><div class="bot-suggestions">',
        suggestions.slice(0, 4).map(function (suggestion) {
            return '<button class="bot-chip" type="button" data-bot-suggestion="' + escapeHtml(suggestion) + '">' + escapeHtml(suggestion) + "</button>";
        }).join(""),
        '</div><form class="floating-panel-foot" id="assistant-form"><textarea id="assistant-input" placeholder="Ask about this page, meetings, fees, attendance, or next steps"></textarea><button class="button" type="submit">Ask</button></form></section>'
    ].join("");

    const panel = document.getElementById("assistant-panel");
    const toggle = document.getElementById("assistant-toggle");
    const close = document.getElementById("assistant-close");
    const form = document.getElementById("assistant-form");
    const body = document.getElementById("assistant-messages");

    toggle.addEventListener("click", function () {
        panel.classList.add("open");
    });

    close.addEventListener("click", function () {
        panel.classList.remove("open");
    });

    root.querySelectorAll("[data-bot-suggestion]").forEach(function (button) {
        button.addEventListener("click", function () {
            handleQuestion(button.getAttribute("data-bot-suggestion") || "");
        });
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const input = document.getElementById("assistant-input");
        const value = input.value.trim();
        if (!value) {
            return;
        }
        input.value = "";
        handleQuestion(value);
    });

    body.scrollTop = body.scrollHeight;
}

function buildMetricsResponse(input) {
    const metrics = contextState.metrics || {};

    if ((/fee|pending|dues|payment/.test(input)) && metrics.pendingFees !== undefined) {
        return "Pending fees are at " + metrics.pendingFees + ". " + (metrics.pendingFeeNote || "");
    }
    if (/attendance|present|absent/.test(input) && metrics.attendance !== undefined) {
        return "Attendance snapshot: " + metrics.attendance + ". " + (metrics.attendanceNote || "");
    }
    if (/mark|grade|score|assessment/.test(input) && metrics.marks !== undefined) {
        return "Marks snapshot: " + metrics.marks + ". " + (metrics.marksNote || "");
    }
    if (/meeting|session|call|room/.test(input) && metrics.meetings !== undefined) {
        return "Meetings overview: " + metrics.meetings + ". " + (metrics.meetingNote || "");
    }
    if (/student/.test(input) && metrics.students !== undefined) {
        return "Students in view: " + metrics.students + ". " + (metrics.studentNote || "");
    }
    if (/teacher|faculty/.test(input) && metrics.teachers !== undefined) {
        return "Teachers in view: " + metrics.teachers + ". " + (metrics.teacherNote || "");
    }
    if (/course|subject|academics/.test(input) && metrics.courses !== undefined) {
        return "Academic setup snapshot: " + metrics.courses + ". " + (metrics.courseNote || "");
    }
    return "";
}

function generateResponse(rawInput) {
    const input = String(rawInput || "").trim().toLowerCase();

    if (!input) {
        return "Send me a question and I will summarize the live page state for you.";
    }

    if (/hello|hi|hey/.test(input)) {
        return buildWelcomeMessage();
    }

    if (/help|what can you do|how to use/.test(input)) {
        const suggestions = (contextState.suggestions || []).slice(0, 4).join(", ");
        return "I can explain this page, summarize live metrics, and point you to likely next actions. Try: " + suggestions + ".";
    }

    if (/summary|summarize|overview|status/.test(input)) {
        return formatSummary();
    }

    if (/where|navigate|open|go to|next/.test(input)) {
        return "Use the sidebar for the main modules, and the quick actions in the top bar for the fastest path. " + formatSummary();
    }

    const metricResponse = buildMetricsResponse(input);
    if (metricResponse) {
        return metricResponse;
    }

    return "Here is the short version: " + formatSummary();
}

function handleQuestion(input) {
    messageState.push({ role: "user", text: input });
    messageState.push({ role: "bot", text: generateResponse(input) });
    renderMessages();
    document.getElementById("assistant-panel").classList.add("open");
}

export function registerAssistantContext(context) {
    contextState = {
        ...contextState,
        ...context
    };

    if (!messageState.length) {
        messageState = [{ role: "bot", text: buildWelcomeMessage() }];
    } else {
        messageState[0] = { role: "bot", text: buildWelcomeMessage() };
    }

    renderMessages();
}

export function mountAssistant(session) {
    sessionState = session;
    if (!messageState.length) {
        messageState = [{ role: "bot", text: buildWelcomeMessage() }];
    }
    renderMessages();
}
