import { icon } from "./icons.js";
import { escapeHtml } from "../core.js";

let handleEsc = null;

function ensureModalRoot() {
    let root = document.getElementById("modal-root");
    if (!root) {
        root = document.createElement("div");
        root.id = "modal-root";
        document.body.appendChild(root);
    }
    return root;
}

export function closeModal() {
    const root = ensureModalRoot();
    root.innerHTML = "";
    document.body.classList.remove("modal-open");
    if (handleEsc) {
        document.removeEventListener("keydown", handleEsc);
        handleEsc = null;
    }
}

export function openModal(options) {
    const {
        title,
        description = "",
        body = "",
        wide = false,
        onOpen = null
    } = options;

    const root = ensureModalRoot();
    root.innerHTML = [
        '<div class="modal-backdrop open" data-modal-close></div>',
        '<section class="modal',
        wide ? " wide" : "",
        ' open" role="dialog" aria-modal="true"><div class="modal-head"><div><h3>',
        escapeHtml(title),
        "</h3>",
        description ? '<p class="muted">' + escapeHtml(description) + "</p>" : "",
        '</div><button class="icon-button" type="button" data-modal-close aria-label="Close">',
        icon("close"),
        '</button></div><div class="modal-body">',
        body,
        "</div></section>"
    ].join("");

    document.body.classList.add("modal-open");

    root.querySelectorAll("[data-modal-close]").forEach(function (node) {
        node.addEventListener("click", closeModal);
    });

    handleEsc = function (event) {
        if (event.key === "Escape") {
            closeModal();
        }
    };
    document.addEventListener("keydown", handleEsc);

    if (typeof onOpen === "function") {
        onOpen(root.querySelector(".modal"));
    }
}
