import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ImageUpload from './components/ImageUpload/ImageUpload';
import FileSummary from './components/FileSummary/FileSummary';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <img src="/assets/logo.png" alt="logo" className="App-logo" />
          <h1>AI for Justice</h1>
        </header>
        <Routes>
          <Route path="/" element={<ImageUpload />} />
          <Route path="/summary" element={<FileSummary />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
