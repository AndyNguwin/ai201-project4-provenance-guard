import json

from scoring import attribution_from_confidence, combine_signal_scores
from signals.llm_classifier import classify_with_llm
from signals.stylometric_heuristics import analyze_stylometry


def classify_text(text):
    llm_result = classify_with_llm(text)
    stylometric_result = analyze_stylometry(text)
    confidence = combine_signal_scores(
        llm_result["score"],
        stylometric_result["score"],
    )
    attribution = attribution_from_confidence(confidence)

    return {
        "llm_classifier": llm_result["score"],
        "stylometric_heuristics": stylometric_result["score"],
        "confidence": confidence,
        "attribution": attribution,
        "details": {
            "llm_classifier": llm_result,
            "stylometric_heuristics": stylometric_result,
        },
    }


if __name__ == "__main__":
    print("Paste text to classify. Press Enter twice when finished.")

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
        print(json.dumps(classify_text(submitted_text), indent=2))
