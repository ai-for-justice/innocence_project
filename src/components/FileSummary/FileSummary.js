import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import PDFViewer from './PDFViewer';
import './FileSummary.css';

const FileSummary = () => {
  const location = useLocation();
  const { fileUrl, fileType } = location.state || {};
  const [responseData, setResponseData] = useState({});

  useEffect(() => {
    // Replace 'http://localhost:5000/upload' with the actual data-fetching endpoint
    fetch('http://localhost:5000/upload')
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => setResponseData(data))
      .catch(error => console.error("Fetch error: ", error));
  }, []);

  const isPdf = fileType === 'pdf';
  const fileSrc = fileUrl;

  // Use responseData to dynamically populate these values
  const leftBoxContent = responseData ? `${responseData.backgroundQ}\n\n${responseData.is_missinginfo_Q}\n\nEvaluation Results: ${responseData.evaluation}` : "";
  const rightBoxContent = responseData ? `${responseData.background}\n\n${responseData.is_missinginfo_A}\n\nConclusion: ${responseData.conclusion}\n\nNext Steps: ${responseData.next_steps}` : "";

  return (
    <div className="file-summary-container">
      <div className="file-display-section">
        {isPdf ? (
          <PDFViewer fileSrc={fileSrc} />
        ) : (
          <img src={fileSrc} alt="Uploaded Document" className="image-display" />
        )}
      </div>
      <div className="summary-section">
        <textarea readOnly value={leftBoxContent} className="summary-textbox"></textarea>
        <textarea readOnly value={rightBoxContent} className="evaluation-textbox"></textarea>
      </div>
    </div>
  );
};

export default FileSummary;
