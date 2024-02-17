// src/components/UI/Button.js
import React from 'react';
import './Button.css'; // Importing the button styles

const Button = ({ onClick, children, className = '', type = 'button' }) => {
  return (
    <button className={`button ${className}`} onClick={onClick} type={type}>
      {children}
    </button>
  );
};

export default Button;
