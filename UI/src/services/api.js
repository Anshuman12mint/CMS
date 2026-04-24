const BASE_URL = "http://localhost:8000/api";

const api = (url, options = {}) => {
  return fetch(BASE_URL + url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + localStorage.getItem("token"),
      ...options.headers,
    },
  }).then((res) => res.json());
};

export default api;