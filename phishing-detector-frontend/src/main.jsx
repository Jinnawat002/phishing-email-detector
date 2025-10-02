import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './theme.css'
import './global.css'
import App from './App.jsx'
import { GoogleOAuthProvider } from '@react-oauth/google';

// 1. ดึงค่า Client ID มาจาก environment variable ของ Vite
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

// 2. (สำคัญ) เพิ่มการตรวจสอบเพื่อให้แน่ใจว่าค่าถูกโหลดมาถูกต้อง
if (!googleClientId) {
  console.error("⚠️ ไม่พบ VITE_GOOGLE_CLIENT_ID กรุณาตรวจสอบไฟล์ .env.local ในโปรเจกต์ Frontend ของคุณ");
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* 3. ตรวจสอบก่อน Render หากไม่มี ID จะแสดงหน้าจอ Error แทน */}
    {googleClientId ? (
      <GoogleOAuthProvider clientId={googleClientId}>
        <App />
      </GoogleOAuthProvider>
    ) : (
      <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px', color: '#c53030', background: '#fed7d7', border: '1px solid #fc8181', borderRadius: '10px', margin: '20px' }}>
        <strong>เกิดข้อผิดพลาด:</strong> ไม่พบ Google Client ID <br/>
        กรุณาตรวจสอบการตั้งค่าในไฟล์ <code>.env.local</code> และ Restart Server
      </div>
    )}
  </StrictMode>,
)