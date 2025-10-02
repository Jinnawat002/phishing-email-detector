import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Shield } from 'lucide-react';
import './Auth.css';
import { useGoogleLogin } from '@react-oauth/google';
import apiClient from '../../api/axiosConfig';

const Login = () => { 
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLoginSuccess = (data) => {
    const { access, refresh } = data;
    if (access) localStorage.setItem('authToken', access);
    if (refresh) localStorage.setItem('refreshToken', refresh);
    navigate('/dashboard');
  };

  // --- ★★★ คืนโค้ด handleSubmit กลับเป็นเวอร์ชันที่สะอาด ★★★ ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // ใช้ apiClient และระบุแค่ endpoint
      const response = await apiClient.post('/token/', {
        username: formData.email, // Django Simple JWT ใช้ username
        password: formData.password
      });
      
      // เรียกใช้ฟังก์ชันกลางเมื่อสำเร็จ
      handleLoginSuccess(response.data);

    } catch (err) {
      console.error("Login error:", err); // เก็บ console.error ไว้ดูตอน dev ได้
      setError(err.response?.data?.detail || 'อีเมลหรือรหัสผ่านไม่ถูกต้อง');
    } finally {
      setLoading(false);
    }
  };
  
  const handleGoogleLoginSuccess = async (googleResponse) => {
    setLoading(true);
    setError('');
    try {
      const backendResponse = await apiClient.post('/auth/google/', {
        access_token: googleResponse.access_token,
      });
      handleLoginSuccess(backendResponse.data);
    } catch (err) {
      console.error("Google Login error:", err);
      setError(err.response?.data?.error_description || 'เกิดข้อผิดพลาดในการล็อกอินด้วย Google');
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

  // --- ส่วน JSX ไม่มีการเปลี่ยนแปลง ---
  return (
    <div className="auth-container">
        <div className="auth-background">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="auth-icon">
                        <Shield size={40} className="text-blue-600" />
                    </div>
                    <h2>เข้าสู่ระบบ</h2>
                    <p>ระบบตรวจจับอีเมลฟิชชิ่งอัจฉริยะ</p>
                </div>
                <form onSubmit={handleSubmit} className="auth-form">
                  {error && <div className="error-message">{error}</div>}
                  <div className="form-group">
                    <label htmlFor="email">อีเมล</label>
                    <div className="input-wrapper">
                      <Mail size={20} className="input-icon" />
                      <input
                        id="email"
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="กรอกอีเมลของคุณ"
                        required
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label htmlFor="password">รหัสผ่าน</label>
                    <div className="input-wrapper">
                      <Lock size={20} className="input-icon" />
                      <input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="กรอกรหัสผ่านของคุณ"
                        required
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                  </div>
                  <button 
                    type="submit" 
                    className="auth-button"
                    disabled={loading}
                  >
                    {loading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ'}
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
                  <svg className="google-icon" width="20" height="20" viewBox="0 0 18 18">
                    <path fill="#4285F4" d="M17.64 9.20455c0-.63864-.05727-1.25182-.16818-1.84091H9.18182v3.48182h4.79091c-.20682 1.125-.84273 2.07818-1.79636 2.71636v2.25818h2.90818c1.70182-1.56636 2.68409-3.87409 2.68409-6.61545z"></path>
                    <path fill="#34A853" d="M9.18182 18c2.43 0 4.46727-.80545 5.95727-2.18182l-2.90818-2.25818c-.80545.54273-1.83364.86182-2.96227.86182-2.27364 0-4.20727-1.53455-4.9-3.58227H1.34182v2.33182C2.82182 16.3377 5.76 18 9.18182 18z"></path>
                    <path fill="#FBBC05" d="M4.28182 10.7345C4.09 10.2159 3.98182 9.65455 3.98182 9c0-.65455.10818-1.21591.28727-1.73455V4.93182H1.34182C.50545 6.45 0 7.68182 0 9c0 1.31818.50545 2.55 1.34182 4.06818l2.94-2.33363z"></path>
                    <path fill="#EA4335" d="M9.18182 3.54545c1.32182 0 2.50727.45545 3.44 1.34545l2.58182-2.58182C13.6455.955909 11.6182 0 9.18182 0 5.76 0 2.82182 1.66227 1.34182 4.06818l2.94 2.33182c.69273-2.04773 2.62636-3.58227 4.9-3.58227z"></path>
                  </svg>
                  เข้าสู่ระบบด้วย Google
                </button>
                <div className="auth-footer">
                  <p>
                    ยังไม่มีบัญชี? 
                    <Link to="/register" className="auth-link">
                      ลงทะเบียนที่นี่
                    </Link>
                  </p>
                </div>
            </div>
        </div>
    </div>
  );
};

export default Login;