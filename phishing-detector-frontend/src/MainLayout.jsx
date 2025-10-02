// src/MainLayout.jsx

import React, { useState } from 'react'; // 1. Import useState
import { Outlet } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';

// 2. Import CSS ของ Sidebar เพื่อให้สไตล์ของปุ่ม Hamburger และ Overlay ทำงาน
import './components/layout/Sidebar.css';
import './App.css';

const MainLayout = () => {
  // 3. สร้าง State เพื่อควบคุมการเปิด-ปิด Sidebar บนมือถือ
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // 4. สร้างฟังก์ชันสำหรับสลับค่า State (เปิด/ปิด)
  const toggleMobileSidebar = () => {
    setMobileSidebarOpen(!isMobileSidebarOpen);
  };

  return (
    <div className="app-layout">
      {/* 5. ปุ่ม Hamburger และ Overlay (จะแสดงผลเฉพาะบนจอมือถือตาม CSS) */}
      <button 
        className={`mobile-menu-toggle ${isMobileSidebarOpen ? 'active' : ''}`}
        onClick={toggleMobileSidebar}
      >
        <div className="hamburger">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </button>

      {isMobileSidebarOpen && (
        <div 
          className="sidebar-overlay active"
          onClick={toggleMobileSidebar} // คลิกที่พื้นหลังเพื่อปิดเมนูได้
        />
      )}

      {/* 6. ส่ง State และฟังก์ชันควบคุมไปให้ Sidebar */}
      <Sidebar 
        isMobileOpen={isMobileSidebarOpen} 
        toggleMobileSidebar={toggleMobileSidebar}
      /> 
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;