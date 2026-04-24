import api from "./api";

export const getStudents = () => api("/students");

export const getStudentById = (id) => api(`/students/${id}`);

export const createStudent = (data) =>
  api("/students", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateStudent = (id, data) =>
  api(`/students/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteStudent = (id) =>
  api(`/students/${id}`, {
    method: "DELETE",
  });