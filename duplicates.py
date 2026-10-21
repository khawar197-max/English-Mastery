import re
import difflib

def normalize_text(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)

def find_duplicate(candidate, existing_questions, threshold=0.88):
    """Return a potential duplicate match, or None. Similarity is a warning, not proof."""
    normalized = normalize_text(candidate)
    for question in existing_questions:
        other = normalize_text(question)
        if normalized == other:
            return {"match": question, "similarity": 1.0, "exact": True}
        score = difflib.SequenceMatcher(None, normalized, other).ratio()
        if score >= threshold:
            return {"match": question, "similarity": round(score, 3), "exact": False}
    return None
