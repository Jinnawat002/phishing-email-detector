// components/profile/Profile.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { User, Mail, Lock, Save } from 'lucide-react';
import './Profile.css';

// 1. Import apiClient
import apiClient from '../../api/axiosConfig';

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        setFormData(prev => ({ ...prev, email: decodedToken.email || '' }));
      } catch (error) {
        console.error("Invalid token:", error);
        localStorage.removeItem('authToken'); // ลบ token ที่ไม่ถูกต้อง
        navigate('/login');
      }
    } else {
      navigate('/login');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      setMessage('รหัสผ่านใหม่ไม่ตรงกัน');
      setLoading(false);
      return;
    }

    try {
      // 2. ใช้ apiClient.put โดยไม่ต้องใส่ header
      const response = await apiClient.put('/profile/update/', formData);

      setMessage('อัปเดตข้อมูลสำเร็จ');
      setIsEditing(false);
      // เคลียร์ค่า password field หลังอัปเดตสำเร็จ
      setFormData(prev => ({ ...prev, currentPassword: '', newPassword: '', confirmPassword: '' }));
      
    } catch (error) {
      // 3. Interceptor จัดการ 401 error, ที่เหลือคือ error อื่นๆ (เช่น รหัสผ่านปัจจุบันผิด)
      console.error('Profile update error:', error);
      setMessage(error.response?.data?.error || 'เกิดข้อผิดพลาดในการอัปเดตข้อมูล');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile">
      <div className="profile-header">
        <h1>โปรไฟล์ผู้ใช้</h1>
        <p>จัดการข้อมูลส่วนตัวของคุณ</p>
      </div>

      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            <User size={48} />
          </div>
          
          <form onSubmit={handleSubmit} className="profile-form">
            {message && (
              <div className={`message ${message.includes('สำเร็จ') ? 'success' : 'error'}`}>
                {message}
              </div>
            )}

            <div className="form-section">
              <h3>ข้อมูลบัญชี</h3>
              <div className="form-group">
                <label>อีเมล</label>
                <div className="input-wrapper">
                  <Mail size={20} />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    disabled={!isEditing}
                    required
                  />
                </div>
              </div>
            </div>

            {isEditing && (
              <div className="form-section">
                <h3>เปลี่ยนรหัสผ่าน</h3>
                <div className="form-group">
                  <label>รหัสผ่านปัจจุบัน</label>
                  <div className="input-wrapper">
                    <Lock size={20} />
                    <input
                      type="password"
                      value={formData.currentPassword}
                      onChange={(e) => setFormData({...formData, currentPassword: e.target.value})}
                      placeholder="กรอกรหัสผ่านปัจจุบัน"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>รหัสผ่านใหม่</label>
                  <div className="input-wrapper">
                    <Lock size={20} />
                    <input
                      type="password"
                      value={formData.newPassword}
                      onChange={(e) => setFormData({...formData, newPassword: e.target.value})}
                      placeholder="กรอกรหัสผ่านใหม่"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>ยืนยันรหัสผ่านใหม่</label>
                  <div className="input-wrapper">
                    <Lock size={20} />
                    <input
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                      placeholder="ยืนยันรหัสผ่านใหม่"
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="form-actions">
              {!isEditing ? (
                <button type="button" onClick={() => setIsEditing(true)} className="edit-btn">
                  แก้ไขข้อมูล
                </button>
              ) : (
                <div className="action-buttons">
                  <button type="button" onClick={() => {
                    setIsEditing(false);
                    setFormData({...formData, currentPassword: '', newPassword: '', confirmPassword: ''});
                  }} className="cancel-btn">
                    ยกเลิก
                  </button>
                  <button type="submit" disabled={loading} className="save-btn">
                    <Save size={20} />
                    {loading ? 'กำลังบันทึก...' : 'บันทึก'}
                  </button>
                </div>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;