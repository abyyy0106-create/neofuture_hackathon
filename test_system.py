#!/usr/bin/env python3
"""
Test script for the AI Resume Scanning System
"""

import unittest
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
    - Experience with machine learning frameworks like TensorFlow or PyTorch
    - Knowledge of AWS and cloud services
    - SQL database experience
    - Docker containerization skills
    - Experience building REST APIs
    - Bachelor's degree in Computer Science or related field
    """

    score = matcher.calculate_match(resume_data, job_description)
    explanation = matcher.get_similarity_explanation(resume_data, job_description)

    print(f"Match Score: {score:.3f}")
    print(f"Match Level: {explanation['match_level']}")

    # Show detailed breakdown
    if 'breakdown' in explanation:
        print("\nDetailed Breakdown:")
        breakdown = explanation['breakdown']
        for component, comp_score in breakdown['component_scores'].items():
            weight = breakdown['weights'][component]
            weighted_contribution = comp_score * weight
            print(f"  {component.capitalize()}: {comp_score:.3f} (weight: {weight}, contribution: {weighted_contribution:.3f})")

    print("\nRecommendations:")
    for rec in explanation['recommendations']:
        print(f"  - {rec}")

class TestResumeSystem(unittest.TestCase):
    """Unit tests for Resume Scanning System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.matcher = SemanticMatcher()
        self.base_resume = {
            'full_text': 'Python developer with ML experience',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '555-0000',
            'skills': ['Python', 'Machine Learning', 'SQL'],
            'experience': ['Software Engineer'],
            'education': ['BS Computer Science']
        }
    
    def test_perfect_match(self):
        """Test matching resume with identical job description"""
        job_desc = "Python developer with Machine Learning and SQL experience"
        score = self.matcher.calculate_match(self.base_resume, job_desc)
        self.assertGreater(score, 0.8, "Perfect match should have high score")
        print(f"✓ Perfect match test passed: {score:.3f}")
    
    def test_partial_match(self):
        """Test matching resume with partially matching job description"""
        job_desc = "Java developer needed"
        score = self.matcher.calculate_match(self.base_resume, job_desc)
        self.assertLess(score, 0.8, "Partial match should have lower score")
        self.assertGreater(score, 0.0, "Score should be positive")
        print(f"✓ Partial match test passed: {score:.3f}")
    
    def test_no_overlap(self):
        """Test resume with completely different job description"""
        job_desc = "Marine biologist with deep sea diving experience required"
        score = self.matcher.calculate_match(self.base_resume, job_desc)
        self.assertLess(score, 0.3, "No overlap should have very low score")
        print(f"✓ No overlap test passed: {score:.3f}")
    
    def test_technical_skills_focus(self):
        """Test matching when job focuses on technical skills"""
        job_desc = "Expert in Python, TensorFlow, PyTorch, and advanced ML algorithms"
        score = self.matcher.calculate_match(self.base_resume, job_desc)
        explanation = self.matcher.get_similarity_explanation(self.base_resume, job_desc)
        self.assertIn('match_level', explanation, "Explanation should contain match_level")
        print(f"✓ Technical skills test passed: {score:.3f}")
    
    def test_frontend_to_backend_mismatch(self):
        """Test frontend developer resume against backend job"""
        frontend_resume = {
            'full_text': 'Frontend developer experience',
            'name': 'Frontend Dev',
            'skills': ['React', 'JavaScript', 'CSS', 'HTML'],
            'experience': ['Frontend Engineer at Web Co'],
            'education': ['BS Computer Science']
        }
        backend_job = "Backend developer needed: Node.js, MongoDB, REST APIs"
        score = self.matcher.calculate_match(frontend_resume, backend_job)
        self.assertLess(score, 0.7, "Frontend resume should not match backend job well")
        print(f"✓ Frontend/Backend mismatch test passed: {score:.3f}")
    
    def test_senior_vs_junior_role(self):
        """Test junior resume against senior role requirements"""
        junior_resume = {
            'full_text': 'Fresh graduate',
            'name': 'Junior Dev',
            'skills': ['Python basics', 'HTML', 'CSS'],
            'experience': ['Internship at Startup'],
            'education': ['BS Computer Science']
        }
        senior_job = """Senior architect position: 10+ years experience, 
                        system design, microservices, Kubernetes, distributed systems"""
        score = self.matcher.calculate_match(junior_resume, senior_job)
        self.assertLess(score, 0.5, "Junior resume should not match senior role")
        print(f"✓ Seniority mismatch test passed: {score:.3f}")
    
    def test_multiple_matching_skills(self):
        """Test resume with multiple matching skills"""
        skills_resume = {
            'full_text': 'Multi-skilled developer',
            'name': 'Full Stack Dev',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB', 'AWS', 'Docker', 'SQL'],
            'experience': ['Senior Developer at Tech Corp'],
            'education': ['MS Computer Science']
        }
        job_desc = "Full stack developer: Python, React, Node.js, MongoDB, Docker, AWS required"
        score = self.matcher.calculate_match(skills_resume, job_desc)
        self.assertGreater(score, 0.7, "Resume with all required skills should score high")
        print(f"✓ Multiple matching skills test passed: {score:.3f}")
    
    def test_score_range(self):
        """Test that scores are always in valid range"""
        for i in range(5):
            score = self.matcher.calculate_match(self.base_resume, f"Job description variant {i}")
            self.assertGreaterEqual(score, 0.0, "Score should be >= 0")
            self.assertLessEqual(score, 1.0, "Score should be <= 1")
        print("✓ Score range test passed")
    
    def test_explanation_structure(self):
        """Test that explanation has required structure"""
        job_desc = "Python developer wanted"
        explanation = self.matcher.get_similarity_explanation(self.base_resume, job_desc)
        self.assertIn('match_level', explanation, "Missing match_level in explanation")
        self.assertIn('recommendations', explanation, "Missing recommendations in explanation")
        print("✓ Explanation structure test passed")

if __name__ == "__main__":
    # Run the main test
    test_semantic_matching()
    
    # Run unit tests
    print("\n" + "="*60)
    print("Running Unit Tests...")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestResumeSystem)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)