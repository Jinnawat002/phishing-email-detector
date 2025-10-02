// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import คอมโพเนนต์ทั้งหมด
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import MainLayout from './MainLayout';
import Dashboard from './components/dashboard/Dashboard';
import EmailChecker from './components/email/EmailChecker';
import EmailHistory from './components/email/EmailHistory';
import SystemEvaluation from './components/evaluation/SystemEvaluation';
import Profile from './components/profile/Profile';

// ProtectedRoute - คอมโพเนนต์สำหรับตรวจสอบ Token
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('authToken');
  if (!token) {
    // ถ้าไม่มี Token, ส่งกลับไปหน้า Login ทันที
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* --- 1. Public Routes --- */}
        {/* Route สำหรับหน้าที่ใครก็เข้าได้ */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* --- 2. Protected Routes --- */}
        {/* ใช้ Route แบบไม่มี path (Pathless Route) เพื่อเป็น Layout Wrapper */}
        {/* มันจะตรวจสอบสิทธิ์ก่อน ถ้าผ่านถึงจะให้ render children (Outlet) ได้ */}
        <Route 
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Route ลูกทั้งหมดนี้จะถูกแสดงผลใน <Outlet /> ของ MainLayout */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/email-checker" element={<EmailChecker />} />
          <Route path="/email-history" element={<EmailHistory />} />
          <Route path="/evaluation" element={<SystemEvaluation />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        
        {/* --- 3. Default Redirect --- */}
        {/* ถ้าผู้ใช้เข้ามาที่ path "/" ให้ redirect ไปที่ /dashboard โดยอัตโนมัติ */}
        {/* ProtectedRoute ข้างบนจะทำงานก่อน ถ้ายังไม่ login ก็จะถูกส่งไป /login อยู่ดี */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

      </Routes>
    </Router>
  );
}

export default App;