// components/evaluation/SystemEvaluation.jsx
import React, { useState } from 'react';
import { Star, Send, CheckCircle } from 'lucide-react';
import './SystemEvaluation.css';

// 1. Import apiClient
import apiClient from '../../api/axiosConfig';

const SystemEvaluation = () => {
  const [evaluation, setEvaluation] = useState({
    accuracy: 0,
    usability: 0,
    speed: 0,
    reliability: 0,
    overall: 0,
    comments: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const handleRatingChange = (category, rating) => {
    setEvaluation({ ...evaluation, [category]: rating });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 2. ใช้ apiClient.post โดยตรง ไม่ต้องเช็ค token หรือใส่ header
      await apiClient.post('/evaluation/submit/', evaluation);
      setSubmitted(true);
    } catch (error) {
      // 3. Interceptor จะจัดการ 401 error, ที่เหลือคือ error อื่นๆ
      console.error('Evaluation submission error:', error);
      alert('เกิดข้อผิดพลาดในการส่งการประเมิน: ' + (error.response?.data?.error || 'กรุณาลองใหม่อีกครั้ง'));
    } finally {
      setLoading(false);
    }
  };

  const StarRating = ({ category, label, value }) => {
    return (
      <div className="rating-item">
        <label>{label}</label>
        <div className="stars">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className={`star ${star <= value ? 'filled' : ''}`}
              onClick={() => handleRatingChange(category, star)}
            >
              <Star size={24} fill={star <= value ? '#fbbf24' : 'none'} />
            </button>
          ))}
        </div>
        <span className="rating-text">
          {value === 0 ? 'ยังไม่ได้ประเมิน' : 
           value === 1 ? 'น้อยมาก' :
           value === 2 ? 'น้อย' :
           value === 3 ? 'ปานกลาง' :
           value === 4 ? 'ดี' : 'ดีมาก'}
        </span>
      </div>
    );
  };

  if (submitted) {
    return (
      <div className="evaluation-success">
        <CheckCircle size={64} className="success-icon" />
        <h2>ขอบคุณสำหรับการประเมิน!</h2>
        <p>ความคิดเห็นของคุณจะช่วยให้เราปรับปรุงระบบให้ดียิ่งขึ้น</p>
      </div>
    );
  }

  return (
    <div className="system-evaluation">
      <div className="evaluation-header">
        <h1>ประเมินการใช้งานระบบ</h1>
        <p>โปรดให้คะแนนและความคิดเห็นเพื่อช่วยปรับปรุงระบบ</p>
      </div>

      <form onSubmit={handleSubmit} className="evaluation-form">
        <div className="rating-section">
          <h3>ประเมินประสิทธิภาพระบบ</h3>
          
          <StarRating 
            category="accuracy"
            label="ความแม่นยำในการตรวจจับ"
            value={evaluation.accuracy}
          />
          
          <StarRating 
            category="usability"
            label="ความสะดวกในการใช้งาน"
            value={evaluation.usability}
          />
          
          <StarRating 
            category="speed"
            label="ความเร็วในการวิเคราะห์"
            value={evaluation.speed}
          />
          
          <StarRating 
            category="reliability"
            label="ความน่าเชื่อถือของระบบ"
            value={evaluation.reliability}
          />
          
          <StarRating 
            category="overall"
            label="ความพึงพอใจโดยรวม"
            value={evaluation.overall}
          />
        </div>

        <div className="comments-section">
          <h3>ความคิดเห็นเพิ่มเติม</h3>
          <textarea
            value={evaluation.comments}
            onChange={(e) => setEvaluation({...evaluation, comments: e.target.value})}
            placeholder="แชร์ประสบการณ์การใช้งาน ข้อเสนอแนะ หรือปัญหาที่พบ..."
            rows={5}
          />
        </div>

        <button 
          type="submit" 
          className="submit-btn"
          disabled={loading || Object.values(evaluation).slice(0, 5).every(v => v === 0)}
        >
          <Send size={20} />
          {loading ? 'กำลังส่ง...' : 'ส่งการประเมิน'}
        </button>
      </form>
    </div>
  );
};

export default SystemEvaluation;
