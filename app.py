# app.py
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS

app = Flask(__name__, static_folder='uploads')  # Set 'uploads' as a folder for static files
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_URL_PATH'] = ''  # Serve static files at the root

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(image_path):
    # Process the image and return the summary
    # This is where you would integrate your AI model or any other logic
    summary = "This is a placeholder for the image summary."
    return summary


@app.route('/uploads/<filename>')
def uploaded_file(filename):
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

        # Create a full URL to the saved image
        image_url = request.host_url.rstrip('/') + '/' + os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("Image URL:", image_url)
        # summary_text = process_image(filepath)
        x = dict()

        return jsonify({
            'message': 'File uploaded successfully',
            'imageUrl': image_url,
            'summaryText': x['summary_text'],
            'xxx': x['xxxx']
        }), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
