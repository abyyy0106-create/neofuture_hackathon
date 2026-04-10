from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Union
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic matcher with a pre-trained model.

        Args:
            model_name: Name of the sentence transformer model to use
        """
        logger.info(f"Initializing SemanticMatcher with model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded model: {model_name}")
        except Exception as e:
            logger.warning(f"Could not load model {model_name}: {e}")
            logger.info("Falling back to basic text similarity instead of semantic matching")
            self.model = None

    def calculate_match(self, resume_data: Union[Dict, str], job_description: str) -> float:
        """
        Calculate semantic match score between resume and job description.
        Returns a score between 0 and 1, where 1 is perfect match.

        Args:
            resume_data: Resume data as dict or string
            job_description: Job description text

        Returns:
            float: Match score between 0 and 1

        Raises:
            ValueError: If job_description is empty or invalid
            TypeError: If resume_data type is invalid
        """
        try:
            if not job_description or not job_description.strip():
                logger.error("Job description is empty")
                raise ValueError("Job description cannot be empty")

            if isinstance(resume_data, dict):
                resume_text = self._prepare_resume_text(resume_data)
            elif isinstance(resume_data, str):
                resume_text = resume_data
            else:
                logger.error(f"Invalid resume_data type: {type(resume_data)}")
                raise TypeError(f"resume_data must be dict or str, got {type(resume_data)}")

            if not resume_text or not resume_text.strip():
                logger.warning("Resume text is empty after preparation")
                return 0.0

            if self.model:
                score = self._calculate_semantic_similarity(resume_text, job_description)
            else:
                score = self._calculate_basic_similarity(resume_text, job_description)

            logger.debug(f"Calculated match score: {score:.4f}")
            return score

        except Exception as e:
            logger.error(f"Error in calculate_match: {e}", exc_info=True)
            raise

    def _prepare_resume_text(self, resume_data: Dict) -> str:
        """
        Prepare resume text for matching by combining relevant sections.

        Args:
            resume_data: Dictionary containing resume information

        Returns:
            str: Combined resume text
        """
        try:
            text_parts = []

            # Add skills (weighted more heavily)
            if 'skills' in resume_data and resume_data['skills']:
                if not isinstance(resume_data['skills'], list):
                    logger.warning("Skills is not a list, converting")
                    resume_data['skills'] = [str(resume_data['skills'])]
                skills_text = ' '.join(str(s) for s in resume_data['skills'])
                text_parts.append(skills_text * 2)  # Weight skills more

            # Add experience
            if 'experience' in resume_data and resume_data['experience']:
                if not isinstance(resume_data['experience'], list):
                    logger.warning("Experience is not a list, converting")
                    resume_data['experience'] = [str(resume_data['experience'])]
                exp_text = ' '.join(str(e) for e in resume_data['experience'])
                text_parts.append(exp_text)

            # Add education
            if 'education' in resume_data and resume_data['education']:
                if not isinstance(resume_data['education'], list):
                    logger.warning("Education is not a list, converting")
                    resume_data['education'] = [str(resume_data['education'])]
                edu_text = ' '.join(str(ed) for ed in resume_data['education'])
                text_parts.append(edu_text)

            # Add full text as fallback
            if 'full_text' in resume_data:
                text_parts.append(str(resume_data['full_text']))

            result = ' '.join(text_parts)
            logger.debug(f"Prepared resume text of length: {len(result)}")
            return result

        except Exception as e:
            logger.error(f"Error in _prepare_resume_text: {e}", exc_info=True)
            return ""

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity using sentence transformers.

        Args:
            text1: First text (resume)
            text2: Second text (job description)

        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            if not self.model:
                logger.error("Model is not initialized")
                return self._calculate_basic_similarity(text1, text2)

            logger.debug(f"Encoding text1 ({len(text1)} chars) and text2 ({len(text2)} chars)")

            # Encode both texts
            embeddings1 = self.model.encode(text1, convert_to_tensor=True)
            embeddings2 = self.model.encode(text2, convert_to_tensor=True)

            # Calculate cosine similarity
            similarity = util.cos_sim(embeddings1, embeddings2)

            # Return similarity score (clamp between 0 and 1)
            score = float(similarity.item())
            score = max(0.0, min(1.0, score))

            logger.debug(f"Semantic similarity score: {score:.4f}")
            return score

        except Exception as e:
            logger.error(f"Error in semantic similarity calculation: {e}", exc_info=True)
            logger.info("Falling back to basic similarity")
            return self._calculate_basic_similarity(text1, text2)

    def _calculate_basic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate basic text similarity using Jaccard similarity of words.

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Jaccard similarity score between 0 and 1
        """
        try:
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
                logger.debug("Both texts are empty after preprocessing")
                return 1.0
            if not words1 or not words2:
                logger.debug("One or both texts empty after preprocessing")
                return 0.0

            # Jaccard similarity
            intersection = len(words1 & words2)
            union = len(words1 | words2)

            score = intersection / union if union > 0 else 0.0
            logger.debug(f"Basic similarity score: {score:.4f}")
            return score

        except Exception as e:
            logger.error(f"Error in basic similarity calculation: {e}", exc_info=True)
            return 0.0

    def find_best_matches(self, resumes: List[Dict], job_description: str, top_k: int = 5) -> List[Dict]:
        """
        Find the best matching resumes for a job description.

        Args:
            resumes: List of resume dictionaries
            job_description: Job description text
            top_k: Number of top matches to return

        Returns:
            List of best matching resumes with scores

        Raises:
            ValueError: If inputs are invalid
        """
        try:
            if not resumes:
                logger.warning("Resumes list is empty")
                return []

            if not isinstance(resumes, list):
                logger.error(f"Resumes must be a list, got {type(resumes)}")
                raise TypeError(f"resumes must be a list, got {type(resumes)}")

            logger.info(f"Finding best {top_k} matches from {len(resumes)} resumes")

            matches = []
            for idx, resume in enumerate(resumes):
                try:
                    score = self.calculate_match(resume, job_description)
                    matches.append({
                        'resume': resume,
                        'score': score,
                        'index': idx
                    })
                except Exception as e:
                    logger.warning(f"Error processing resume {idx}: {e}")
                    continue

            # Sort by score descending
            matches.sort(key=lambda x: x['score'], reverse=True)

            result = matches[:top_k]
            logger.info(f"Found {len(result)} matches, top score: {result[0]['score']:.4f if result else 'N/A'}")
            return result

        except Exception as e:
            logger.error(f"Error in find_best_matches: {e}", exc_info=True)
            raise

    def get_similarity_explanation(self, resume_data: Union[Dict, str], job_description: str) -> Dict:
        """
        Provide detailed explanation of why resumes match or don't match.

        Args:
            resume_data: Resume information
            job_description: Job description text

        Returns:
            Dictionary with explanation and recommendations
        """
        try:
            logger.info("Generating similarity explanation")

            score = self.calculate_match(resume_data, job_description)

            explanation = {
                'overall_score': score,
                'match_level': self._get_match_level(score),
                'recommendations': []
            }

            if isinstance(resume_data, dict):
                # Check for specific matches
                if 'skills' in resume_data:
                    try:
                        job_skills = self._extract_keywords(job_description)
                        resume_skills = set(resume_data['skills']) if isinstance(resume_data['skills'], list) else {resume_data['skills']}
                        matching_skills = resume_skills & job_skills
                        missing_skills = job_skills - resume_skills

                        if matching_skills:
                            explanation['recommendations'].append(f"Matching skills: {', '.join(matching_skills)}")
                        if missing_skills:
                            explanation['recommendations'].append(f"Consider adding skills: {', '.join(list(missing_skills)[:5])}")
                    except Exception as e:
                        logger.warning(f"Error extracting skills: {e}")

            logger.debug(f"Generated explanation with {len(explanation['recommendations'])} recommendations")
            return explanation

        except Exception as e:
            logger.error(f"Error in get_similarity_explanation: {e}", exc_info=True)
            raise

    def _get_match_level(self, score: float) -> str:
        """
        Convert score to human-readable match level.

        Args:
            score: Match score between 0 and 1

        Returns:
            str: Human-readable match level
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

        Args:
            text: Text to extract keywords from

        Returns:
            set: Set of technical keywords found
        """
        try:
            # Simple keyword extraction - in a real system, you'd use more sophisticated NLP
            tech_keywords = {
                'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
                'machine learning', 'ai', 'data science', 'web development', 'mobile development',
                'c++', 'c#', '.net', 'php', 'ruby', 'golang', 'rust', 'kotlin', 'swift',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy'
            }

            text_lower = text.lower()
            found_keywords = set()

            for keyword in tech_keywords:
                if keyword in text_lower:
                    found_keywords.add(keyword)

            logger.debug(f"Extracted {len(found_keywords)} keywords from text")
            return found_keywords

        except Exception as e:
            logger.error(f"Error in _extract_keywords: {e}", exc_info=True)
            return set()
