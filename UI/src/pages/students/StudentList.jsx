import React, { useEffect, useState } from "react";
import Table from "../../components/common/Table";

const StudentList = () => {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/students", {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    })
      .then((res) => res.json())
      .then(setStudents);
  }, []);

  return (
    <div>
      <h2>Students</h2>

      <Table
        columns={["first_name", "last_name", "email"]}
        data={students}
      />
    </div>
  );
};

export default StudentList;