import React from 'react';
import Button from '../UI/Button'; // Adjust the path as necessary
import './ImageUpload.css';

const ImageUpload = () => {
    // Assuming you have state and handlers set up for image upload

    const handleSubmit = () => {
        console.log('Submit the image here');
        // Implementation for what happens on submit
    };

    return (
        <div className="image-upload-container">
            {/* Existing input and label for file upload */}
            <Button onClick={handleSubmit}>Submit Image</Button>
            {/* Other UI elements as needed */}
        </div>
    );
};

export default ImageUpload;

<textarea className="textbox" placeholder="Enter text here..."></textarea>
