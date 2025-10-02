import React from 'react';
import './RiskMeter.css';

const RiskMeter = ({ score }) => {
  const percentage = Math.round(score * 100);
  
  const getColor = (score) => {
    if (score >= 0.8) return '#dc2626'; // Red
    if (score >= 0.6) return '#ea580c'; // Orange-red
    if (score >= 0.4) return '#d97706'; // Orange
    if (score >= 0.2) return '#65a30d'; // Yellow-green
    return '#16a34a'; // Green
  };

  const getGradient = (score) => {
    const color = getColor(score);
    return `linear-gradient(90deg, ${color} 0%, ${color}88 50%, ${color}44 100%)`;
  };

  return (
    <div className="risk-meter">
      <div className="meter-container">
        <div className="meter-background">
          <div className="meter-segments">
            <div className="segment very-low"></div>
            <div className="segment low"></div>
            <div className="segment medium"></div>
            <div className="segment high"></div>
            <div className="segment very-high"></div>
          </div>
          <div 
            className="meter-fill"
            style={{ 
              width: `${percentage}%`,
              background: getGradient(score)
            }}
          ></div>
          <div 
            className="meter-indicator"
            style={{ left: `${percentage}%` }}
          ></div>
        </div>
        
        <div className="meter-labels">
          <span>ปลอดภัย</span>
          <span>ต่ำ</span>
          <span>ปานกลาง</span>
          <span>สูง</span>
          <span>อันตราย</span>
        </div>
      </div>
      
      <div className="meter-display">
        <div className="score-circle" style={{ borderColor: getColor(score) }}>
          <span className="score-text">{percentage}%</span>
        </div>
      </div>
    </div>
  );
};

export default RiskMeter;