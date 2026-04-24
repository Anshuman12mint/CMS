import React, { useState, useEffect } from "react";
import ChatSidebar from "../../components/chat/ChatSidebar";
import ChatBox from "../../components/chat/ChatBox";

const ChatPage = () => {
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // 🔥 replace later with real API
    fetch("http://localhost:8000/api/users", {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    })
      .then((res) => res.json())
      .then(setUsers);
  }, []);

  return (
    <div style={styles.container}>
      <ChatSidebar users={users} onSelectUser={setSelectedUser} />
      <ChatBox selectedUser={selectedUser} />
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    height: "80vh",
  },
};

export default ChatPage;