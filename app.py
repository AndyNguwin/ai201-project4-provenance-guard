import os
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from audit_log import get_log, write_log
from scoring import attribution_from_confidence, combine_signal_scores
from signals.llm_classifier import classify_with_llm
from signals.stylometric_heuristics import analyze_stylometry


load_dotenv()


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/log")
    def read_log():
        return jsonify({"entries": get_log()})

    @app.post("/submit")
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
        attribution = attribution_from_confidence(confidence)

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
        }
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
            }
        )

        return jsonify(response), 202

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
