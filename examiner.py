import re

def words(text):
    return re.findall(r"\b[\w'-]+\b", text or "")

def assess_writing(text, prompt="", is_essay=False, rubric=None):
    """Transparent heuristic feedback. Not an official or AI-powered assessment."""
    tokens = words(text)
    count = len(tokens)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    paragraphs = [p.strip() for p in (text or "").splitlines() if p.strip()]
    feedback = []
    score = 0.0
    max_marks = sum(rubric.values()) if rubric else (100 if is_essay else 20)

    if count < 1:
        return {"score": 0, "feedback": ["No writing was provided."]}

    # Grammar/clarity proxies: these cannot reliably detect grammar errors.
    sentence_lengths = [len(words(s)) for s in sentences]
    avg_sentence = sum(sentence_lengths) / max(1, len(sentence_lengths))
    punctuation_ok = text.rstrip().endswith((".", "!", "?", '"', "'"))

    if is_essay:
        # Provisional distribution across the supplied practice rubric.
        score += min(20, 10 + (4 if prompt.strip() and len(text.strip()) > 500 else 0) + (3 if count >= 250 else 0))
        score += min(25, 8 + (8 if count >= 350 else 0) + (4 if count >= 500 else 0))
        score += min(20, 6 + (5 if len(paragraphs) >= 4 else 0) + (4 if len(paragraphs) >= 5 else 0))
        score += min(15, 5 + (4 if count >= 300 else 0))
        score += min(10, 6 if 12 <= avg_sentence <= 28 else 3)
        score += min(10, 6 if count >= 250 else 3)
        if count < 250:
            feedback.append(f"Your essay is {count} words. Develop your argument further with a clear thesis, supporting reasons, examples and a conclusion.")
        elif count > 1200:
            feedback.append(f"Your essay is {count} words. Check the exam's prescribed length and remove repetition.")
        else:
            feedback.append(f"Word count: {count}. Check the specific exam instructions for the expected length.")
        if len(paragraphs) < 4:
            feedback.append("Use a clear structure: introduction and thesis, separate argument paragraphs, counterargument where relevant, and conclusion.")
        else:
            feedback.append(f"You used {len(paragraphs)} non-empty paragraphs. Ensure each paragraph develops one main point.")
        if prompt.strip():
            feedback.append("Before submission, verify that every major paragraph directly answers the topic and supports your thesis.")
        else:
            feedback.append("Add the exact essay topic so relevance to the question can be assessed more meaningfully.")
    else:
        score += min(5, 2 + (2 if count >= 20 else 0) + (1 if count >= 35 else 0))
        score += min(4, 2 + (1 if count <= 0.65 * max(1, len(words(prompt))) else 0) + (1 if count >= 15 else 0))
        score += min(4, 2 + (1 if punctuation_ok else 0) + (1 if 8 <= avg_sentence <= 25 else 0))
        score += min(4, 2 + (1 if len(sentences) >= 2 else 0) + (1 if len(paragraphs) >= 1 else 0))
        score += min(3, 1 + (2 if re.search(r"(?im)^\s*(title|heading)\s*:", text) else 0))
        if prompt.strip():
            source_count = len(words(prompt))
            if count > 0.75 * max(1, source_count):
                feedback.append("Your precis may be too close to the source length. Remove examples, repetition and secondary details while preserving the central argument.")
            elif count < 0.15 * max(1, source_count):
                feedback.append("Your precis may be too short to preserve the passage's main reasoning. Check that no essential idea is missing.")
            else:
                feedback.append(f"Your precis has {count} words; the source has {source_count}. Confirm the required length and word limit from your exam instructions.")
        else:
            feedback.append("Paste the original passage to assess whether the precis preserves the central idea and avoids unnecessary details.")
        if not re.search(r"(?im)^\s*(title|heading)\s*:", text):
            feedback.append("Add a concise, accurate title if your task requires one.")
        if count and not punctuation_ok:
            feedback.append("Review punctuation and ensure the final sentence is complete.")
        feedback.append("Use your own words, preserve the author's central idea, and avoid inserting personal opinions.")

    if not punctuation_ok:
        feedback.append("The submission does not end with conventional sentence punctuation; check the final sentence.")
    if avg_sentence > 35:
        feedback.append("Several sentences may be too long. Split complex sentences and make each claim easier to follow.")
    if avg_sentence < 6 and len(sentences) > 2:
        feedback.append("Many sentences are very short. Improve flow by combining related ideas where appropriate.")
    if not feedback:
        feedback.append("Review relevance, logical progression, sentence variety and precise word choice.")
    score = max(0, min(max_marks, round(score, 1)))
    return {"score": score, "feedback": feedback}
