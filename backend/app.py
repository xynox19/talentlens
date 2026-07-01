from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import logging
import os
import threading
import time

from jobs import fetch_jobs, get_cached_jobs
from cv_parser import parse_cv, score_job_match
from cover_letter import generate_cover_letter

load_dotenv()

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

# ── background job refresh every 5 minutes ──────────────────────────────────
def refresh_loop():
    while True:
        try:
            fetch_jobs()
            app.logger.info("[talentlens] jobs refreshed")
        except Exception as e:
            app.logger.error(f"[talentlens] refresh error: {e}")
        time.sleep(300)  # 5 minutes

threading.Thread(target=refresh_loop, daemon=True, name="job-refresh").start()


# ── routes ───────────────────────────────────────────────────────────────────

@app.route("/api/jobs")
def jobs():
    """Return cached jobs, optionally filtered by query/location."""
    query    = request.args.get("q", "data engineer")
    location = request.args.get("location", "London")
    cached   = get_cached_jobs(query, location)
    return jsonify(cached)


def _extract_text_from_file(file):
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            app.logger.error(f"PDF parse error: {e}")
            return ""

    return file.read().decode("utf-8", errors="ignore")


@app.route("/api/parse-cv", methods=["POST"])
def upload_cv():
    """
    Accept a PDF or plain-text CV.
    Returns extracted skills + candidate profile.
    """
    if "file" in request.files:
        file = request.files["file"]
        text = _extract_text_from_file(file)
    elif request.is_json:
        text = (request.get_json(silent=True) or {}).get("text", "")
    else:
        return jsonify({"error": "Send a file or JSON {text}"}), 400

    if not text or not text.strip():
        return jsonify({"error": "Unable to extract text from the uploaded CV. Try a plain text file or a readable PDF."}), 400

    profile = parse_cv(text)
    return jsonify(profile)


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok", "service": "TalentLens"})


@app.route("/api/match", methods=["POST"])
def match():
    """
    Score a list of jobs against a candidate profile.
    Body: { profile: {...}, jobs: [...] }
    """
    data = request.get_json(silent=True) or {}
    profile = data.get("profile", {})
    jobs_in = data.get("jobs", [])
    if not isinstance(jobs_in, list):
        return jsonify({"error": "`jobs` must be a list."}), 400
    scored = [score_job_match(profile, job) for job in jobs_in]
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored)


@app.route("/api/cover-letter", methods=["POST"])
def cover_letter():
    """
    Generate a tailored cover letter.
    Body: { profile: {...}, job: {...} }
    """
    data = request.get_json(silent=True) or {}
    profile = data.get("profile", {})
    job = data.get("job", {})
    if not profile or not job:
        return jsonify({"error": "Provide both `profile` and `job` in request body."}), 400
    result = generate_cover_letter(profile, job)
    return jsonify(result)


if __name__ == "__main__":
    # initial fetch on startup
    fetch_jobs()
    app.run(debug=True, port=5000)
