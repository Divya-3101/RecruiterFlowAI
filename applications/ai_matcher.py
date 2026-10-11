import os
import math
import re
import logging
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """
    Lazy initialization of Gemini client so missing API keys do not crash
    the application at import time.
    """
    global _client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    if _client is None:
        try:
            from google import genai
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Could not initialize Google GenAI client: {e}")
            _client = None

    return _client


def cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def fallback_text_similarity(text_a, text_b):
    """
    Fallback semantic text similarity using term-frequency cosine similarity.
    Ensures system continues to work smoothly even when offline or when
    GEMINI_API_KEY is not configured.
    """
    if not text_a or not text_b:
        return 0.0

    words_a = re.findall(r"\b[a-zA-Z0-9+#.-]{2,}\b", text_a.lower())
    words_b = re.findall(r"\b[a-zA-Z0-9+#.-]{2,}\b", text_b.lower())

    if not words_a or not words_b:
        return 0.0

    freq_a = Counter(words_a)
    freq_b = Counter(words_b)

    all_words = set(freq_a.keys()).union(set(freq_b.keys()))
    vec_a = [freq_a.get(w, 0) for w in all_words]
    vec_b = [freq_b.get(w, 0) for w in all_words]

    similarity = cosine_similarity(vec_a, vec_b)
    # Scale slightly for typical resume-job overlap distribution
    return max(0.0, min(1.0, similarity * 1.25))


def generate_embedding(text):
    if not text or not text.strip():
        return []

    client = get_client()
    if client is None:
        return None

    try:
        # Use first 4000 characters to stay within content embedding token limits
        trimmed_text = text[:4000]
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=trimmed_text
        )
        if response and response.embeddings:
            return response.embeddings[0].values
    except Exception as e:
        logger.warning(f"Gemini embedding API call failed: {e}. Using fallback similarity.")
        return None

    return None


def calculate_semantic_score(resume_text, job_text):
    """
    Calculates semantic similarity between resume and job description.
    Uses Gemini embeddings when available, and falls back to term-frequency
    similarity if the API is offline or unconfigured.
    """
    if not resume_text or not job_text:
        return 0.0

    resume_embedding = generate_embedding(resume_text)
    job_embedding = generate_embedding(job_text)

    if resume_embedding and job_embedding:
        similarity = cosine_similarity(resume_embedding, job_embedding)
    else:
        similarity = fallback_text_similarity(resume_text, job_text)

    score = max(0.0, min(100.0, similarity * 100))
    return round(score, 2)