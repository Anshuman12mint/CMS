import React from "react";
import { Link } from "react-router-dom";

const Sidebar = () => {
  const role = localStorage.getItem("role");

  return (
    <div style={styles.sidebar}>
      <h2 style={styles.logo}>CMS</h2>

      <nav>
        <Link to="/dashboard" style={styles.link}>Dashboard</Link>

        {role === "Admin" && (
          <>
            <Link to="/students" style={styles.link}>Students</Link>
            <Link to="/courses" style={styles.link}>Courses</Link>
            <Link to="/attendance" style={styles.link}>Attendance</Link>
            <Link to="/fees" style={styles.link}>Fees</Link>
            <Link to="/marks" style={styles.link}>Marks</Link>
            <Link to="/meetings" style={styles.link}>Meetings</Link>
          </>
        )}

        {role === "Teacher" && (
          <>
            <Link to="/students" style={styles.link}>My Students</Link>
            <Link to="/attendance" style={styles.link}>Attendance</Link>
            <Link to="/marks" style={styles.link}>Marks</Link>
            <Link to="/meetings" style={styles.link}>Meetings</Link>
          </>
        )}

        <Link to="/chat" style={styles.link}>Chat</Link>
      </nav>
    </div>
  );
};

const styles = {
  sidebar: {
    width: "220px",
    height: "100vh",
    background: "#1e293b",
    color: "#fff",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
  },
  logo: {
    marginBottom: "20px",
  },
  link: {
    display: "block",
    color: "#cbd5f5",
    textDecoration: "none",
    marginBottom: "10px",
  },
};

export default Sidebar;