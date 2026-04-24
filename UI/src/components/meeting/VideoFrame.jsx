import React from "react";

const VideoFrame = ({ roomName }) => {
  if (!roomName) return <div>Select meeting</div>;

  return (
    <iframe
      src={`https://meet.jit.si/${roomName}`}
      style={styles.frame}
      allow="camera; microphone; fullscreen"
      title="Meeting"
    />
  );
};

const styles = {
  frame: {
    width: "100%",
    height: "400px",
    border: "none",
    borderRadius: "10px",
  },
};

export default VideoFrame;