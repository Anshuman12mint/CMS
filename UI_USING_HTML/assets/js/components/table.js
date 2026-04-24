import { escapeHtml, renderEmptyState } from "../core.js";

export function renderTable(options) {
    const {
        columns = [],
        rows = [],
        emptyMessage = "No rows available right now.",
        bodyId = "",
        tableClass = "data-table"
    } = options;

    return [
        '<div class="table-wrap"><table class="',
        escapeHtml(tableClass),
        '"><thead><tr>',
        columns.map(function (column) {
            return "<th>" + escapeHtml(column) + "</th>";
        }).join(""),
        "</tr></thead><tbody",
        bodyId ? ' id="' + escapeHtml(bodyId) + '"' : "",
        ">",
        rows.length ? rows.join("") : '<tr><td colspan="' + escapeHtml(columns.length) + '">' + renderEmptyState(emptyMessage) + "</td></tr>",
        "</tbody></table></div>"
    ].join("");
}

export function renderTableRow(cells, attrs = "") {
    return "<tr " + attrs + ">" + cells.map(function (cell) {
        return "<td>" + cell + "</td>";
    }).join("") + "</tr>";
}
