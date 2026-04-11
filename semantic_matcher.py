import logging
from sentence_transformers import SentenceTransformer, util

# Load model ONCE (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")

<<<<<<< HEAD
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic matcher with a pre-trained model.
=======
def sbert_similarity(text1, text2):
    """
    Returns semantic similarity score (0–100)
    using SBERT embeddings + cosine similarity
    """
>>>>>>> ec333ba (final changes)

    if not text1.strip() or not text2.strip():
        return 0.0

<<<<<<< HEAD
    def calculate_match(self, resume_data: Union[Dict, str], job_description: str) -> float:
        """
        Calculate semantic match score between resume and job description.
        Returns a score between 0 and 1, where 1 is perfect match.
        """
        if isinstance(resume_data, dict):
            return self._calculate_weighted_score(resume_data, job_description)

        if self.model:
            return self._calculate_semantic_similarity(resume_data, job_description)
        else:
            return self._calculate_basic_similarity(resume_data, job_description)

    def _calculate_weighted_score(self, resume_data: Dict, job_description: str) -> float:
        """
        Calculate weighted match score with different components.
        """
        try:
            weights = {
                'skills': 0.6,
                'experience': 0.2,
                'semantic': 0.1,
                'education': 0.1
            }

            scores = {
                'skills': 0.0,
                'experience': 0.0,
                'semantic': 0.0,
                'education': 0.0
            }

            if 'skills' in resume_data and resume_data['skills']:
                scores['skills'] = self._calculate_skills_match(resume_data['skills'], job_description)

            if 'experience' in resume_data and resume_data['experience']:
                scores['experience'] = self._calculate_experience_match(resume_data['experience'], job_description)

            resume_text = self._prepare_resume_text(resume_data)
            if self.model:
                scores['semantic'] = self._calculate_semantic_similarity(resume_text, job_description)
            else:
                scores['semantic'] = self._calculate_basic_similarity(resume_text, job_description)

            if 'education' in resume_data and resume_data['education']:
                scores['education'] = self._calculate_education_match(resume_data['education'], job_description)

            final_score = sum(scores[key] * weights[key] for key in weights)
            logger.debug(f"Calculated weighted score: {final_score:.4f}")
            return max(0.0, min(1.0, final_score))

        except Exception as e:
            logger.error(f"Error in _calculate_weighted_score: {e}", exc_info=True)
            raise

    def _calculate_skills_match(self, skills: Union[List[str], str], job_description: str) -> float:
        if isinstance(skills, str):
            skills = [skills]

        resume_skills = {str(s).strip().lower() for s in skills if s}
        job_keywords = self._extract_keywords(job_description)

        if job_keywords:
            if not resume_skills:
                return 0.0
            matched = 0
            for keyword in job_keywords:
                if keyword in resume_skills:
                    matched += 1
                elif keyword.replace('.', '') in ' '.join(resume_skills):
                    matched += 1
            return matched / len(job_keywords)

        job_text = job_description.lower()
        found = sum(1 for skill in resume_skills if skill in job_text)
        return found / len(resume_skills) if resume_skills else 0.0

    def _calculate_experience_match(self, experiences: Union[List[str], str], job_description: str) -> float:
        if isinstance(experiences, str):
            experiences = [experiences]

        experience_text = ' '.join(str(i) for i in experiences)
        if self.model:
            return self._calculate_semantic_similarity(experience_text, job_description)
        return self._calculate_basic_similarity(experience_text, job_description)

    def _calculate_education_match(self, education: Union[List[str], str], job_description: str) -> float:
        if isinstance(education, str):
            education = [education]

        education_text = ' '.join(str(e) for e in education).lower()
        if 'bachelor' in education_text or 'bs' in education_text or 'b.sc' in education_text:
            return 1.0
        if 'master' in education_text or 'ms' in education_text or 'm.sc' in education_text:
            return 1.0
        if 'phd' in education_text or 'doctorate' in education_text:
            return 1.0
        return 0.2 if education_text else 0.0

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
=======
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()
    return round(score * 100, 2)
>>>>>>> ec333ba (final changes)
