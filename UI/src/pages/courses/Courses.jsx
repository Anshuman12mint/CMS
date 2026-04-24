import React, { useEffect, useState } from "react";
import Table from "../../components/common/Table";

const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [form, setForm] = useState({
    course_code: "",
    course_name: "",
  });

  const fetchCourses = () => {
    fetch("http://localhost:8000/api/courses", {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    })
      .then((res) => res.json())
      .then(setCourses);
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const createCourse = () => {
    fetch("http://localhost:8000/api/courses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(form),
    }).then(() => {
      fetchCourses();
      setForm({ course_code: "", course_name: "" });
    });
  };

  return (
    <div>
      <h2>Courses</h2>

      {/* 🔥 Add Course */}
      <div style={styles.form}>
        <input
          placeholder="Course Code"
          value={form.course_code}
          onChange={(e) =>
            setForm({ ...form, course_code: e.target.value })
          }
        />

        <input
          placeholder="Course Name"
          value={form.course_name}
          onChange={(e) =>
            setForm({ ...form, course_name: e.target.value })
          }
        />

        <button onClick={createCourse}>Add Course</button>
      </div>

      {/* 🔥 Table */}
      <Table
        columns={["course_code", "course_name"]}
        data={courses}
      />
    </div>
  );
};

const styles = {
  form: {
    marginBottom: "20px",
  },
};

export default Courses;