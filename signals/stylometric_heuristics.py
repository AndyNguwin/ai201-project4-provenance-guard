import math
import json
import re
import string
from statistics import mean, pstdev


WORD_RE = re.compile(r"\b[\w']+\b")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")
PUNCTUATION = set(string.punctuation)


def analyze_stylometry(text):
    """Return a 0-1 AI-likelihood score from stylometric heuristics."""
    words = _words(text)
    sentences = _sentences(text)

    if not words:
        return {
            "score": None,
            "rationale": "Stylometric heuristics could not run because there were no words to analyze.",
            "measurements": {},
            "sub_scores": {},
        }

    sentence_lengths = [_word_count(sentence) for sentence in sentences]
    sentence_lengths = [length for length in sentence_lengths if length > 0]

    sentence_variation = _sentence_length_cv(sentence_lengths)
    type_token_ratio = len(set(words)) / len(words)
    punctuation_density = _punctuation_count(text) / len(words)

    sentence_score = _score_low_is_ai(sentence_variation, human_like=0.60)
    ttr_score = _score_ttr(type_token_ratio)
    punctuation_score = _score_high_is_ai(
        punctuation_density,
        human_like=0.05,
        ai_like=0.20,
    )

    score = round(
        (0.4 * sentence_score)
        + (0.4 * ttr_score)
        + (0.2 * punctuation_score),
        3,
    )

    return {
        "score": score,
        "rationale": "Stylometric score uses sentence variation, vocabulary diversity, and punctuation density, with punctuation weighted lower because it varies by writing style.",
        "measurements": {
            "sentence_length_cv": round(sentence_variation, 3),
            "type_token_ratio": round(type_token_ratio, 3),
            "punctuation_density": round(punctuation_density, 3),
        },
        "sub_scores": {
            "sentence_variation": round(sentence_score, 3),
            "type_token_ratio": round(ttr_score, 3),
            "punctuation_density": round(punctuation_score, 3),
        },
    }


def _words(text):
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def _sentences(text):
    return [sentence.strip() for sentence in SENTENCE_RE.findall(text) if sentence.strip()]


def _word_count(text):
    return len(_words(text))


def _punctuation_count(text):
    return sum(1 for char in text if char in PUNCTUATION)


def _sentence_length_cv(sentence_lengths):
    if len(sentence_lengths) < 2:
        return 0.0

    average_length = mean(sentence_lengths)
    if math.isclose(average_length, 0.0):
        return 0.0

    return pstdev(sentence_lengths) / average_length


def _score_low_is_ai(raw_value, human_like, ai_like=0.0):
    return _clamp((human_like - raw_value) / (human_like - ai_like))


def _score_high_is_ai(raw_value, human_like, ai_like):
    return _clamp((raw_value - human_like) / (ai_like - human_like))


def _score_ttr(type_token_ratio):
    low_ttr_score = _score_low_is_ai(type_token_ratio, human_like=0.55, ai_like=0.30)
    high_ttr_score = _score_high_is_ai(type_token_ratio, human_like=0.75, ai_like=0.95)
    return max(low_ttr_score, high_ttr_score)


def _clamp(value):
    return max(0.0, min(1.0, value))


if __name__ == "__main__":
    print("Paste text to analyze. Press Enter twice when finished.")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    submitted_text = "\n".join(lines).strip()
    if not submitted_text:
        print("No text submitted.")
    else:
        result = analyze_stylometry(submitted_text)
        print(json.dumps(result, indent=2))
