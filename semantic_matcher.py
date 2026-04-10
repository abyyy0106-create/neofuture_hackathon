from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Union, Tuple
import re
import hashlib
from functools import lru_cache

TFIDF_WEIGHT = 0.5
SEMANTIC_WEIGHT = 0.5

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

        # Initialize caching for embeddings
        self.embedding_cache = {}

        # Enhanced stop words list
        self.stop_words = self._load_stop_words()

        # Comprehensive skill categories
        self.skill_categories = self._load_skill_categories()

    def _load_stop_words(self) -> set:
        """Load comprehensive stop words list."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
            'am', 'as', 'if', 'then', 'else', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there'
        }

    def _load_skill_categories(self) -> Dict[str, List[str]]:
        """Load comprehensive skill categories."""
        return {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'php', 'ruby',
                'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
                'spring', 'asp.net', 'jquery', 'bootstrap', 'sass', 'less', 'webpack', 'babel'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
                'elasticsearch', 'dynamodb', 'firebase', 'couchdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode',
                'kubernetes', 'docker', 'terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions'
            ],
            'ml_ai': [
                'machine learning', 'deep learning', 'artificial intelligence', 'neural networks',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'opencv',
                'computer vision', 'nlp', 'natural language processing', 'data science', 'statistics'
            ],
            'tools_frameworks': [
                'git', 'github', 'bitbucket', 'jira', 'slack', 'trello', 'figma', 'postman',
                'vscode', 'intellij', 'eclipse', 'vim', 'linux', 'windows', 'macos'
            ]
        }

    def calculate_match(self, resume_data: Union[Dict, str], job_description: str) -> float:
        """
        Calculate semantic match score between resume and job description.
        Returns a score between 0 and 1, where 1 is perfect match.
        """
        if isinstance(resume_data, dict):
            # Extract relevant text from resume data
            resume_text = self._prepare_resume_text(resume_data)
            # Calculate weighted score with breakdown
            return self._calculate_weighted_score(resume_data, job_description)
        else:
            resume_text = resume_data

        if self.model:
            return self._calculate_semantic_similarity(resume_text, job_description)
        else:
            return self._calculate_basic_similarity(resume_text, job_description)

    def _calculate_weighted_score(self, resume_data: Dict, job_description: str) -> float:
        """
        Calculate weighted match score with different components.
        """
        weights = {
            'skills': 0.4,      # Most important
            'experience': 0.3,  # Second most important
            'semantic': 0.2,    # Overall semantic similarity
            'education': 0.1    # Least important for technical roles
        }

        scores = {}

        # Skills matching (most weighted)
        if 'skills' in resume_data and resume_data['skills']:
            scores['skills'] = self._calculate_skills_match(resume_data['skills'], job_description)
        else:
            scores['skills'] = 0.0

        # Experience matching
        if 'experience' in resume_data and resume_data['experience']:
            scores['experience'] = self._calculate_experience_match(resume_data['experience'], job_description)
        else:
            scores['experience'] = 0.0

        # Semantic similarity of full text
        resume_text = self._prepare_resume_text(resume_data)
        if self.model:
            scores['semantic'] = self._calculate_semantic_similarity(resume_text, job_description)
        else:
            scores['semantic'] = self._calculate_basic_similarity(resume_text, job_description)

        # Education matching (basic keyword matching)
        if 'education' in resume_data and resume_data['education']:
            scores['education'] = self._calculate_education_match(resume_data['education'], job_description)
        else:
            scores['education'] = 0.0

        # Calculate weighted average
        weighted_score = sum(scores[component] * weights[component] for component in weights.keys())

        # Store breakdown for explanation
        self.last_match_breakdown = {
            'overall_score': weighted_score,
            'component_scores': scores,
            'weights': weights
        }

        return min(1.0, max(0.0, weighted_score))

    def _prepare_resume_text(self, resume_data: Dict) -> str:
        """
        Prepare resume text for matching by combining relevant sections.
        """
        text_parts = []

        # Add skills (weighted more heavily)
        if 'skills' in resume_data and resume_data['skills']:
            skills_text = ' '.join(resume_data['skills'])
            text_parts.append(skills_text)

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

    def _calculate_skills_match(self, resume_skills: List[str], job_description: str) -> float:
        """
        Calculate skills match score based on overlap between resume skills and job requirements.
        """
        if not resume_skills:
            return 0.0

        # Extract skills from job description
        job_skills = self._extract_skills_from_text(job_description)

        if not job_skills:
            # If no specific skills found in job description, give moderate score
            return 0.5

        # Normalize skills for comparison
        resume_skills_norm = set(self._normalize_skill(skill) for skill in resume_skills)
        job_skills_norm = set(self._normalize_skill(skill) for skill in job_skills)

        # Calculate Jaccard similarity
        intersection = len(resume_skills_norm & job_skills_norm)
        union = len(resume_skills_norm | job_skills_norm)

        if union == 0:
            return 0.0

        # Boost score if there are many matching skills
        base_score = intersection / union
        if intersection >= 3:  # Bonus for having multiple matching skills
            base_score = min(1.0, base_score * 1.2)

        return base_score

    def _calculate_experience_match(self, resume_experience: List[str], job_description: str) -> float:
        """
        Calculate experience match score based on semantic similarity of experience descriptions.
        """
        if not resume_experience:
            return 0.0

        # Combine all experience text
        experience_text = ' '.join(resume_experience)

        # Extract experience-related keywords from job description
        experience_keywords = self._extract_experience_keywords(job_description)

        if not experience_keywords:
            return 0.5  # Neutral score if no specific experience requirements

        # Calculate semantic similarity between experience text and job requirements
        if self.model:
            return self._calculate_semantic_similarity(experience_text, ' '.join(experience_keywords))
        else:
            return self._calculate_basic_similarity(experience_text, ' '.join(experience_keywords))

    def _calculate_education_match(self, resume_education: List[str], job_description: str) -> float:
        """
        Calculate education match score based on degree and field matching.
        """
        if not resume_education:
            return 0.0

        education_text = ' '.join(resume_education).lower()
        job_text = job_description.lower()

        # Check for degree requirements
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'degree', 'bsc', 'msc', 'bachelor\'s', 'master\'s']
        required_degrees = [kw for kw in degree_keywords if kw in job_text]

        if not required_degrees:
            return 0.7  # Most jobs don't specify strict degree requirements

        # Check if resume has matching degrees
        matching_degrees = [degree for degree in required_degrees if degree in education_text]

        if matching_degrees:
            return 0.9  # Good match if degree requirements are met
        else:
            return 0.3  # Poor match if degree requirements not met

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using comprehensive skill categories.
        """
        text_lower = text.lower()
        found_skills = []

        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill)

        return list(set(found_skills))  # Remove duplicates

    def _extract_experience_keywords(self, job_description: str) -> List[str]:
        """
        Extract experience-related keywords from job description.
        """
        experience_indicators = [
            'experience', 'years', 'senior', 'junior', 'lead', 'principal', 'staff',
            'developed', 'built', 'designed', 'managed', 'led', 'architected'
        ]

        text_lower = job_description.lower()
        found_keywords = []

        for indicator in experience_indicators:
            if indicator in text_lower:
                found_keywords.append(indicator)

        return found_keywords

    def _normalize_skill(self, skill: str) -> str:
        """
        Normalize skill names for better matching.
        """
        skill = skill.lower().strip()
        # Remove common variations
        skill = re.sub(r'[^\w\s]', '', skill)  # Remove punctuation
        skill = re.sub(r'\s+', ' ', skill)     # Normalize whitespace

        # Standardize common variations
        normalizations = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'nlp': 'natural language processing',
            'cv': 'computer vision'
        }

        return normalizations.get(skill, skill)

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity using sentence transformers with caching.
        """
        try:
            # Create cache keys
            key1 = self._get_text_hash(text1)
            key2 = self._get_text_hash(text2)

            # Check cache first
            if key1 in self.embedding_cache:
                embedding1 = self.embedding_cache[key1]
            else:
                embedding1 = self.model.encode(text1, convert_to_tensor=True)
                self.embedding_cache[key1] = embedding1

            if key2 in self.embedding_cache:
                embedding2 = self.embedding_cache[key2]
            else:
                embedding2 = self.model.encode(text2, convert_to_tensor=True)
                self.embedding_cache[key2] = embedding2

            # Calculate cosine similarity
            similarity = util.cos_sim(embedding1, embedding2)

            # Return similarity score (clamp between 0 and 1)
            score = float(similarity.item())
            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"Error in semantic similarity calculation: {e}")
            return self._calculate_basic_similarity(text1, text2)

    def _get_text_hash(self, text: str) -> str:
        """
        Generate a hash for text caching.
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _calculate_basic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate basic text similarity using Jaccard similarity of words.
        """
        def preprocess_text(text: str) -> set:
            # Convert to lowercase, remove punctuation, split into words
            text = re.sub(r'[^\w\s]', '', text.lower())
            words = set(text.split())
            # Remove stop words
            return words - self.stop_words

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

        # Add detailed breakdown if available
        if hasattr(self, 'last_match_breakdown'):
            explanation['breakdown'] = self.last_match_breakdown

        if isinstance(resume_data, dict):
            # Check for specific matches
            if 'skills' in resume_data:
                job_skills = self._extract_skills_from_text(job_description)
                resume_skills = set(resume_data['skills'])
                matching_skills = resume_skills & set(job_skills)
                missing_skills = set(job_skills) - resume_skills

                if matching_skills:
                    explanation['recommendations'].append(f"Matching skills: {', '.join(list(matching_skills)[:5])}")
                if missing_skills:
                    explanation['recommendations'].append(f"Consider adding skills: {', '.join(list(missing_skills)[:5])}")

            # Experience recommendations
            if hasattr(self, 'last_match_breakdown') and 'component_scores' in self.last_match_breakdown:
                exp_score = self.last_match_breakdown['component_scores'].get('experience', 0)
                if exp_score < 0.5:
                    explanation['recommendations'].append("Consider highlighting more relevant work experience")

                # Education recommendations
                edu_score = self.last_match_breakdown['component_scores'].get('education', 0)
                if edu_score < 0.5:
                    explanation['recommendations'].append("Education background may not fully match requirements")

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
    gap_percentage = len(missing) / max(len(job_skills), 1)
    
    return matched, missing