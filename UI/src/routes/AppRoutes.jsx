import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "../pages/auth/Login";
import Dashboard from "../pages/dashboard/Dashboard";
import StudentList from "../pages/students/StudentList";
import StudentForm from "../pages/students/StudentForm";
import Courses from "../pages/courses/Courses";
import Attendance from "../pages/attendance/Attendance";
import Fees from "../pages/fees/Fees";
import Marks from "../pages/marks/Marks";
import ChatPage from "../pages/chat/ChatPage";
import MeetingPage from "../pages/meetings/MeetingPage";

import Layout from "../components/layout/Layout";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");

  return token ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>

        {/* PUBLIC */}
        <Route path="/login" element={<Login />} />

        {/* PROTECTED */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="students" element={<StudentList />} />
          <Route path="students/add" element={<StudentForm />} />
          <Route path="courses" element={<Courses />} />
          <Route path="attendance" element={<Attendance />} />
          <Route path="fees" element={<Fees />} />
          <Route path="marks" element={<Marks />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="meetings" element={<MeetingPage />} />
        </Route>

        {/* DEFAULT */}
        <Route path="*" element={<Navigate to="/login" />} />

      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;