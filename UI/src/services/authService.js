import api from "./api";

// 🔐 LOGIN
export const loginUser = (data) =>
  api("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });

// 🆕 REGISTER (optional if you support it)
export const registerUser = (data) =>
  api("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

// 🚪 LOGOUT (frontend only)
export const logoutUser = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("role");
};