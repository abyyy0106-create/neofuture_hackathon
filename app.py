import logging
logging.basicConfig(level=logging.INFO)
from flask_cors import CORS
CORS(app)

from flask import Flask, request, jsonify
import os
import uuid
from resumer_parser import ResumeParser
from semantic_matcher import SemanticMatcher

app = Flask(__name__)

# Initialize components once (important for performance)
parser = ResumeParser()
matcher = SemanticMatcher()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        job_description = request.form.get('job_description', '')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Generate unique temp file
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        temp_path = os.path.join(UPLOAD_DIR, unique_name)
        file.save(temp_path)

        # Parse resume
        resume_data = parser.parse_resume(temp_path)

        # Optional matching
        if job_description:
            match_result = matcher.calculate_match(resume_data, job_description)
            resume_data["match"] = match_result

        return jsonify(resume_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Cleanup safely
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/match_resumes', methods=['POST'])
def match_resumes():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON body provided'}), 400

        resumes = data.get('resumes', [])
        job_description = data.get('job_description', '')

        if not resumes or not job_description:
            return jsonify({'error': 'Missing resumes or job description'}), 400

        matched_resumes = []

        # batch matching
        for resume in resumes:
            result = matcher.calculate_match(resume, job_description)
            resume["match"] = result
            matched_resumes.append(resume)

        # Sort by final score
        matched_resumes.sort(
            key=lambda x: x["match"]["final_score"],
            reverse=True
        )

        return jsonify({
            "total": len(matched_resumes),
            "matched_resumes": matched_resumes
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "service": "AI Resume Screener",
        "version": "1.1"
    })