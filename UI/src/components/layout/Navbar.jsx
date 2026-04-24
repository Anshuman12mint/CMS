import React from "react";

const Navbar = () => {
  const username = localStorage.getItem("username");

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/login";
  };

  return (
    <div style={styles.navbar}>
      <h3>Welcome, {username}</h3>
      <button onClick={handleLogout} style={styles.btn}>Logout</button>
    </div>
  );
};

const styles = {
  navbar: {
    height: "60px",
    background: "#0f172a",
    color: "#fff",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0 20px",
  },
  btn: {
    padding: "6px 12px",
    background: "#ef4444",
    border: "none",
    color: "#fff",
    cursor: "pointer",
  },
};

export default Navbar;