import React from "react";

const Button = ({ children, onClick, type = "primary" }) => {
  return (
    <button
      onClick={onClick}
      style={{
        ...styles.btn,
        ...(type === "danger" ? styles.danger : {}),
      }}
    >
      {children}
    </button>
  );
};

const styles = {
  btn: {
    padding: "10px 16px",
    background: "#3b82f6",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  danger: {
    background: "#ef4444",
  },
};

export default Button;