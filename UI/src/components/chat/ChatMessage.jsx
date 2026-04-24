import React from "react";

const ChatMessage = ({ message, isOwn }) => {
  return (
    <div
      style={{
        ...styles.message,
        alignSelf: isOwn ? "flex-end" : "flex-start",
        background: isOwn ? "#3b82f6" : "#e2e8f0",
        color: isOwn ? "#fff" : "#000",
      }}
    >
      {message.text}
    </div>
  );
};

const styles = {
  message: {
    padding: "8px 12px",
    borderRadius: "10px",
    margin: "5px",
    maxWidth: "60%",
  },
};

export default ChatMessage;