# ProvenanceGuard

ProvenanceGuard is a Flask prototype for classifying submitted text as likely AI-generated, likely human-written, or uncertain. The system combines an LLM classifier with stylometric heuristics, produces a confidence score, displays a transparency label, logs submission events, and supports appeal intake.

## Architecture Overview

Describe the path a submission takes through the system:

```text
POST /submit
  -> validate text and creator_id
  -> run LLM classifier signal
  -> run stylometric heuristics signal
  -> combine signal scores into confidence score
  -> map confidence score to transparency label
  -> save submission state
  -> write audit log entry
  -> return JSON response
```

Fill in:

- Input format:
- Output format:
- Where submissions are stored:
- Where audit events are logged:
- How appeals fit into the architecture:

## Detection Signals

### Signal 1: LLM Classifier

What it measures:

- 

Why I chose it:

- 

What it misses:

- 

### Signal 2: Stylometric Heuristics

What it measures:

- Sentence length variation:
- Type-token ratio:
- Punctuation density:

Why I chose it:

- 

What it misses:

- 

## Confidence Scoring

The system combines the two signal scores into one confidence score.

Current formula:

```text
confidence = (0.7 * llm_classifier_score) + (0.3 * stylometric_heuristics_score)
```

Explain why this weighting was chosen:

- 

Explain how I validated that the score was meaningful:

- 

### Example: High-Confidence Result

Submission summary:

```text
[Paste or summarize example text here]
```

Actual scores:

```text
LLM classifier:
Stylometric heuristics:
Final confidence:
Attribution:
```

Why this result makes sense:

- 

### Example: Lower-Confidence Result

Submission summary:

```text
[Paste or summarize example text here]
```

Actual scores:

```text
LLM classifier:
Stylometric heuristics:
Final confidence:
Attribution:
```

Why this result makes sense:

- 

## Transparency Labels

The system maps confidence scores to three user-facing transparency labels.

### High-Confidence AI

Threshold:

```text
0.70 - 1.00
```

Exact label text:

```text
This submission appears likely to be AI-generated based on multiple writing signals.
```

### High-Confidence Human

Threshold:

```text
0.00 - 0.30
```

Exact label text:

```text
This submission appears likely to be written by a human based on multiple writing signals.
```

### Uncertain

Threshold:

```text
0.31 - 0.69
```

Exact label text:

```text
The system found mixed signals in the writing, making it hard to label and it cannot confidently determine if this submission was written by a human or AI-generated.
```

Optional screenshot or mockup:

- 

## Rate Limiting

Chosen limit:

```text
POST /submit: 10 submissions per minute per creator_id
```

Reasoning:

- 

What this prevents:

- 

What this does not prevent:

- 

## Known Limitations

Specific content type the system may misclassify:

- 

Why the system may misclassify it:

- 

How the current design tries to reduce harm:

- 

## Spec Reflection

One way the spec helped me:

- 

One way implementation diverged from the spec and why:

- 

## AI Usage

### Instance 1

What I directed the AI to do:

- 

What I revised or overrode:

- 

### Instance 2

What I directed the AI to do:

- 

What I revised or overrode:

- 

### Additional Notes

- 
