"""PhishGuard AI web application entry point."""

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from src.database import ScanRepository
from src.security_analyzer import EmailSecurityAnalyzer, extract_eml_text


ROOT = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def create_app(test_config=None):
    app = Flask(__name__)
    data_directory = Path(os.environ.get("PHISHGUARD_DATA_DIR", ROOT / "data"))
    app.config.update(
        MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
        DATABASE_PATH=data_directory / "phishguard.db",
    )
    if test_config:
        app.config.update(test_config)

    repository = ScanRepository(app.config["DATABASE_PATH"])
    analyzer = EmailSecurityAnalyzer(ROOT / "models" / "phishing_email_model.joblib")

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "img-src 'self' data:; connect-src 'self'"
        )
        return response

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.post("/api/scan")
    def scan_email():
        payload = request.get_json(silent=True) or {}
        email_text = str(payload.get("email_text", "")).strip()
        subject = str(payload.get("subject", "")).strip()
        sender = str(payload.get("sender", "")).strip()

        if len(email_text) < 12:
            return jsonify({"error": "Paste at least 12 characters of email content."}), 400
        if len(email_text) > 100_000:
            return jsonify({"error": "Email content is too large (maximum 100,000 characters)."}), 400

        result = analyzer.analyze(email_text, subject=subject, sender=sender)
        scan_id = repository.save_scan(subject, sender, email_text, result)
        return jsonify({"scan_id": scan_id, **result}), 201

    @app.post("/api/upload-eml")
    def upload_eml():
        uploaded = request.files.get("email_file")
        if not uploaded or not uploaded.filename:
            return jsonify({"error": "Choose a valid .eml email file."}), 400
        if not uploaded.filename.lower().endswith(".eml"):
            return jsonify({"error": "Only .eml files are supported."}), 400

        try:
            subject, sender, email_text = extract_eml_text(uploaded.read())
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        result = analyzer.analyze(email_text, subject=subject, sender=sender)
        scan_id = repository.save_scan(subject, sender, email_text, result)
        return jsonify({"scan_id": scan_id, **result}), 201

    @app.get("/api/history")
    def history():
        return jsonify(repository.list_scans(limit=30))

    @app.post("/api/scans/<int:scan_id>/feedback")
    def submit_feedback(scan_id):
        payload = request.get_json(silent=True) or {}
        feedback = payload.get("feedback")
        if feedback not in {"phishing", "safe"}:
            return jsonify({"error": "Feedback must be phishing or safe."}), 400
        if not repository.save_feedback(scan_id, feedback):
            return jsonify({"error": "Scan was not found."}), 404
        return jsonify({"status": "saved"})

    @app.get("/api/export")
    def export_history():
        export_path = repository.export_json(ROOT / "data" / "exports")
        return send_file(export_path, as_attachment=True, download_name="phishguard_scan_history.json")

    @app.errorhandler(413)
    def file_too_large(_error):
        return jsonify({"error": "Upload exceeds the 2 MB limit."}), 413

    return app


if __name__ == "__main__":
    create_app().run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
    )
