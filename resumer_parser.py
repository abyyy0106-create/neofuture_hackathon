import pdfplumber
from docx import Document
import spacy
import re
from typing import Dict, List

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not installed, we'll use basic text processing
            self.nlp = None
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")

    def parse_resume(self, file_path: str) -> Dict:
        """
        Parse a resume file (PDF or DOCX) and extract structured information.
        """
        text = self._extract_text(file_path)

        if not text:
            raise ValueError("Could not extract text from resume")

        # Extract basic information
        resume_data = {
            'full_text': text,
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text)
        }

        return resume_data

    def _extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF or DOCX file.
        """
        if file_path.lower().endswith('.pdf'):
            return self._extract_pdf_text(file_path)
        elif file_path.lower().endswith('.docx'):
            return self._extract_docx_text(file_path)
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")

    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text from PDF file using pdfplumber.
        """
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    def _extract_docx_text(self, file_path: str) -> str:
        """
        Extract text from DOCX file.
        """
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    def _extract_name(self, text: str) -> str:
        """
        Extract name from resume text (simple heuristic).
        """
        lines = text.split('\n')[:5]  # Check first few lines
        for line in lines:
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                # Simple check: not too long, no numbers
                return line
        return "Unknown"

    def _extract_email(self, text: str) -> str:
        """
        Extract email address using regex.
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def _extract_phone(self, text: str) -> str:
        """
        Extract phone number using regex.
        """
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else ""

    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text.
        """
        # Common skills keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'html', 'css', 'react', 'angular', 'vue', 'node.js',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        ]

        text_lower = text.lower()
        skills = []

        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())

        return list(set(skills))  # Remove duplicates

    def _extract_experience(self, text: str) -> List[str]:
        """
        Extract work experience sections.
        """
        # Simple pattern matching for experience sections
        experience_patterns = [
            r'(?:work experience|professional experience|employment history)(.*?)(?:education|skills|$)',
            r'(?:experience|work history)(.*?)(?:education|skills|$)'
        ]

        experience_text = ""
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                experience_text = match.group(1).strip()
                break

        if not experience_text:
            # Fallback: look for years and company names
            lines = text.split('\n')
            experience_lines = []
            for line in lines:
                if re.search(r'\b(19|20)\d{2}\b', line) or any(word in line.lower() for word in ['inc', 'ltd', 'corp', 'company', 'llc']):
                    experience_lines.append(line.strip())

            experience_text = '\n'.join(experience_lines[:10])  # Limit to first 10 lines

        return [experience_text] if experience_text else []

    def _extract_education(self, text: str) -> List[str]:
        """
        Extract education information.
        """
        education_patterns = [
            r'(?:education|academic background)(.*?)(?:experience|skills|$)',
            r'(?:degree|bachelor|master|phd|university|college)(.*?)(?:experience|skills|$)'
        ]

        education_text = ""
        for pattern in education_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                education_text = match.group(1).strip()
                break

        if not education_text:
            # Fallback: look for education keywords
            lines = text.split('\n')
            education_lines = []
            for line in lines:
                if any(word in line.lower() for word in ['university', 'college', 'degree', 'bachelor', 'master', 'phd']):
                    education_lines.append(line.strip())

            education_text = '\n'.join(education_lines[:5])  # Limit to first 5 lines

        return [education_text] if education_text else []
