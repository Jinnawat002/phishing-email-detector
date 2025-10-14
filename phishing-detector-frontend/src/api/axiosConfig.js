import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // แม้จะใช้ตรงๆ ไม่ได้ แต่เป็นแนวคิด

// ฟังก์ชันสำหรับเคลียร์ session และ redirect (จะถูกเรียกใช้จาก interceptor)
const clearAuthAndRedirect = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('refreshToken');
  // ใช้ window.location เพราะเราอยู่นอก React component context
  window.location.href = '/login'; 
};

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// ★★★ Interceptor: ก่อนที่ Request จะถูกส่ง ★★★
// ทำหน้าที่แนบ Token ไปกับทุก Request ที่ต้องมีการยืนยันตัวตน
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // ถ้ามี token, ให้เพิ่ม Authorization header
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ★★★ Interceptor: หลังจากที่ได้รับ Response กลับมา ★★★
// ทำหน้าที่จัดการกับ Error, โดยเฉพาะเมื่อ Token หมดอายุ (401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => {
    // ถ้า Response ปกติ ก็ส่งต่อไปเลย
    return response;
  },
  (error) => {
    // ถ้ามี error เกิดขึ้น
    if (error.response && error.response.status === 401) {
      // ถ้าเป็น 401 Unauthorized (Token ไม่ถูกต้อง หรือหมดอายุ)
      console.error("Authentication Error: Token might be expired or invalid.");
      clearAuthAndRedirect(); // เรียกฟังก์ชันเพื่อลบ token และกลับไปหน้า login
    }
    // ส่ง error ต่อไปเพื่อให้ .catch() ใน component จัดการได้
    return Promise.reject(error);
  }
);

export default apiClient;