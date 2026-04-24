import React from "react";

const ChatSidebar = ({ users, onSelectUser }) => {
  return (
    <div style={styles.sidebar}>
      <h3>Chats</h3>
      {users.map((user) => (
        <div
          key={user.id}
          style={styles.user}
          onClick={() => onSelectUser(user)}
        >
          {user.name}
        </div>
      ))}
    </div>
  );
};

const styles = {
  sidebar: {
    width: "200px",
    background: "#1e293b",
    color: "#fff",
    padding: "10px",
  },
  user: {
    padding: "10px",
    borderBottom: "1px solid #334155",
    cursor: "pointer",
  },
};

export default ChatSidebar;