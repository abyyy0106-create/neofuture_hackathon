import logging
from sentence_transformers import SentenceTransformer, util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = SentenceTransformer("all-MiniLM-L6-v2")


def sbert_similarity(text1: str, text2: str) -> float:
    """Return semantic similarity score between 0 and 100."""
    if not text1 or not text2:
        return 0.0

    try:
        embeddings1 = model.encode(text1, convert_to_tensor=True)
        embeddings2 = model.encode(text2, convert_to_tensor=True)
        similarity = util.cos_sim(embeddings1, embeddings2)
        score = float(similarity.item()) * 100.0
        return max(0.0, min(100.0, score))
    except Exception as exc:
        logger.error("SBERT similarity failed: %s", exc, exc_info=True)
        return 0.0

