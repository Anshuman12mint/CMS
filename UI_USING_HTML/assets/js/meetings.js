import {
    byId,
    requireSession,
    hydrateShell,
    apiRequest,
    renderErrorState,
    renderEmptyState,
    renderStatusBadge,
    formatDateTime,
    setLoading,
    escapeHtml,
    fromLocalDateTimeInput,
    toLocalDateTimeInput,
    readQueryParam,
    getRoleName
} from "./core.js";

let session = null;
let meetings = [];
let courses = [];
let selectedMeetingId = null;
let pollHandle = null;

function canCreateMeetings() {
    const role = String(session?.role || "").trim().toUpperCase();
    return ["ADMIN", "TEACHER", "STAFF"].includes(role);
}

function renderMeetingList() {
    const target = byId("meeting-list");
    if (!meetings.length) {
        target.innerHTML = renderEmptyState("No meetings are available right now.");
        return;
    }

    target.innerHTML = meetings.map(function (meeting) {
        const activeClass = meeting.meetingId === selectedMeetingId ? " active" : "";
        return [
            '<button class="meeting-card',
            activeClass,
            '" type="button" data-meeting-id="',
            escapeHtml(meeting.meetingId),
            '">',
            '<span class="meeting-card-title">',
            escapeHtml(meeting.title || "Untitled meeting"),
            "</span>",
            '<span class="meeting-card-meta">',
            escapeHtml(formatDateTime(meeting.scheduledStartAt)),
            "</span>",
            '<span class="meeting-card-meta">',
            escapeHtml(meeting.courseCode || meeting.audienceType || "Open"),
            "</span>",
            renderStatusBadge(meeting.status),
            "</button>"
        ].join("");
    }).join("");

    target.querySelectorAll("[data-meeting-id]").forEach(function (button) {
        button.addEventListener("click", function () {
            selectedMeetingId = Number(button.getAttribute("data-meeting-id"));
            renderMeetingList();
            loadMeetingDetail();
        });
    });
}

function renderParticipants(participants) {
    const target = byId("meeting-participants");
    if (!participants.length) {
        target.innerHTML = renderEmptyState("No participants have joined yet.");
        return;
    }

    target.innerHTML = participants.map(function (participant) {
        return '<div class="participant-chip"><strong>' + escapeHtml(participant.displayName || participant.username || "Participant") + "</strong><span>" + escapeHtml(participant.role || "--") + "</span></div>";
    }).join("");
}

function renderMessages(messages) {
    const target = byId("meeting-messages");
    if (!messages.length) {
        target.innerHTML = renderEmptyState("No chat messages yet. Join the meeting and start the conversation.");
        return;
    }

    target.innerHTML = messages.map(function (message) {
        return [
            '<article class="chat-message">',
            '<div class="chat-message-head"><strong>',
            escapeHtml(message.displayName || message.username || "User"),
            "</strong><span>",
            escapeHtml(formatDateTime(message.createdAt)),
            "</span></div>",
            '<p>',
            escapeHtml(message.messageText || ""),
            "</p>",
            "</article>"
        ].join("");
    }).join("");

    target.scrollTop = target.scrollHeight;
}

async function refreshMeetings(selectQuery = false) {
    meetings = await apiRequest("/api/meetings");
    const queryMeetingId = Number(readQueryParam("meetingId") || 0);
    if (selectQuery && queryMeetingId) {
        const exists = meetings.some(function (meeting) {
            return meeting.meetingId === queryMeetingId;
        });
        if (exists) {
            selectedMeetingId = queryMeetingId;
        }
    }
    if (!selectedMeetingId && meetings.length) {
        selectedMeetingId = meetings[0].meetingId;
    }
    renderMeetingList();
}

