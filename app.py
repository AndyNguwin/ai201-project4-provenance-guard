import os
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_limiter import Limiter

from audit_log import get_log, write_log
from labels import generate_label
from scoring import combine_signal_scores
from signals.llm_classifier import classify_with_llm
from signals.stylometric_heuristics import analyze_stylometry
from submission_store import get_submission, save_submission, update_submission_status


load_dotenv()


def creator_id_rate_limit_key():
    payload = request.get_json(silent=True) or {}
    creator_id = payload.get("creator_id")
    if isinstance(creator_id, str) and creator_id.strip():
        return creator_id.strip()

    return request.remote_addr or "anonymous"


def create_app():
    app = Flask(__name__)
    limiter = Limiter(
        key_func=creator_id_rate_limit_key,
        storage_uri="memory://",
    )
    limiter.init_app(app)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/log")
    def read_log():
        return jsonify({"entries": get_log()})

    @app.post("/submit")
    @limiter.limit("10 per minute")
    def submit_text():
        payload = request.get_json(silent=True) or {}
        raw_text = payload.get("text", "")
        creator_id = payload.get("creator_id", "")

        if not isinstance(raw_text, str) or not raw_text.strip():
            return jsonify({"error": "Request JSON must include a non-empty text field."}), 400
        if not isinstance(creator_id, str) or not creator_id.strip():
            return jsonify({"error": "Request JSON must include a non-empty creator_id field."}), 400

        content_id = str(uuid4())
        llm_result = classify_with_llm(raw_text)
        stylometric_result = analyze_stylometry(raw_text)
        confidence = combine_signal_scores(
            llm_result["score"],
            stylometric_result["score"],
        )
        transparency_label = generate_label(confidence)
        attribution = transparency_label["attribution"]

        timestamp = datetime.now(timezone.utc).isoformat()
        
        response = {
            "content_id": content_id,
            "creator_id": creator_id.strip(),
            "status": "classified",
            "timestamp": timestamp,
            "llm_classifier": llm_result["score"],
            "stylometric_heuristics": stylometric_result["score"],
            "confidence": confidence,
            "attribution": attribution,
            "transparency_label": transparency_label["text"],
        }

        save_submission(response)

        write_log(
            {
                "event_type": "submission",
                "content_id": content_id,
                "creator_id": creator_id.strip(),
                "timestamp": timestamp,
                "attribution": attribution,
                "llm_classifier_score": llm_result["score"],
                "stylometric_heuristics_score": stylometric_result["score"],
                "confidence": confidence,
                "transparency_label": transparency_label["text"],
            }
        )

        return jsonify(response), 202

    @app.post("/appeal")
    def submit_appeal():
        payload = request.get_json(silent=True) or {}
        content_id = payload.get("content_id", "")
        creator_reasoning = payload.get("creator_reasoning", "")

        if not isinstance(content_id, str) or not content_id.strip():
            return jsonify({"error": "Request JSON must include a non-empty content_id field."}), 400
        if not isinstance(creator_reasoning, str) or not creator_reasoning.strip():
            return jsonify({"error": "Request JSON must include a non-empty creator_reasoning field."}), 400

        submission = get_submission(content_id.strip())
        if submission is None:
            return jsonify({"error": "No submission found for the provided content_id."}), 404

        appeal_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        updated_status = "under_review"
        original_classification = submission.get("attribution")
        updated_submission = update_submission_status(content_id.strip(), updated_status)

        write_log(
            {
                "event_type": "appeal",
                "appeal_id": appeal_id,
                "content_id": content_id.strip(),
                "creator_id": submission.get("creator_id"),
                "timestamp": timestamp,
                "status": updated_status,
                "original_classification": original_classification,
                "appeal_reasoning": creator_reasoning.strip(),
            }
        )

        return jsonify(
            {
                "appeal_id": appeal_id,
                "content_id": content_id.strip(),
                "status": updated_submission["status"],
                "original_classification": original_classification,
                "message": "Appeal received and submission status updated to under review.",
            }
        ), 202

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
