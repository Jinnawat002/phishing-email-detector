// components/dashboard/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Mail, Shield, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import './Dashboard.css';

// 1. Import apiClient
import apiClient from '../../api/axiosConfig';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalEmails: 0,
    phishingDetected: 0,
    safeEmails: 0,
    accuracy: 0
  });

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        // 2. ใช้ apiClient.get โดยไม่ต้องใส่ header หรือ URL เต็มๆ
        const response = await apiClient.get('/dashboard/stats/');
        setStats(response.data);
      } catch (error) {
        // 3. ไม่ต้องจัดการ 401 error เองแล้ว เพราะ Interceptor จัดการให้
        console.error('Error fetching stats:', error);
        // อาจจะตั้งค่า error state เพื่อแสดงข้อความบางอย่างก็ได้
      }
    };

    fetchDashboardStats();
  }, []); // ไม่ต้องมี navigate ใน dependency array แล้ว

  const statCards = [
    {
      title: 'อีเมลทั้งหมด',
      value: stats.totalEmails,
      icon: Mail,
      color: '#3b82f6',
      bgColor: 'rgba(59, 130, 246, 0.1)'
    },
    {
      title: 'ตรวจพบฟิชชิ่ง',
      value: stats.phishingDetected,
      icon: AlertTriangle,
      color: '#ef4444',
      bgColor: 'rgba(239, 68, 68, 0.1)'
    },
    {
      title: 'อีเมลปลอดภัย',
      value: stats.safeEmails,
      icon: CheckCircle,
      color: '#10b981',
      bgColor: 'rgba(16, 185, 129, 0.1)'
    },
    {
      title: 'ความแม่นยำ',
      value: `${stats.accuracy}%`,
      icon: TrendingUp,
      color: '#8b5cf6',
      bgColor: 'rgba(139, 92, 246, 0.1)'
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>แดชบอร์ด</h1>
        <p>ภาพรวมการตรวจจับอีเมลฟิชชิ่ง</p>
      </div>

      <div className="stats-grid">
        {statCards.map((card, index) => (
          <div key={index} className="stat-card" style={{ background: card.bgColor }}>
            <div className="stat-icon" style={{ color: card.color }}>
              <card.icon size={32} />
            </div>
            <div className="stat-info">
              <h3>{card.value}</h3>
              <p>{card.title}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-content">
        <div className="welcome-section">
          <div className="welcome-card">
            <Shield size={48} className="welcome-icon" />
            <h2>ยินดีต้อนรับสู่ระบบตรวจจับอีเมลฟิชชิ่งอัจฉริยะ</h2>
            <p>ระบบของเราใช้เทคโนโลยี AI เพื่อช่วยป้องกันคุณจากการโจมตีแบบฟิชชิ่ง</p>
            <div className="feature-list">
              <div className="feature-item">
                <CheckCircle size={20} />
                <span>ตรวจจับอีเมลฟิชชิ่งด้วย AI</span>
              </div>
              <div className="feature-item">
                <CheckCircle size={20} />
                <span>วิเคราะห์ความเสี่ยงแบบเรียลไทม์</span>
              </div>
              <div className="feature-item">
                <CheckCircle size={20} />
                <span>คำแนะนำในการป้องกัน</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;