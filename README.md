# AI-Based Resume Scanning System

An intelligent resume parsing and matching system that uses AI to analyze resumes and match them against job descriptions.

## Features

- **Resume Parsing**: Extract text from PDF and DOCX resume files
- **Information Extraction**: Automatically identify name, email, phone, skills, experience, and education
- **Advanced Semantic Matching**: Use AI-powered semantic similarity with weighted scoring system
- **Detailed Scoring Breakdown**: Provides component-wise scoring (skills, experience, semantic, education)
- **Comprehensive Skill Categories**: Supports programming languages, web technologies, databases, cloud platforms, ML/AI, and tools
- **Performance Optimization**: Embedding caching for faster repeated matches
- **REST API**: Simple Flask-based API for easy integration
- **Intelligent Recommendations**: Provides specific suggestions for skill gaps and improvements

## Scoring System

The matching algorithm uses a weighted scoring system:

- **Skills (40%)**: Direct skill overlap between resume and job requirements
- **Experience (30%)**: Semantic similarity of work experience descriptions
- **Semantic Similarity (20%)**: Overall AI-powered text similarity
- **Education (10%)**: Degree and field matching

### Example Output

```
Match Score: 0.492
Match Level: Fair Match

Detailed Breakdown:
  Skills: 0.600 (weight: 0.4, contribution: 0.240)
  Experience: 0.097 (weight: 0.3, contribution: 0.029)
  Semantic: 0.663 (weight: 0.2, contribution: 0.133)
  Education: 0.900 (weight: 0.1, contribution: 0.090)

Recommendations:
  - Consider adding skills: python, docker, tensorflow
  - Consider highlighting more relevant work experience
```

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

### Set environment variables

Before running the app, set the MongoDB URI and optional Flask secret key:

```bash
export MONGO_URI="mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority"
export FLASK_SECRET_KEY="your_flask_secret_here"
```

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

## Example Output

```
Match Score: 0.492
Match Level: Fair Match

Detailed Breakdown:
  Skills: 0.600 (weight: 0.4, contribution: 0.240)
  Experience: 0.097 (weight: 0.3, contribution: 0.029)
  Semantic: 0.663 (weight: 0.2, contribution: 0.133)
  Education: 0.900 (weight: 0.1, contribution: 0.090)

Recommendations:
  - Consider adding skills: python, docker, tensorflow
  - Consider highlighting more relevant work experience
```
