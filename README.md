# AI-Based Resume Scanning System

An intelligent resume parsing and matching system that uses AI to analyze resumes and match them against job descriptions.

## Features

- **Resume Parsing**: Extract text from PDF and DOCX resume files
- **Information Extraction**: Automatically identify name, email, phone, skills, experience, and education
- **Semantic Matching**: Use AI-powered semantic similarity to match resumes with job descriptions
- **REST API**: Simple Flask-based API for easy integration
- **Scoring System**: Provides match scores and recommendations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd neofuture_hackathon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### Upload and Analyze Resume
```http
POST /upload_resume
```

Upload a resume file and optionally provide a job description for matching.

**Parameters:**
- `file`: Resume file (PDF or DOCX)
- `job_description`: (optional) Job description text

**Example using curl:**
```bash
curl -X POST -F "file=@resume.pdf" -F "job_description=Looking for Python developer with ML experience" http://localhost:5000/upload_resume
```

#### Match Multiple Resumes
```http
POST /match_resumes
```

Match multiple resumes against a job description.

**Request Body:**
```json
{
  "resumes": [
    {
      "name": "John Doe",
      "skills": ["Python", "Machine Learning"],
      "experience": ["Software Engineer at XYZ Corp"]
    }
  ],
  "job_description": "Looking for Python developer with ML experience"
}
```

## Components

- `app.py`: Main Flask application with API endpoints
- `resumer_parser.py`: Resume parsing and information extraction
- `semantic_matcher.py`: AI-powered semantic matching using sentence transformers

## Dependencies

- Flask: Web framework
- pdfplumber: PDF text extraction
- python-docx: DOCX text extraction
- sentence-transformers: AI semantic similarity
- spaCy: Natural language processing
- torch: Machine learning framework

## Testing

Run the test script to see the system in action:

```bash
python test_system.py
```

This will demonstrate:
- Resume parsing capabilities
- Semantic matching against a job description
- Match scoring and recommendations

## Example Output

```
Match Score: 0.690
Match Level: Good Match
Recommendations:
  - Matching skills: Python, Machine Learning, AWS, Docker
  - Consider adding skills: react, tensorflow
```