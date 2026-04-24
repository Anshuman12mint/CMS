# API Overview

This document lists the main backend API groups. For exact request and response schemas, run the server and open:

```text
http://localhost:8000/docs
```

## Authentication

### Login

```http
POST /api/auth/login
```

Request:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response:

```json
{
  "token": "...",
  "issuedAt": "2026-04-22T10:00:00+00:00",
  "userId": 1,
  "username": "admin",
  "email": "admin@college.com",
  "role": "Admin",
  "studentId": null,
  "dashboard": {
    "type": "admin",
    "summary": {
      "totalStudents": 0,
      "totalTeachers": 0,
      "totalStaff": 0,
      "totalCourses": 0,
      "totalSubjects": 0,
      "totalUsers": 0,
      "totalAdmissions": 0,
      "totalAttendanceRecords": 0,
      "totalMarksRecorded": 0,
      "pendingFeeCount": 0,
      "pendingFeeAmount": "0",
      "recentAdmissions": []
    }
  }
}
```

### Register

```http
POST /api/auth/register
```

Requires an admin token.

## Authorization

Protected requests need:

```http
Authorization: Bearer <jwt-token>
```

Admin-only endpoints include user management and auth registration.

## Endpoint Groups

| Group | Methods And Paths |
| --- | --- |
| Health | `GET /health` |
| Auth | `POST /api/auth/login`, `POST /api/auth/register` |
| Users | `GET/POST /api/users`, `GET/PUT/DELETE /api/users/{userId}` |
| Courses | `GET/POST /api/courses`, `GET/PUT/DELETE /api/courses/{courseCode}` |
| Subjects | `GET/POST /api/subjects`, `GET/PUT/DELETE /api/subjects/{subjectId}` |
| Students | `GET/POST /api/students`, `GET/PUT/DELETE /api/students/{studentId}` |
| Admissions | `GET/POST /api/admissions`, `GET/PUT/DELETE /api/admissions/{studentId}` |
| Attendance | `GET/POST /api/attendance`, `GET/PUT/DELETE /api/attendance/{attendanceId}` |
| Fees | `GET/POST /api/fees`, `GET/PUT/DELETE /api/fees/{feeId}` |
| Marks | `GET/POST /api/marks`, `GET/PUT/DELETE /api/marks/{markId}` |
| Staff | `GET/POST /api/staff`, `GET/PUT/DELETE /api/staff/{staffId}` |
| Teachers | `GET/POST /api/teachers`, `GET/PUT/DELETE /api/teachers/{teacherId}` |
| Teacher Assignments | `PUT /api/teachers/{teacherId}/courses`, `PUT /api/teachers/{teacherId}/subjects` |
| Dashboard | `GET /api/dashboard` |
| Reports | `GET /api/reports/students/{studentId}`, `GET /api/reports/teachers/{teacherId}`, `GET /api/reports/fees/summary` |
| Meetings | `GET/POST /api/meetings`, `GET/PUT/DELETE /api/meetings/{meetingId}` |
| Meeting Actions | `POST /api/meetings/{meetingId}/join`, `POST /api/meetings/{meetingId}/leave`, `POST /api/meetings/{meetingId}/end` |
| Meeting Messages | `GET/POST /api/meetings/{meetingId}/messages` |

## Login Dashboard Shapes

### Admin

```json
{
  "type": "admin",
  "summary": {}
}
```

### Staff

```json
{
  "type": "staff",
  "staff": {},
  "summary": {}
}
```

### Student

```json
{
  "type": "student",
  "student": {},
  "quickStats": {
    "presentDays": 0,
    "absentDays": 0,
    "totalAttendanceRecords": 0,
    "totalFees": "0",
    "paidFees": "0",
    "pendingFeeCount": 0,
    "pendingFeesAmount": "0",
    "marksRecorded": 0
  },
  "recentAttendance": [],
  "recentFees": [],
  "pendingFees": [],
  "recentMarks": []
}
```

### Teacher

```json
{
  "type": "teacher",
  "teacher": {},
  "quickStats": {
    "assignedCourses": 0,
    "assignedSubjects": 0,
    "studentsInAssignedCourses": 0
  },
  "courses": [],
  "subjects": [],
  "studentsByCourse": {}
}
```

## Common Status Codes

| Code | Meaning |
| --- | --- |
| `200` | Successful request |
| `201` | Resource created |
| `204` | Resource deleted successfully |
| `400` | Validation/business rule failure |
| `401` | Missing or invalid authentication |
| `403` | Authenticated but not allowed |
| `404` | Resource not found |
| `500` | Unexpected server error |
