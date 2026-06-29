def combine_signal_scores(llm_score, stylometric_score):
    """Combine AI-likelihood signals into one confidence score."""
    if llm_score is None or stylometric_score is None:
        return None

    return round((0.7 * llm_score) + (0.3 * stylometric_score), 3)


def attribution_from_confidence(confidence):
    if confidence is None:
        return "pending"
    if confidence >= 0.70:
        return "likely_ai"
    if confidence <= 0.30:
        return "likely_human"
    return "uncertain"
