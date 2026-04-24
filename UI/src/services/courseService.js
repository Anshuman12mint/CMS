import api from "./api";

export const getCourses = () => api("/courses");

export const getCourseByCode = (code) =>
  api(`/courses/${code}`);

export const createCourse = (data) =>
  api("/courses", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateCourse = (code, data) =>
  api(`/courses/${code}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteCourse = (code) =>
  api(`/courses/${code}`, {
    method: "DELETE",
  });