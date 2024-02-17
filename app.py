# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from llm_pipeline import (
    analyze_applicant_intake_letters,
    MISSINFO_CHECK_CHAIN,
    CRITERIA_CHECK_CHAIN,
)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "pdf", "jpg", "jpeg"}


# Application Factory
def create_app():
    app = Flask(__name__, static_folder=UPLOAD_FOLDER)
    CORS(app)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Utility function
    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    # Routes
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        mimetype = "application/pdf" if filename.lower().endswith(".pdf") else None
        return send_from_directory(
            app.config["UPLOAD_FOLDER"], filename, mimetype=mimetype
        )

    @app.route("/upload", methods=["POST"])
    def upload_file():
        # Error handling for missing file part
        if "image" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["image"]
        # Error handling for empty filename
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Process the uploaded file
            background = analyze_applicant_intake_letters(filepath)
            is_missinginfo = MISSINFO_CHECK_CHAIN.invoke({"background": background})

            if is_missinginfo["response"].lower() == "yes":
                response = {
                    "backgroundQ": "What background information have we extracted from the applicant's intake letter?",
                    "background": background,
                    "is_missinginfo_Q": "Do we need more information from the applicant to proceed with the evaluation?",
                    "next_steps": is_missinginfo["next_steps"],
                }
            else:
                evaluation = CRITERIA_CHECK_CHAIN.invoke({"background": background})
                response = {
                    "backgroundQ": "What background information have we extracted from the applicant's intake letter?",
                    "background": background,
                    "is_missinginfo_Q": "Do we need more information from the applicant to proceed with the evaluation?",
                    "is_missinginfo_A": "No, we have enough information to proceed with the evaluation.",
                    "evaluation": evaluation["evaluation"],
                    "conclusion": evaluation["conclusion"],
                    "next_steps": evaluation["next_steps"],
                }

            return jsonify(response), 200
        else:
            return jsonify({"error": "File type not allowed"}), 400

    return app


# Main entry point
if __name__ == "__main__":
    app = create_app()
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
