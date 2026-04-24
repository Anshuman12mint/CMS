import React from "react";

const Card = ({ title, value }) => {
  return (
    <div style={styles.card}>
      <h4 style={styles.title}>{title}</h4>
      <p style={styles.value}>{value}</p>
    </div>
  );
};

const styles = {
  card: {
    padding: "20px",
    background: "#fff",
    borderRadius: "10px",
    boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
    margin: "10px",
    flex: 1,
  },
  title: {
    marginBottom: "10px",
    color: "#64748b",
  },
  value: {
    fontSize: "20px",
    fontWeight: "bold",
  },
};

export default Card;