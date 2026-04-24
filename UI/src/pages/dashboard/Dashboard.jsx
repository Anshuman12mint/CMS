import React, { useEffect, useState } from "react";
import Card from "../../components/common/Card";

const Dashboard = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/dashboard", {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    })
      .then((res) => res.json())
      .then(setData);
  }, []);

  if (!data) return <p>Loading...</p>;

  return (
    <div style={styles.grid}>
      <Card title="Students" value={data.summary?.totalStudents} />
      <Card title="Teachers" value={data.summary?.totalTeachers} />
      <Card title="Courses" value={data.summary?.totalCourses} />
      <Card title="Fees Pending" value={data.summary?.pendingFeeCount} />
    </div>
  );
};

const styles = {
  grid: {
    display: "flex",
    gap: "10px",
  },
};

export default Dashboard;