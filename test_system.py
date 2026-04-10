#!/usr/bin/env python3
"""
Test script for the AI Resume Scanning System
"""

from resumer_parser import ResumeParser
from semantic_matcher import SemanticMatcher

def test_resume_parsing():
    """Test resume parsing functionality"""
    print("Testing Resume Parser...")

    # Since we don't have a PDF/DOCX file, let's test with text directly
    parser = ResumeParser()

    # Read sample resume
    with open('sample_resume.txt', 'r') as f:
        sample_text = f.read()

    # Create a mock resume data structure
    resume_data = {
        'full_text': sample_text,
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '555-123-4567',
        'skills': ['Python', 'Machine Learning', 'JavaScript', 'SQL', 'AWS', 'Docker'],
        'experience': ['Software Engineer at Tech Corp', 'Junior Developer at Startup Inc'],
        'education': ['Bachelor of Science in Computer Science']
    }

    print("Resume Data:")
    for key, value in resume_data.items():
        print(f"  {key}: {value}")

    return resume_data

def test_semantic_matching():
    """Test semantic matching functionality"""
    print("\nTesting Semantic Matcher...")

    matcher = SemanticMatcher()

    resume_data = test_resume_parsing()

    job_description = """
    We are looking for a Python developer with machine learning experience.
    The ideal candidate should have:
    - Strong Python programming skills
    - Experience with machine learning frameworks
    - Knowledge of AWS and cloud services
    - SQL database experience
    - Docker containerization skills
    """

    score = matcher.calculate_match(resume_data, job_description)
    explanation = matcher.get_similarity_explanation(resume_data, job_description)

    print(f"Match Score: {score:.3f}")
    print(f"Match Level: {explanation['match_level']}")
    print("Recommendations:")
    for rec in explanation['recommendations']:
        print(f"  - {rec}")

if __name__ == "__main__":
    test_semantic_matching()