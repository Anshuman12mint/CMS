import React from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div style={styles.container}>
      <Sidebar />

      <div style={styles.main}>
        <Navbar />

        <div style={styles.content}>
          <Outlet />
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: { display: "flex" },
  main: { flex: 1, display: "flex", flexDirection: "column" },
  content: {
    padding: "20px",
    background: "#f1f5f9",
    minHeight: "calc(100vh - 60px)",
  },
};

export default Layout;