// components/email/EmailChecker.jsx
import React, { useState } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import RiskMeter from './RiskMeter';
import './EmailChecker.css';
import apiClient from '../../api/axiosConfig';

const EmailChecker = () => {
  const [activeTab, setActiveTab] = useState('text');
  const [emailContent, setEmailContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.eml')) {
      setSelectedFile(file);
    } else {
      alert('กรุณาเลือกไฟล์ .eml เท่านั้น');
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setAnalysisResult(null); // เคลียร์ผลลัพธ์เก่าทุกครั้งที่วิเคราะห์ใหม่
    
    try {
      const formData = new FormData();
      if (activeTab === 'text' && emailContent.trim()) {
        formData.append('content', emailContent);
        formData.append('type', 'text');
      } else if (activeTab === 'file' && selectedFile) {
        formData.append('file', selectedFile);
        formData.append('type', 'file');
      } else {
        alert('กรุณากรอกข้อมูลอีเมลหรือเลือกไฟล์');
        setIsAnalyzing(false);
        return;
      }
      
      const response = await apiClient.post('/email/analyze/', formData);
      setAnalysisResult(response.data);

    } catch (error) {
      // Interceptor จะจัดการ 401 error (เด้งไปหน้า login), ที่เหลือคือ error อื่นๆ
      console.error('Analysis error:', error);
      alert('เกิดข้อผิดพลาดในการวิเคราะห์: ' + (error.response?.data?.error || 'ไม่ทราบสาเหตุ'));
    } finally {
      setIsAnalyzing(false);
    }
  };

  // --- ส่วนฟังก์ชัน Helper ไม่มีการเปลี่ยนแปลง ---
  const getRiskLevel = (score) => {
    if (score >= 0.8) return 'สูงมาก';
    if (score >= 0.6) return 'สูง';
    if (score >= 0.4) return 'ปานกลาง';
    if (score >= 0.2) return 'ต่ำ';
    return 'ต่ำมาก';
  };

  const getRiskColor = (score) => {
    if (score >= 0.8) return '#dc2626';
    if (score >= 0.6) return '#ea580c';
    if (score >= 0.4) return '#d97706';
    if (score >= 0.2) return '#65a30d';
    return '#16a34a';
  };

  const getRecommendations = (score) => {
    if (score >= 0.8) return ['ไม่ควรคลิกลิงก์หรือดาวน์โหลดไฟล์แนบ', 'ไม่ควรตอบกลับอีเมลนี้', 'ลบอีเมลนี้ทิ้งทันที', 'รายงานอีเมลนี้ให้กับผู้ดูแลระบบ'];
    if (score >= 0.6) return ['ระวังการคลิกลิงก์ในอีเมลนี้', 'ตรวจสอบผู้ส่งให้แน่ใจ', 'สแกนไฟล์แนบก่อนเปิด', 'ปรึกษาผู้เชี่ยวชาญหากไม่แน่ใจ'];
    if (score >= 0.4) return ['ตรวจสอบผู้ส่งให้แน่ใจ', 'ระวังการให้ข้อมูลส่วนตัว', 'สแกนไฟล์แนบก่อนเปิด'];
    return ['อีเมลนี้น่าจะปลอดภัย', 'แต่ยังคงต้องระวังข้อมูลส่วนตัว', 'ตรวจสอบลิงก์ก่อนคลิก'];
  };

  return (
    <div className="email-checker">
      <div className="page-header">
        <h1>ตรวจสอบอีเมลฟิชชิ่ง</h1>
        <p>วิเคราะห์อีเมลเพื่อตรวจจับการโจมตีแบบฟิชชิ่ง</p>
      </div>

      <div className="checker-container">
        <div className="input-section">
          <div className="tab-buttons">
            <button 
              className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
              onClick={() => setActiveTab('text')}
            >
              <FileText size={20} />
              กรอกข้อความ
            </button>
            <button 
              className={`tab-btn ${activeTab === 'file' ? 'active' : ''}`}
              onClick={() => setActiveTab('file')}
            >
              <Upload size={20} />
              อัปโหลดไฟล์ .eml
            </button>
          </div>

          {activeTab === 'text' && (
            <div className="text-input">
              <label htmlFor="email-content">เนื้อหาอีเมล</label>
              <textarea
                id="email-content"
                value={emailContent}
                onChange={(e) => setEmailContent(e.target.value)}
                placeholder="วางเนื้อหาอีเมลที่ต้องการตรวจสอบที่นี่..."
                rows={10}
              />
            </div>
          )}

          {activeTab === 'file' && (
            <div className="file-input">
              <label htmlFor="email-file">เลือกไฟล์ .eml</label>
              <div className="file-upload-area">
                <input
                  id="email-file"
                  type="file"
                  accept=".eml"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <label htmlFor="email-file" className="file-upload-label">
                  <Upload size={48} />
                  <p>คลิกเพื่อเลือกไฟล์ .eml</p>
                  <span>หรือลากไฟล์มาวางที่นี่</span>
                </label>
                {selectedFile && (
                  <div className="selected-file">
                    <FileText size={20} />
                    <span>{selectedFile.name}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          <button 
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={isAnalyzing || (!emailContent.trim() && !selectedFile)}
          >
            {isAnalyzing ? 'กำลังวิเคราะห์...' : 'ตรวจสอบอีเมล'}
          </button>
        </div>

        {analysisResult && (
          <div className="result-section">
            <div className="result-header">
              <h2>ผลการวิเคราะห์</h2>
            </div>

            <div className="risk-display">
              {/* ใช้ ?. และ ?? เพื่อป้องกัน error ถ้า analysisResult หรือ risk_score ไม่มีค่า */}
              <RiskMeter score={analysisResult?.risk_score ?? 0} />
              
              <div className="risk-info">
                <div className="risk-level">
                  <span>ระดับความเสี่ยง:</span>
                  <span 
                    className="risk-value"
                    style={{ color: getRiskColor(analysisResult?.risk_score ?? 0) }}
                  >
                    {getRiskLevel(analysisResult?.risk_score ?? 0)}
                  </span>
                </div>
                <div className="risk-score">
                  <span>คะแนน:</span>
                  {/* ตรวจสอบก่อนว่า risk_score มีค่าหรือไม่ */}
                  <span>{typeof analysisResult?.risk_score === 'number' ? `${(analysisResult.risk_score * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
              </div>
            </div>

            <div className="recommendations">
              <h3>
                <Info size={20} />
                คำแนะนำ
              </h3>
              <ul>
                {getRecommendations(analysisResult?.risk_score ?? 0).map((rec, index) => (
                  <li key={index}>
                    {(analysisResult?.risk_score ?? 0) >= 0.6 ? (
                      <AlertTriangle size={16} className="warning-icon" />
                    ) : (
                      <CheckCircle size={16} className="info-icon" />
                    )}
                    {rec}
                  </li>
                ))}
              </ul>
            </div>

            {/* ใช้ ?. เพื่อป้องกัน error ถ้า details ไม่มีค่า และเช็คว่ามี key ข้างในหรือไม่ */}
            {analysisResult?.details && Object.keys(analysisResult.details).length > 0 && (
              <div className="analysis-details">
                <h3>รายละเอียดการวิเคราะห์</h3>
                <div className="details-grid">
                  {analysisResult.details.suspicious_keywords && (
                    <div className="detail-item">
                      <label>คำที่น่าสงสัย:</label>
                      <span>{analysisResult.details.suspicious_keywords.join(', ')}</span>
                    </div>
                  )}
                  {analysisResult.details.domain_reputation && (
                    <div className="detail-item">
                      <label>ชื่อเสียงโดเมน:</label>
                      <span>{analysisResult.details.domain_reputation}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailChecker;