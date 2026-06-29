LABEL_TEXT = {
    "likely_ai": "This submission appears likely to be AI-generated based on multiple writing signals.",
    "likely_human": "This submission appears likely to be written by a human based on multiple writing signals.",
    "uncertain": "The system found mixed signals in the writing, making it hard to label and it cannot confidently determine if this submission was written by a human or AI-generated.",
    "pending": "The system could not generate a transparency label because one or more detection signals did not return a score.",
}


def generate_label(confidence):
    """Map a confidence score to an attribution category and label text."""
    if confidence is None:
        attribution = "pending"
    elif confidence >= 0.70:
        attribution = "likely_ai"
    elif confidence <= 0.30:
        attribution = "likely_human"
    else:
        attribution = "uncertain"

    return {
        "attribution": attribution,
        "text": LABEL_TEXT[attribution],
    }
