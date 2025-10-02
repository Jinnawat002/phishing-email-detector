// components/auth/Register.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Shield } from 'lucide-react';
import './Auth.css';
import { useGoogleLogin } from '@react-oauth/google';

// 1. Import apiClient
import apiClient from '../../api/axiosConfig';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  // 2. (Optional) สร้างฟังก์ชันกลางสำหรับ Google Login (เหมือนในหน้า Login)
  const handleLoginSuccess = (data) => {
    const { access, refresh } = data;
    if (access) localStorage.setItem('authToken', access);
    if (refresh) localStorage.setItem('refreshToken', refresh);
    navigate('/dashboard');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    if (formData.password !== formData.confirmPassword) {
      setError('รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน');
      setLoading(false);
      return;
    }

    try {
      // 3. เปลี่ยนมาใช้ apiClient
      await apiClient.post('/register/', {
        email: formData.email,
        password: formData.password,
      });

      setSuccessMessage('ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ');
      setTimeout(() => {
        navigate('/login');
      }, 2000);

    } catch (err) {
      const errorMsg = err.response?.data?.email?.[0] || err.response?.data?.error || 'อีเมลนี้อาจถูกใช้งานแล้ว หรือเกิดข้อผิดพลาด';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLoginSuccess = async (googleResponse) => {
    setLoading(true);
    setError('');
    try {
      // 4. เปลี่ยนมาใช้ apiClient
      const backendResponse = await apiClient.post('/auth/google/', {
        access_token: googleResponse.access_token,
      });
      // เรียกใช้ฟังก์ชันกลางเพื่อจัดการ token และ redirect
      handleLoginSuccess(backendResponse.data);

    } catch (err) {
      console.error("Google Login/Register error:", err);
      setError(err.response?.data?.error_description || 'เกิดข้อผิดพลาดในการลงทะเบียนด้วย Google');
    } finally {
      setLoading(false);
    }
  };

  const googleLogin = useGoogleLogin({
    onSuccess: handleGoogleLoginSuccess,
    onError: (error) => console.error('Google Login Failed:', error),
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  
  // --- 3. ปรับปรุง UI ทั้งหมดให้เหมือนหน้า Login ---
  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-icon">
              <Shield size={40} className="text-blue-600" />
            </div>
            <h2>ลงทะเบียน</h2>
            <p>สร้างบัญชีใหม่สำหรับระบบตรวจจับอีเมลฟิชชิ่ง</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {error && <div className="error-message">{error}</div>}
            {successMessage && <div className="success-message">{successMessage}</div>}
            
            <div className="form-group">
              <label htmlFor="email">อีเมล</label>
              <div className="input-wrapper">
                <Mail size={20} className="input-icon" />
                <input id="email" type="email" name="email" value={formData.email} onChange={handleChange} placeholder="กรอกอีเมลของคุณ" required />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">รหัสผ่าน</label>
              <div className="input-wrapper">
                <Lock size={20} className="input-icon" />
                <input id="password" type={showPassword ? 'text' : 'password'} name="password" value={formData.password} onChange={handleChange} placeholder="กรอกรหัสผ่าน" required />
                <button type="button" className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">ยืนยันรหัสผ่าน</label>
              <div className="input-wrapper">
                <Lock size={20} className="input-icon" />
                <input id="confirmPassword" type={showConfirmPassword ? 'text' : 'password'} name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} placeholder="ยืนยันรหัสผ่านอีกครั้ง" required />
                <button type="button" className="password-toggle" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? 'กำลังลงทะเบียน...' : 'สร้างบัญชี'}
            </button>
          </form>

          <div className="divider">
            <span>หรือ</span>
          </div>

          <button 
            onClick={() => googleLogin()}
            className="google-auth-button"
            disabled={loading}
          >
            <svg className="google-icon" width="20" height="20" viewBox="0 0 18 18"><path fill="#4285F4" d="M17.64 9.20455c0-.63864-.05727-1.25182-.16818-1.84091H9.18182v3.48182h4.79091c-.20682 1.125-.84273 2.07818-1.79636 2.71636v2.25818h2.90818c1.70182-1.56636 2.68409-3.87409 2.68409-6.61545z"></path><path fill="#34A853" d="M9.18182 18c2.43 0 4.46727-.80545 5.95727-2.18182l-2.90818-2.25818c-.80545.54273-1.83364.86182-2.96227.86182-2.27364 0-4.20727-1.53455-4.9-3.58227H1.34182v2.33182C2.82182 16.3377 5.76 18 9.18182 18z"></path><path fill="#FBBC05" d="M4.28182 10.7345C4.09 10.2159 3.98182 9.65455 3.98182 9c0-.65455.10818-1.21591.28727-1.73455V4.93182H1.34182C.50545 6.45 0 7.68182 0 9c0 1.31818.50545 2.55 1.34182 4.06818l2.94-2.33363z"></path><path fill="#EA4335" d="M9.18182 3.54545c1.32182 0 2.50727.45545 3.44 1.34545l2.58182-2.58182C13.6455.955909 11.6182 0 9.18182 0 5.76 0 2.82182 1.66227 1.34182 4.06818l2.94 2.33182c.69273-2.04773 2.62636-3.58227 4.9-3.58227z"></path></svg>
            ลงทะเบียนด้วย Google
          </button>
          
          <div className="auth-footer">
            <p>
              มีบัญชีผู้ใช้อยู่แล้ว? 
              <Link to="/login" className="auth-link">
                เข้าสู่ระบบที่นี่
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;