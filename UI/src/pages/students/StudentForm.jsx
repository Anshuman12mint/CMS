import React, { useState } from "react";

const StudentForm = () => {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
  });

  const submit = () => {
    fetch("http://localhost:8000/api/students", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(form),
    }).then(() => alert("Student Added"));
  };

  return (
    <div>
      <h2>Add Student</h2>

      <input
        placeholder="First Name"
        onChange={(e) =>
          setForm({ ...form, first_name: e.target.value })
        }
      />

      <input
        placeholder="Last Name"
        onChange={(e) =>
          setForm({ ...form, last_name: e.target.value })
        }
      />

      <input
        placeholder="Email"
        onChange={(e) =>
          setForm({ ...form, email: e.target.value })
        }
      />

      <button onClick={submit}>Submit</button>
    </div>
  );
};

export default StudentForm;