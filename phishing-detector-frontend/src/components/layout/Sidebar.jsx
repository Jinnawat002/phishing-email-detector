// src/components/layout/Sidebar.jsx

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { Home, Mail, User, Clock, Star, LogOut, Shield, ChevronLeft, ChevronRight, X } from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ isMobileOpen, toggleMobileSidebar }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userEmail, setUserEmail] = useState('ผู้ใช้งาน');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        setUserEmail(decodedToken.email || 'ผู้ใช้งาน');
      } catch (error) { 
        console.error("Invalid token:", error); 
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    navigate('/login');
  };

  const menuItems = [
    { id: 'dashboard', path: '/dashboard', icon: Home, label: 'หน้าหลัก' },
    { id: 'email-checker', path: '/email-checker', icon: Mail, label: 'ตรวจสอบอีเมล' },
    { id: 'profile', path: '/profile', icon: User, label: 'โปรไฟล์' },
    { id: 'email-history', path: '/email-history', icon: Clock, label: 'ประวัติ' },
    { id: 'evaluation', path: '/evaluation', icon: Star, label: 'ประเมินระบบ' }
  ];

  const handleLinkClick = () => {
    if (isMobileOpen) {
      toggleMobileSidebar();
    }
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''} ${isMobileOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Shield size={24} />
          </div>
          {!isCollapsed && (
            <div className="brand-text">
              <h3>Phishing Detector</h3>
              <span>Version 1.0</span>
            </div>
          )}
        </div>
        
        {/* ปุ่ม Toggle สำหรับ Desktop (ซ่อนในมือถือ) */}
        <button 
          className="sidebar-toggle" 
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
        
        {/* ปุ่มปิดสำหรับมือถือ (ซ่อนในเดสก์ท็อป) */}
        {/* <button 
          className="sidebar-close-btn" 
          onClick={toggleMobileSidebar}
        >
          <X size={20} />
        </button> */}
      </div>

      <div className="sidebar-user">
        <div className="user-avatar">
          {userEmail.charAt(0).toUpperCase()}
        </div>
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
                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                title={isCollapsed ? item.label : ''}
                onClick={handleLinkClick}
              >
                <div className="nav-icon">
                  <item.icon size={20} />
                </div>
                {!isCollapsed && <span className="nav-label">{item.label}</span>}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <button 
          className="logout-btn" 
          onClick={handleLogout} 
          title={isCollapsed ? 'ออกจากระบบ' : ''}
        >
          <LogOut size={20} />
          {!isCollapsed && <span>ออกจากระบบ</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;