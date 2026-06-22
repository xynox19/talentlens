from flask import Flask, request, jsonify
from flask_cors import CORS
import threading, time, os
from jobs import fetch_jobs, get_cached_jobs
from cv_parser import parse_cv, score_job_match
from cover_letter import generate_cover_letter

app = Flask(__name__)
CORS(app)

# ── background job refresh every 5 minutes ──────────────────────────────────
def refresh_loop():
    while True:
        try:
            fetch_jobs()
            print("[talentlens] jobs refreshed")
        except Exception as e:
            print(f"[talentlens] refresh error: {e}")
        time.sleep(300)  # 5 minutes

threading.Thread(target=refresh_loop, daemon=True).start()


# ── routes ───────────────────────────────────────────────────────────────────

@app.route("/api/jobs")
def jobs():
    """Return cached jobs, optionally filtered by query/location."""
    query    = request.args.get("q", "data engineer")
    location = request.args.get("location", "London")
    cached   = get_cached_jobs(query, location)
    return jsonify(cached)


@app.route("/api/parse-cv", methods=["POST"])
def upload_cv():
    """
    Accept a PDF or plain-text CV.
    Returns extracted skills + candidate profile.
    """
    if "file" in request.files:
        file = request.files["file"]
        text = file.read().decode("utf-8", errors="ignore")
    elif request.is_json:
        text = request.json.get("text", "")
    else:
        return jsonify({"error": "Send a file or JSON {text}"}), 400

    profile = parse_cv(text)
    return jsonify(profile)


@app.route("/api/match", methods=["POST"])
def match():
    """
    Score a list of jobs against a candidate profile.
    Body: { profile: {...}, jobs: [...] }
    """
    data    = request.json
    profile = data.get("profile", {})
    jobs_in = data.get("jobs", [])
    scored  = [score_job_match(profile, job) for job in jobs_in]
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored)


@app.route("/api/cover-letter", methods=["POST"])
def cover_letter():
    """
    Generate a tailored cover letter.
    Body: { profile: {...}, job: {...} }
    """
    data    = request.json
    profile = data.get("profile", {})
    job     = data.get("job", {})
    result  = generate_cover_letter(profile, job)
    return jsonify(result)


if __name__ == "__main__":
    # initial fetch on startup
    fetch_jobs()
    app.run(debug=True, port=5000)
