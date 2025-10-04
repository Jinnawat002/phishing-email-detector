// src/components/layout/Sidebar.jsx (ฉบับแก้ไข)

import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import {
  Home,
  Mail,
  User,
  Clock,
  Star,
  LogOut,
  Shield,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";
import "./Sidebar.css";

// 1. รับ props isMobileOpen และ toggleMobileSidebar เข้ามา
const Sidebar = ({ isMobileOpen, toggleMobileSidebar }) => {
  // isCollapsed สำหรับ Desktop ยังคงทำงานเหมือนเดิม
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userEmail, setUserEmail] = useState("ผู้ใช้งาน");
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        setUserEmail(decodedToken.email || "ผู้ใช้งาน");
      } catch (error) {
        console.error("Invalid token:", error);
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    navigate("/login");
  };

  const menuItems = [
    { id: "dashboard", path: "/dashboard", icon: Home, label: "หน้าหลัก" },
    {
      id: "email-checker",
      path: "/email-checker",
      icon: Mail,
      label: "ตรวจสอบอีเมล",
    },
    { id: "profile", path: "/profile", icon: User, label: "โปรไฟล์" },
    {
      id: "email-history",
      path: "/email-history",
      icon: Clock,
      label: "ประวัติ",
    },
    { id: "evaluation", path: "/evaluation", icon: Star, label: "ประเมินระบบ" },
  ];

  // 2. สร้างฟังก์ชันสำหรับปิดเมนูมือถือเมื่อคลิกที่ Link
  const handleLinkClick = () => {
    if (isMobileOpen) {
      toggleMobileSidebar();
    }
  };

  return (
    // 3. เพิ่ม class 'open' ตาม State ของ isMobileOpen
    <aside
      className={`sidebar ${isCollapsed ? "collapsed" : ""} ${
        isMobileOpen ? "open" : ""
      }`}
    >
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Shield size={24} />
          </div>
          {/* เงื่อนไขแสดงผลข้อความยังคงเหมือนเดิม */}
          {!isCollapsed && (
            <div className="brand-text">
              <h3>Phishing Detector</h3>
              <span>Version 1.0</span>
            </div>
          )}
        </div>

        {/* 1. เพิ่มปุ่มปิดสำหรับ Mobile ที่นี่ */}
        {/* ปุ่มนี้จะถูกแสดง/ซ่อนด้วย CSS ที่เราทำไว้ก่อนหน้า */}
        <button className="sidebar-close-btn" onClick={toggleMobileSidebar}>
          <X size={22} /> {/* อย่าลืม import X จาก lucide-react */}
        </button>

        {/* 2. ปุ่มสลับสำหรับ Desktop ยังคงอยู่เหมือนเดิม */}
        <button
          className="sidebar-toggle"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <div className="sidebar-user">
        <div className="user-avatar">{userEmail.charAt(0).toUpperCase()}</div>
        {!isCollapsed && (
          <div className="user-info">
            <h4>{userEmail}</h4>
            <span>สมาชิกทั่วไป</span>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        <ul>
          {menuItems.map((item) => (
            <li key={item.id}>
              <Link
                to={item.path}
                className={`nav-item ${
                  location.pathname === item.path ? "active" : ""
                }`}
                title={isCollapsed ? item.label : ""}
                onClick={handleLinkClick} // 5. เพิ่ม onClick เพื่อปิดเมนู
              >
                <div className="nav-icon">
                  <item.icon size={20} />
                </div>
                {!isCollapsed && (
                  <span className="nav-label">{item.label}</span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <button
          className="logout-btn"
          onClick={handleLogout}
          title={isCollapsed ? "ออกจากระบบ" : ""}
        >
          <LogOut size={20} />
          {!isCollapsed && <span>ออกจากระบบ</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
