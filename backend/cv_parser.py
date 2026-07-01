"""
cv_parser.py — extract skills, experience, and education from CV text.
Uses keyword matching + optional spaCy NER for name/org extraction.
Also scores a candidate profile against a job description.
"""
import re
from typing import Any

# ── master skill taxonomy ────────────────────────────────────────────────────
SKILL_GROUPS = {
    "languages": [
        "python", "c++", "javascript", "typescript", "java", "go", "rust",
        "sql", "r", "scala", "php", "html", "css", "matlab", "assembly",
        "bash", "shell",
    ],
    "data_engineering": [
        "spark", "apache spark", "kafka", "airflow", "dbt", "hadoop", "flink",
        "luigi", "prefect", "databricks", "snowflake", "bigquery", "redshift",
        "etl", "data pipeline", "data warehouse", "datalake", "delta lake",
    ],
    "ml_ai": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "sklearn", "nlp", "computer vision", "llm",
        "neural network", "ann", "reinforcement learning", "xgboost",
        "huggingface", "transformers", "pandas", "numpy",
    ],
    "cloud_devops": [
        "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform",
        "ci/cd", "github actions", "jenkins", "linux", "debian", "kali",
        "virtualbox", "nginx",
    ],
    "databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "oracle", "cassandra", "dynamodb", "neo4j",
    ],
    "web_frameworks": [
        "flask", "django", "fastapi", "react", "vue", "angular", "node",
        "express", "next.js", "rest api", "graphql",
    ],
    "tools": [
        "git", "github", "docker", "figma", "powerbi", "tableau", "jira",
        "confluence", "vscode", "jupyter", "solidworks", "blender",
        "rapidminer", "altair", "dbt", "postman", "mqtt",
    ],
    "security": [
        "penetration testing", "pentest", "vulnerability", "siem", "ctem",
        "threat modelling", "cybersecurity", "cryptography", "owasp",
        "burp suite", "wireshark", "metasploit", "nmap",
    ],
}

ALL_SKILLS = {skill for group in SKILL_GROUPS.values() for skill in group}


def parse_cv(text: str) -> dict:
    """
    Extract a structured profile from raw CV text.
    Returns a dict with: name, email, skills (grouped), experience_years, raw_text.
    """
    text_lower = text.lower()

    # ── extract skills ───────────────────────────────────────────────────────
    found: dict[str, list] = {g: [] for g in SKILL_GROUPS}
    for group, skills in SKILL_GROUPS.items():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found[group].append(skill)

    all_found = sorted({s for group_skills in found.values() for s in group_skills})

    # ── extract email ────────────────────────────────────────────────────────
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group(0) if email_match else ""

    # ── extract name (first non-empty line heuristic) ────────────────────────
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if lines else ""

    # ── estimate years of experience from date ranges ────────────────────────
    years = _estimate_experience_years(text)

    # ── extract education ────────────────────────────────────────────────────
    edu = _extract_education(text)

    return {
        "name":             name,
        "email":            email,
        "skills":           found,
        "all_skills":       all_found,
        "skill_count":      len(all_found),
        "experience_years": years,
        "education":        edu,
        "raw_text":         text,
    }


def score_job_match(profile: dict, job: dict) -> dict:
    """
    Score a job against a candidate profile (0–100).
    Adds match_score, matched_skills, missing_skills to the job dict.
    """
    description = (job.get("description", "") + " " + job.get("title", "")).lower()

    # skills demanded by the JD
    demanded = set()
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, description):
            demanded.add(skill)

    candidate_skills = set(s.lower() for s in profile.get("all_skills", []))

    matched = demanded & candidate_skills
    missing = demanded - candidate_skills

    score = int((len(matched) / max(len(demanded), 1)) * 100)

    return {
        **job,
        "match_score":    score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "demanded_count": len(demanded),
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def _estimate_experience_years(text: str) -> float:
    """Rough heuristic: infer experience from year ranges and common phrases."""
    text_lower = text.lower()
    years = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
    if len(years) >= 2:
        years_int = sorted(set(int(y) for y in years))
        span = years_int[-1] - years_int[0]
        return round(min(span, 15), 1)

    match = re.search(r'(\d+)\+?\s+years? of experience', text_lower)
    if match:
        return float(match.group(1))

    if "senior" in text_lower:
        return 5.0
    if "junior" in text_lower or "graduate" in text_lower:
        return 1.0

    return 0.0


def _extract_education(text: str) -> list[dict]:
    """Extract degree/institution pairs by simple keyword proximity."""
    degrees = ["bsc", "msc", "ba", "ma", "phd", "bachelor", "master", "degree"]
    results = []
    for line in text.split("\n"):
        line_lower = line.lower()
        if any(d in line_lower for d in degrees):
            results.append({"line": line.strip()})
    return results[:3]
