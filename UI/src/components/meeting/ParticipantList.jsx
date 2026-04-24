import React from "react";

const ParticipantList = ({ participants }) => {
  return (
    <div style={styles.container}>
      <h4>Participants</h4>
      {participants.map((p) => (
        <div key={p.id} style={styles.item}>
          {p.name}
        </div>
      ))}
    </div>
  );
};

const styles = {
  container: {
    width: "200px",
    background: "#1e293b",
    color: "#fff",
    padding: "10px",
  },
  item: {
    padding: "6px",
    borderBottom: "1px solid #334155",
  },
};

export default ParticipantList;