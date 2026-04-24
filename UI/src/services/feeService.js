import api from "./api";

export const getFees = () => api("/fees");

export const getFeeById = (id) =>
  api(`/fees/${id}`);

export const createFee = (data) =>
  api("/fees", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateFee = (id, data) =>
  api(`/fees/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteFee = (id) =>
  api(`/fees/${id}`, {
    method: "DELETE",
  });