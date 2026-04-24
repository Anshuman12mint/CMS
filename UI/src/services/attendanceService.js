import api from "./api";

export const getAttendance = () => api("/attendance");

export const getAttendanceById = (id) =>
  api(`/attendance/${id}`);

export const markAttendance = (data) =>
  api("/attendance", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateAttendance = (id, data) =>
  api(`/attendance/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteAttendance = (id) =>
  api(`/attendance/${id}`, {
    method: "DELETE",
  });