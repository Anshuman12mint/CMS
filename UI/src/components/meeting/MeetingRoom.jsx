import React, { useState } from "react";
import VideoFrame from "./VideoFrame";
import ParticipantList from "./ParticipantList";
import ChatBox from "../chat/ChatBox";

const MeetingRoom = ({ meeting }) => {
  const [participants] = useState([
    { id: 1, name: "Teacher" },
    { id: 2, name: "Student" },
  ]);

  if (!meeting) return <div>Select a meeting</div>;

  return (
    <div style={styles.container}>
      <div style={styles.left}>
        <VideoFrame roomName={meeting.room_name} />
        <ChatBox selectedUser={{ name: "Meeting Chat" }} />
      </div>

      <ParticipantList participants={participants} />
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    gap: "10px",
  },
  left: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
};

export default MeetingRoom;