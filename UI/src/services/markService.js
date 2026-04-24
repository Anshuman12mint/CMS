import api from "./api";

export const getMarks = () => api("/marks");

export const getMarkById = (id) =>
  api(`/marks/${id}`);

export const createMark = (data) =>
  api("/marks", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateMark = (id, data) =>
  api(`/marks/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteMark = (id) =>
  api(`/marks/${id}`, {
    method: "DELETE",
  });