async function loadMeetingDetail() {
    const detailTarget = byId("meeting-detail");
    const messagesTarget = byId("meeting-messages");
    if (!selectedMeetingId) {
        detailTarget.innerHTML = renderEmptyState("Choose a meeting to see its details.");
        messagesTarget.innerHTML = renderEmptyState("Choose a meeting to load its chat.");
        return;
    }

    setLoading(detailTarget, "Loading meeting details...");
    setLoading(messagesTarget, "Loading chat...");

    try {
        const [meeting, messages] = await Promise.all([
            apiRequest("/api/meetings/" + selectedMeetingId),
            apiRequest("/api/meetings/" + selectedMeetingId + "/messages")
        ]);

        detailTarget.innerHTML = [
            '<div class="meeting-detail-head"><div><span class="section-kicker">Selected meeting</span><h3>',
            escapeHtml(meeting.title || "Untitled meeting"),
            "</h3><p class=\"muted\">",
            escapeHtml(meeting.description || "No description"),
            "</p></div><div>",
            renderStatusBadge(meeting.status),
            "</div></div>",
            '<div class="detail-grid">',
            '<div class="detail-pair"><span>Provider</span><strong>',
            escapeHtml(meeting.provider || "--"),
            '</strong></div>',
            '<div class="detail-pair"><span>Course</span><strong>',
            escapeHtml(meeting.courseCode || meeting.audienceType || "Open"),
            '</strong></div>',
            '<div class="detail-pair"><span>Start</span><strong>',
            escapeHtml(formatDateTime(meeting.scheduledStartAt)),
            '</strong></div>',
            '<div class="detail-pair"><span>Host</span><strong>',
            escapeHtml(meeting.hostUsername || "--"),
            "</strong></div></div>",
            '<div class="button-row" id="meeting-actions"></div>',
            '<div><span class="section-kicker">Participants</span><div id="meeting-participants"></div></div>'
        ].join("");

        const actions = [];
        if (meeting.canJoin) {
            actions.push('<button class="button" type="button" id="join-meeting-action">Join Meeting</button>');
        }
        if (meeting.joinUrl) {
            actions.push('<a class="button-secondary" href="' + escapeHtml(meeting.joinUrl) + '" target="_blank" rel="noreferrer">Open Room</a>');
        }
        actions.push('<button class="button-quiet" type="button" id="leave-meeting-action">Leave</button>');
        if (meeting.canManage) {
            actions.push('<button class="button-danger" type="button" id="end-meeting-action">End Meeting</button>');
        }
        byId("meeting-actions").innerHTML = actions.join("");
        renderParticipants(meeting.participants || []);
        renderMessages(messages || []);

        const joinButton = byId("join-meeting-action");
        if (joinButton) {
            joinButton.addEventListener("click", async function () {
                try {
                    const joinResponse = await apiRequest("/api/meetings/" + selectedMeetingId + "/join", { method: "POST" });
                    if (joinResponse?.joinUrl) {
                        window.open(joinResponse.joinUrl, "_blank", "noopener");
                    }
                    await refreshMeetings();
                    await loadMeetingDetail();
                } catch (error) {
                    detailTarget.innerHTML += renderErrorState(error.message);
                }
            });
        }

        const leaveButton = byId("leave-meeting-action");
        if (leaveButton) {
            leaveButton.addEventListener("click", async function () {
                try {
                    await apiRequest("/api/meetings/" + selectedMeetingId + "/leave", { method: "POST" });
                    await refreshMeetings();
                    await loadMeetingDetail();
                } catch (error) {
                    detailTarget.innerHTML += renderErrorState(error.message);
                }
            });
        }

        const endButton = byId("end-meeting-action");
        if (endButton) {
            endButton.addEventListener("click", async function () {
                try {
                    await apiRequest("/api/meetings/" + selectedMeetingId + "/end", { method: "POST" });
                    await refreshMeetings();
                    await loadMeetingDetail();
                } catch (error) {
                    detailTarget.innerHTML += renderErrorState(error.message);
                }
            });
        }
    } catch (error) {
        detailTarget.innerHTML = renderErrorState(error.message);
        messagesTarget.innerHTML = renderErrorState(error.message);
    }
}

async function handleMessageSubmit(event) {
    event.preventDefault();
    const input = byId("message-text");
    const value = input.value.trim();
    if (!selectedMeetingId || !value) {
        return;
    }

    try {
        await apiRequest("/api/meetings/" + selectedMeetingId + "/messages", {
            method: "POST",
            body: { messageText: value }
        });
        input.value = "";
        byId("chat-status").textContent = "Message sent.";
        byId("chat-status").className = "status-banner success compact";
        await loadMeetingDetail();
    } catch (error) {
        byId("chat-status").textContent = error.message;
        byId("chat-status").className = "status-banner error compact";
    }
}

async function handleCreateMeeting(event) {
    event.preventDefault();
    const status = byId("create-status");
    status.textContent = "Creating meeting...";
    status.className = "status-banner info compact";

    try {
        const created = await apiRequest("/api/meetings", {
            method: "POST",
            body: {
                title: byId("meeting-title").value.trim(),
                description: byId("meeting-description").value.trim() || null,
                courseCode: byId("meeting-course").value || null,
                scheduledStartAt: fromLocalDateTimeInput(byId("meeting-start").value),
                scheduledEndAt: fromLocalDateTimeInput(byId("meeting-end").value)
            }
        });
        status.textContent = "Meeting created.";
        status.className = "status-banner success compact";
        selectedMeetingId = created.meetingId;
        await refreshMeetings();
        await loadMeetingDetail();
        byId("create-meeting-form").reset();
    } catch (error) {
        status.textContent = error.message;
        status.className = "status-banner error compact";
    }
}

async function init() {
    session = requireSession(["Admin", "Staff", "Teacher", "Student"]);
    if (!session) {
        return;
    }

    hydrateShell(session, { pageTitle: "CMS Meetings" });
    byId("meeting-role").textContent = getRoleName(session.role);
    byId("meeting-role-note").textContent = "Signed in as " + (session.username || "user") + ".";

    if (!canCreateMeetings()) {
        byId("create-panel").classList.add("hidden");
    } else {
        courses = await apiRequest("/api/courses");
        byId("meeting-course").innerHTML = '<option value="">Open Meeting</option>' + courses.map(function (course) {
            return '<option value="' + escapeHtml(course.courseCode) + '">' + escapeHtml(course.courseCode + " - " + (course.courseName || "")) + "</option>";
        }).join("");
        const now = new Date();
        const oneHourLater = new Date(now.getTime() + (60 * 60 * 1000));
        byId("meeting-start").value = toLocalDateTimeInput(now);
        byId("meeting-end").value = toLocalDateTimeInput(oneHourLater);
        byId("create-meeting-form").addEventListener("submit", handleCreateMeeting);
    }

    byId("chat-form").addEventListener("submit", handleMessageSubmit);

    try {
        await refreshMeetings(true);
        await loadMeetingDetail();
    } catch (error) {
        byId("meeting-list").innerHTML = renderErrorState(error.message);
        byId("meeting-detail").innerHTML = renderErrorState(error.message);
        byId("meeting-messages").innerHTML = renderErrorState(error.message);
    }

    if (pollHandle) {
        clearInterval(pollHandle);
    }
    pollHandle = setInterval(async function () {
        if (!selectedMeetingId) {
            return;
        }
        try {
            await refreshMeetings();
            await loadMeetingDetail();
        } catch (_) {
            // Silent background polling failure; the visible state is kept.
        }
    }, 5000);
}

document.addEventListener("DOMContentLoaded", init);
