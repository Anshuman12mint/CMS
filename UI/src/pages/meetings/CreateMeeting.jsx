import React, { useState } from "react";

const CreateMeeting = () => {
  const [title, setTitle] = useState("");

  const createMeeting = () => {
    fetch("http://localhost:8000/api/meetings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        provider: "internal",
        meeting_code: Math.random().toString(36).substring(2, 8),
        room_name: "cms-" + Date.now(),
        status: "scheduled",
        audience_type: "course",
        scheduled_start_at: new Date().toISOString(),
      }),
    }).then(() => alert("Meeting Created"));
  };

  return (
    <div>
      <h2>Create Meeting</h2>

      <input
        placeholder="Meeting title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <button onClick={createMeeting}>Create</button>
    </div>
  );
};

export default CreateMeeting;