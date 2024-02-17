# app.py
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS

app = Flask(__name__, static_folder='uploads')  # Set 'uploads' as a folder for static files
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'pdf', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_URL_PATH'] = ''  # Serve static files at the root

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(image_path):
    # Process the image and return the summary
    # This is where you would integrate your AI model or any other logic
    summary = """This is a placeholder for the image summary
                Here is more text.
                Evaluation: 
                Next step: 
    """
    return summary


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Set the MIME type for PDF if the file is a PDF
    if filename.lower().endswith('.pdf'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype='application/pdf')
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        file_url = f'http://localhost:5000/uploads/{filename}'  # Ensure this URL is correct
        summary, evaluation = process_image(filepath)  # Call the summary processing function
        
        return jsonify({
            'message': 'File uploaded successfully',
            'fileUrl': file_url,
            'summaryText': summary,
            'evaluationText': evaluation,
            'fileType': 'pdf' if filename.lower().endswith('.pdf') else 'image'
        }), 200

    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
