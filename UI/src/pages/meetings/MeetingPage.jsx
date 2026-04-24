import React, { useState } from "react";
import MeetingList from "./MeetingList";
import MeetingRoom from "../../components/meeting/MeetingRoom";

const MeetingPage = () => {
  const [selectedMeeting, setSelectedMeeting] = useState(null);

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <MeetingList onSelect={setSelectedMeeting} />
      </div>

      <div style={styles.main}>
        <MeetingRoom meeting={selectedMeeting} />
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    height: "80vh",
  },
  sidebar: {
    width: "250px",
    overflowY: "auto",
  },
  main: {
    flex: 1,
    padding: "10px",
  },
};

export default MeetingPage;