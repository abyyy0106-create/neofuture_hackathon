from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Union
import re

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic matcher with a pre-trained model.
        """
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"Warning: Could not load model {model_name}: {e}")
            print("Using basic text similarity instead.")
            self.model = None

    def calculate_match(self, resume_data: Union[Dict, str], job_description: str) -> float:
        """
        Calculate semantic match score between resume and job description.
        Returns a score between 0 and 1, where 1 is perfect match.
        """
        if isinstance(resume_data, dict):
            # Extract relevant text from resume data
            resume_text = self._prepare_resume_text(resume_data)
        else:
            resume_text = resume_data

        if self.model:
            return self._calculate_semantic_similarity(resume_text, job_description)
        else:
            return self._calculate_basic_similarity(resume_text, job_description)

    def _prepare_resume_text(self, resume_data: Dict) -> str:
        """
        Prepare resume text for matching by combining relevant sections.
        """
        text_parts = []

        # Add skills (weighted more heavily)
        if 'skills' in resume_data and resume_data['skills']:
            skills_text = ' '.join(resume_data['skills'])
            text_parts.append(skills_text * 2)  # Weight skills more

        # Add experience
        if 'experience' in resume_data and resume_data['experience']:
            exp_text = ' '.join(resume_data['experience'])
            text_parts.append(exp_text)

        # Add education
        if 'education' in resume_data and resume_data['education']:
            edu_text = ' '.join(resume_data['education'])
            text_parts.append(edu_text)

        # Add full text as fallback
        if 'full_text' in resume_data:
            text_parts.append(resume_data['full_text'])

        return ' '.join(text_parts)

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity using sentence transformers.
        """
        try:
            # Encode both texts
            embeddings1 = self.model.encode(text1, convert_to_tensor=True)
            embeddings2 = self.model.encode(text2, convert_to_tensor=True)

            # Calculate cosine similarity
            similarity = util.cos_sim(embeddings1, embeddings2)

            # Return similarity score (clamp between 0 and 1)
            score = float(similarity.item())
            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"Error in semantic similarity calculation: {e}")
            return self._calculate_basic_similarity(text1, text2)

    def _calculate_basic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate basic text similarity using Jaccard similarity of words.
        """
        def preprocess_text(text: str) -> set:
            # Convert to lowercase, remove punctuation, split into words
            text = re.sub(r'[^\w\s]', '', text.lower())
            words = set(text.split())
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}
            return words - stop_words

        words1 = preprocess_text(text1)
        words2 = preprocess_text(text2)

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def find_best_matches(self, resumes: List[Dict], job_description: str, top_k: int = 5) -> List[Dict]:
        """
        Find the best matching resumes for a job description.
        """
        matches = []
        for resume in resumes:
            score = self.calculate_match(resume, job_description)
            matches.append({
                'resume': resume,
                'score': score
            })

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches[:top_k]

    def get_similarity_explanation(self, resume_data: Union[Dict, str], job_description: str) -> Dict:
        """
        Provide detailed explanation of why resumes match or don't match.
        """
        score = self.calculate_match(resume_data, job_description)

        explanation = {
            'overall_score': score,
            'match_level': self._get_match_level(score),
            'recommendations': []
        }

        if isinstance(resume_data, dict):
            # Check for specific matches
            if 'skills' in resume_data:
                job_skills = self._extract_keywords(job_description)
                resume_skills = set(resume_data['skills'])
                matching_skills = resume_skills & job_skills
                missing_skills = job_skills - resume_skills

                if matching_skills:
                    explanation['recommendations'].append(f"Matching skills: {', '.join(matching_skills)}")
                if missing_skills:
                    explanation['recommendations'].append(f"Consider adding skills: {', '.join(list(missing_skills)[:5])}")

        return explanation

    def _get_match_level(self, score: float) -> str:
        """
        Convert score to human-readable match level.
        """
        if score >= 0.8:
            return "Excellent Match"
        elif score >= 0.6:
            return "Good Match"
        elif score >= 0.4:
            return "Fair Match"
        elif score >= 0.2:
            return "Poor Match"
        else:
            return "No Match"

    def _extract_keywords(self, text: str) -> set:
        """
        Extract important keywords from text.
        """
        # Simple keyword extraction - in a real system, you'd use more sophisticated NLP
        tech_keywords = {
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'machine learning', 'ai', 'data science', 'web development', 'mobile development'
        }

        text_lower = text.lower()
        found_keywords = set()

        for keyword in tech_keywords:
            if keyword in text_lower:
                found_keywords.add(keyword)

        return found_keywords
def match_skills(resume_skills, job_skills):
    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))
    
    return matched, missing