from flask import Flask, request, jsonify
import os
from resumer_parser import ResumeParser
from semantic_matcher import SemanticMatcher

app = Flask(__name__)

# Initialize components
parser = ResumeParser()
matcher = SemanticMatcher()

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)

    try:
        # Parse resume
        resume_data = parser.parse_resume(temp_path)

        # Get job description from request
        job_description = request.form.get('job_description', '')

        if job_description:
            # Calculate semantic match score
            match_score = matcher.calculate_match(resume_data, job_description)
            resume_data['match_score'] = match_score

        # Clean up temp file
        os.remove(temp_path)

        return jsonify(resume_data)

    except Exception as e:
        os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

@app.route('/match_resumes', methods=['POST'])
def match_resumes():
    data = request.get_json()

    if not data or 'resumes' not in data or 'job_description' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    resumes = data['resumes']
    job_description = data['job_description']

    matched_resumes = []
    for resume in resumes:
        match_score = matcher.calculate_match(resume, job_description)
        resume['match_score'] = match_score
        matched_resumes.append(resume)

    # Sort by match score
    matched_resumes.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify({'matched_resumes': matched_resumes})

if __name__ == '__main__':
    app.run(debug=True)
