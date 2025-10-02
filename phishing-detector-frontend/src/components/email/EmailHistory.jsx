// components/email/EmailHistory.jsx
import React, { useState, useEffect } from 'react';
import { Clock, Mail, AlertTriangle, CheckCircle, Search, Filter } from 'lucide-react';
import './EmailHistory.css';

// 1. Import apiClient
import apiClient from '../../api/axiosConfig';

const EmailHistory = () => {
  const [emailHistory, setEmailHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    const fetchEmailHistory = async () => {
      setLoading(true);
      try {
        // 2. ใช้ apiClient.get ตรงๆ ได้เลย
        const response = await apiClient.get('/email/history/');
        
        const data = response.data;
        if (Array.isArray(data)) {
          setEmailHistory(data);
        } else if (data.history && Array.isArray(data.history)) {
          setEmailHistory(data.history);
        } else {
          throw new Error('รูปแบบข้อมูลไม่ถูกต้อง');
        }
      } catch (error) {
        // 3. Interceptor จัดการ 401 error ให้แล้ว
        console.error('Error fetching email history:', error);
        setError('เกิดข้อผิดพลาดในการโหลดข้อมูล');
      } finally {
        setLoading(false);
      }
    };

    fetchEmailHistory();
  }, []); // ไม่ต้องมี navigate

  const getRiskLevel = (score) => {
    if (score >= 0.8) return { level: 'สูงมาก', color: '#dc2626' };
    if (score >= 0.6) return { level: 'สูง', color: '#ea580c' };
    if (score >= 0.4) return { level: 'ปานกลาง', color: '#d97706' };
    if (score >= 0.2) return { level: 'ต่ำ', color: '#65a30d' };
    return { level: 'ปลอดภัย', color: '#16a34a' };
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'ไม่ทราบวันที่';
    }
  };

  const filteredHistory = emailHistory.filter(email => {
    const matchesSearch = email.content && email.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || 
      (filterStatus === 'safe' && email.risk_score < 0.4) ||
      (filterStatus === 'risky' && email.risk_score >= 0.4);
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="email-history">
        <div className="history-header">
          <h1>กำลังโหลดข้อมูล...</h1>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="email-history">
        <div className="history-header">
          <h1>เกิดข้อผิดพลาด</h1>
          <p style={{ color: 'red' }}>{error}</p>
          <button onClick={() => window.location.reload()}>ลองใหม่</button>
        </div>
      </div>
    );
  }

  return (
    <div className="email-history">
      <div className="history-header">
        <h1>ประวัติการตรวจสอบอีเมล</h1>
        <p>รายการอีเมลที่เคยตรวจสอบทั้งหมด</p>
      </div>

      <div className="history-controls">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="ค้นหาในเนื้อหาอีเมล..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="filter-box">
          <Filter size={20} />
          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">ทั้งหมด</option>
            <option value="safe">ปลอดภัย</option>
            <option value="risky">มีความเสี่ยง</option>
          </select>
        </div>
      </div>

      <div className="history-list">
        {filteredHistory.length === 0 ? (
          <div className="no-data">
            <Mail size={48} />
            <h3>ไม่พบข้อมูล</h3>
            <p>
              {searchTerm || filterStatus !== 'all' 
                ? 'ไม่พบข้อมูลที่ตรงกับการค้นหา' 
                : 'ยังไม่มีประวัติการตรวจสอบอีเมล'
              }
            </p>
            {(searchTerm || filterStatus !== 'all') && (
              <button onClick={() => {
                setSearchTerm('');
                setFilterStatus('all');
              }}>
                ล้างตัวกรอง
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="results-count">
              แสดง {filteredHistory.length} จาก {emailHistory.length} รายการ
            </div>
            {filteredHistory.map((email) => {
              const risk = getRiskLevel(email.risk_score);
              return (
                <div key={email.id} className="history-item">
                  <div className="item-header">
                    <div className="risk-indicator" style={{ background: risk.color }}>
                      {email.risk_score >= 0.4 ? 
                        <AlertTriangle size={16} /> : 
                        <CheckCircle size={16} />
                      }
                    </div>
                    <div className="item-info">
                      <div className="risk-level" style={{ color: risk.color }}>
                        {risk.level} ({Math.round(email.risk_score * 100)}%)
                      </div>
                      <div className="analyze-date">
                        <Clock size={14} />
                        {formatDate(email.analyzed_at)}
                      </div>
                    </div>
                  </div>
                  <div className="item-content">
                    <p>{email.content && email.content.length > 200 ? 
                      email.content.substring(0, 200) + '...' : 
                      email.content || 'ไม่มีเนื้อหา'
                    }</p>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
};

export default EmailHistory;