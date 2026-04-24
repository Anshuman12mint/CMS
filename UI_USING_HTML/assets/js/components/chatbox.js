import { escapeHtml, formatDateTime, renderEmptyState, renderStatusBadge } from "../core.js";

export function renderConversationList(options) {
    const {
        items = [],
        selectedId = null,
        getId,
        getTitle,
        getMeta,
        getStatus
    } = options;

    if (!items.length) {
        return renderEmptyState("No conversations are available yet.");
    }

    return '<div class="conversation-list">' + items.map(function (item) {
        const itemId = getId(item);
        const activeClass = String(itemId) === String(selectedId) ? " active" : "";
        const meta = getMeta ? getMeta(item) : "";
        const status = getStatus ? getStatus(item) : "";
        return [
            '<button class="conversation-item',
            activeClass,
            '" type="button" data-conversation-id="',
            escapeHtml(itemId),
            '"><div class="conversation-item-main"><strong>',
            escapeHtml(getTitle(item)),
            "</strong>",
            meta ? '<span class="meta">' + escapeHtml(meta) + "</span>" : "",
            "</div>",
            status ? renderStatusBadge(status) : "",
            "</button>"
        ].join("");
    }).join("") + "</div>";
}

export function renderMessageList(messages, currentUsername) {
    if (!messages.length) {
        return renderEmptyState("No messages yet. Start the conversation when you're ready.");
    }

    return messages.map(function (message) {
        const self = String(message.username || "").toLowerCase() === String(currentUsername || "").toLowerCase();
        return [
            '<article class="chat-bubble',
            self ? " self" : "",
            '"><div class="chat-message-head"><strong>',
            escapeHtml(message.displayName || message.username || "User"),
            "</strong><span>",
            escapeHtml(formatDateTime(message.createdAt)),
            '</span></div><p>',
            escapeHtml(message.messageText || ""),
            "</p></article>"
        ].join("");
    }).join("");
}

export function renderChatThread(options) {
    const {
        title,
        meta = "",
        messages = [],
        currentUsername = "",
        formId = "chat-form",
        inputId = "message-text",
        placeholder = "Write your message"
    } = options;

    return [
        '<section class="chat-thread"><header class="chat-thread-head"><div><h3>',
        escapeHtml(title),
        "</h3>",
        meta ? '<p class="muted">' + escapeHtml(meta) + "</p>" : "",
        '</div></header><div class="chat-scroll" id="meeting-messages">',
        renderMessageList(messages, currentUsername),
        '</div><form class="chat-composer" id="',
        escapeHtml(formId),
        '"><textarea id="',
        escapeHtml(inputId),
        '" placeholder="',
        escapeHtml(placeholder),
        '"></textarea><div class="button-row"><button class="button" type="submit">Send</button></div><div id="chat-status" class="status-banner info compact">Messages are saved to the active room.</div></form></section>'
    ].join("");
}
