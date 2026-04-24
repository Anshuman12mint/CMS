import React, { useEffect, useState } from "react";

const MeetingList = ({ onSelect }) => {
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/meetings")
      .then((res) => res.json())
      .then(setMeetings);
  }, []);

  return (
    <div>
      <h2>Meetings</h2>

      {meetings.map((m) => (
        <div key={m.meeting_id} style={styles.card}>
          <h4>{m.title}</h4>
          <button onClick={() => onSelect(m)}>Join</button>
        </div>
      ))}
    </div>
  );
};

const styles = {
  card: {
    padding: "10px",
    background: "#fff",
    marginBottom: "10px",
    borderRadius: "8px",
  },
};

export default MeetingList;