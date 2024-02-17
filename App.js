import React from 'react';
import Button from './components/UI/Button'; // If App.js and components folder are on the same level
import ImageUpload from './components/ImageUpload/ImageUpload';
import './App.css'; // Assuming App.css is directly within src/


function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src="/assets/logo.png" alt="logo" className="App-logo" />
        <h1>AI for Justice</h1>
      </header>
      <main>
        <ImageUpload />
        {/* Example button, e.g., for navigating to another page */}
        <Button onClick={() => console.log('Navigate somewhere')}>Go Somewhere</Button>
      </main>
    </div>
  );
}

export default App;
