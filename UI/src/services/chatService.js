import api from "./api";

export const getMessages = (meetingId) =>
  api(`/meetings/${meetingId}/messages`);

export const sendMessage = (meetingId, message) =>
  api(`/meetings/${meetingId}/messages`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });