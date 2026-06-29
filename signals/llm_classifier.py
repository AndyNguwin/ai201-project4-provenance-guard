import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT_SECONDS = float(os.getenv("GROQ_TIMEOUT_SECONDS", "20"))


SYSTEM_PROMPT = """You are the first detection signal in Provenance Guard.
Classify whether submitted text is likely AI-generated or human-written.

Return only valid JSON with these fields:
- ai_score: number from 0 to 1, where 0 is very human-like and 1 is very AI-like
- rationale: one short sentence explaining the score in plain language

Focus on meaning-level and context-level evidence: semantic specificity,
contextual grounding, generic claims, neutral tone, prompt-shaped structure,
and whether the writing feels personally situated or broadly generated."""


def classify_with_llm(text):
    """Return an AI-likelihood score from the LLM classifier signal."""
    api_key = os.getenv("GROQ_API_KEY")
    if os.getenv("DISABLE_LLM_CLASSIFIER") == "1" or not api_key:
        return {
            "score": None,
            "rationale": "The LLM classifier is disabled or GROQ_API_KEY is not configured.",
        }

    try:
        client = Groq(api_key=api_key, timeout=GROQ_TIMEOUT_SECONDS)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = completion.choices[0].message.content
        parsed = json.loads(content)
        ai_score = _clamp_score(parsed.get("ai_score"))
    except Exception as exc:
        return {
            "score": None,
            "rationale": f"LLM classifier failed before returning a score: {exc.__class__.__name__}.",
        }

    return {
        "score": ai_score,
        "rationale": str(parsed.get("rationale", "")).strip(),
    }


def _clamp_score(value):
    score = float(value)
    return max(0.0, min(1.0, score))


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
        result = classify_with_llm(submitted_text)
        print(json.dumps(result, indent=2))
