// src/components/FileSummary.js
import React from 'react';
import { useLocation } from 'react-router-dom';
import './FileSummary.css';

const FileSummary = () => {
  const location = useLocation();
  const { imageSrc, summaryText } = location.state || { imageSrc: '', summaryText: 'No summary available.' };

  return (
    <div className="file-summary-container">
      <div className="image-section">
        {imageSrc && <img src={imageSrc} alt="Uploaded Document" />}
      </div>
      <div className="summary-section">
        <p>{summaryText}</p>
      </div>
    </div>
  );
};

export default FileSummary;
