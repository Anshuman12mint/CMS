import api from "./api";

export const getMeetings = () => api("/meetings");

export const getMeetingById = (id) =>
  api(`/meetings/${id}`);

export const createMeeting = (data) =>
  api("/meetings", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateMeeting = (id, data) =>
  api(`/meetings/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteMeeting = (id) =>
  api(`/meetings/${id}`, {
    method: "DELETE",
  });

export const joinMeeting = (id) =>
  api(`/meetings/${id}/join`, { method: "POST" });

export const leaveMeeting = (id) =>
  api(`/meetings/${id}/leave`, { method: "POST" });

export const endMeeting = (id) =>
  api(`/meetings/${id}/end`, { method: "POST" });