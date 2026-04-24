import { escapeHtml } from "../core.js";

function renderOption(option, value) {
    const optionValue = typeof option === "object" ? option.value : option;
    const optionLabel = typeof option === "object" ? option.label : option;
    const selected = String(optionValue ?? "") === String(value ?? "") ? ' selected' : "";
    return '<option value="' + escapeHtml(optionValue) + '"' + selected + ">" + escapeHtml(optionLabel) + "</option>";
}

function renderField(field) {
    const {
        name,
        label,
        type = "text",
        value = "",
        placeholder = "",
        required = false,
        options = [],
        rows = 4,
        min = "",
        max = "",
        step = "",
        full = false
    } = field;

    const className = full ? "field span-2" : "field";
    const requiredAttr = required ? " required" : "";
    const placeholderAttr = placeholder ? ' placeholder="' + escapeHtml(placeholder) + '"' : "";
    const minAttr = min !== "" ? ' min="' + escapeHtml(min) + '"' : "";
    const maxAttr = max !== "" ? ' max="' + escapeHtml(max) + '"' : "";
    const stepAttr = step !== "" ? ' step="' + escapeHtml(step) + '"' : "";

    if (type === "textarea") {
        return [
            '<div class="',
            className,
            '"><label for="',
            escapeHtml(name),
            '">',
            escapeHtml(label),
            "</label><textarea id=\"",
            escapeHtml(name),
            '" name="',
            escapeHtml(name),
            '" rows="',
            escapeHtml(rows),
            '"',
            placeholderAttr,
            requiredAttr,
            ">",
            escapeHtml(value),
            "</textarea></div>"
        ].join("");
    }

    if (type === "select") {
        return [
            '<div class="',
            className,
            '"><label for="',
            escapeHtml(name),
            '">',
            escapeHtml(label),
            "</label><select id=\"",
            escapeHtml(name),
            '" name="',
            escapeHtml(name),
            '"',
            requiredAttr,
            ">",
            options.map(function (option) {
                return renderOption(option, value);
            }).join(""),
            "</select></div>"
        ].join("");
    }

    return [
        '<div class="',
        className,
        '"><label for="',
        escapeHtml(name),
        '">',
        escapeHtml(label),
        "</label><input id=\"",
        escapeHtml(name),
        '" name="',
        escapeHtml(name),
        '" type="',
        escapeHtml(type),
        '" value="',
        escapeHtml(value),
        '"',
        placeholderAttr,
        requiredAttr,
        minAttr,
        maxAttr,
        stepAttr,
        "></div>"
    ].join("");
}

export function renderFormGrid(fields, columns = 2) {
    return '<div class="field-grid' + (columns === 2 ? " two" : "") + '">' + fields.map(renderField).join("") + "</div>";
}

export function serializeForm(form) {
    const data = new FormData(form);
    const result = {};

    data.forEach(function (value, key) {
        result[key] = String(value);
    });

    return result;
}
