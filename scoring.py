from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_score(resume_text, job_text):
    """
    Calculate similarity score between resume and job description.
    
    Args:
        resume_text (str): The resume text
        job_text (str): The job description text
        
    Returns:
        float: Similarity score between 0 and 100, or None if error occurs
        
    Raises:
        ValueError: If inputs are None or empty
        Exception: For unexpected errors during calculation
    """
    try:
        # Input validation
        if not resume_text or not isinstance(resume_text, str):
            raise ValueError("Resume text must be a non-empty string")
        if not job_text or not isinstance(job_text, str):
            raise ValueError("Job text must be a non-empty string")
        
        # Vectorize and calculate similarity
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_text, job_text])
        
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return round(score * 100, 2)
    
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during score calculation: {str(e)}")
        raise