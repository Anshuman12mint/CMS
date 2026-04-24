import React, { useState } from "react";
import ChatMessage from "./ChatMessage";

const ChatBox = ({ selectedUser }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input) return;

    const newMessage = {
      text: input,
      sender: "me",
    };

    setMessages([...messages, newMessage]);
    setInput("");

    // 🔥 later: send to API
  };

  return (
    <div style={styles.container}>
      <h3>{selectedUser ? selectedUser.name : "Select a chat"}</h3>

      <div style={styles.messages}>
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            message={msg}
            isOwn={msg.sender === "me"}
          />
        ))}
      </div>

      {selectedUser && (
        <div style={styles.inputBox}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={styles.input}
            placeholder="Type message..."
          />
          <button onClick={sendMessage} style={styles.btn}>
            Send
          </button>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    background: "#f1f5f9",
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "10px",
    display: "flex",
    flexDirection: "column",
  },
  inputBox: {
    display: "flex",
    padding: "10px",
    background: "#fff",
  },
  input: {
    flex: 1,
    padding: "10px",
    marginRight: "10px",
  },
  btn: {
    padding: "10px",
    background: "#3b82f6",
    color: "#fff",
    border: "none",
  },
};

export default ChatBox;