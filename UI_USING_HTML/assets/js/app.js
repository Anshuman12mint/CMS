document.addEventListener("DOMContentLoaded", function () {
    var currentFile = window.location.pathname.split("/").pop() || "index.html";
    var navLinks = document.querySelectorAll(".nav-link");
    var statusTarget = document.querySelector("[data-demo-status]");
    var todayTargets = document.querySelectorAll("[data-today]");
    var sidebarToggle = document.querySelector("[data-sidebar-toggle]");

    navLinks.forEach(function (link) {
        var href = link.getAttribute("href") || "";
        if (href.indexOf(currentFile) !== -1) {
            link.classList.add("active");
        }
    });

    todayTargets.forEach(function (node) {
        node.textContent = new Date().toLocaleDateString("en-IN", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });
    });

    document.querySelectorAll("[data-demo-action]").forEach(function (button) {
        button.addEventListener("click", function () {
            var action = button.getAttribute("data-demo-action");
            if (statusTarget) {
                statusTarget.textContent = action + " is wired as a UI placeholder. Connect it to the FastAPI endpoint next.";
            }
        });
    });

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", function () {
            document.body.classList.toggle("sidebar-open");
        });
    }
});
