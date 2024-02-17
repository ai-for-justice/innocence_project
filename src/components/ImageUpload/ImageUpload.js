// src/components/ImageUpload.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ImageUpload.css'; // Create and import your CSS for styling

const ImageUpload = () => {
  const [file, setFile] = useState(null);
  const navigate = useNavigate(); // useNavigate instead of useHistory

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert('No file selected.');
      return;
    }
    const formData = new FormData();
    formData.append('image', file);

    try {
      // Inside your upload handling function
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        // Use the React Router's navigate function to redirect to the FileSummary component with the necessary state
        navigate('/summary', { state: { fileUrl: data.fileUrl, fileType: data.fileType } });
      } else {
        // Handle the error
        console.error('Upload failed:', data.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred. Please try again later.');
    }
  };

  return (
    <div className="upload-container">
      <div className="welcome-text">
        Welcome to AI for Justice Website. We are here to help!
        Please upload the scanned questionnaire.
      </div>
      {/* The file input - hidden but functional */}
      <input type="file" id="file-input" className="file-input" onChange={handleFileChange} />
      {/* Style label as a button for the file input */}
      <label htmlFor="file-input" className="file-input-label">Choose File</label>
      <button onClick={handleSubmit} className="submit-button">Submit File</button>
    </div>
  );
};


export default ImageUpload;
