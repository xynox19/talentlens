"""
jobs.py — fetch live jobs from the Adzuna API and cache them in memory.

Sign up free at https://developer.adzuna.com/ to get APP_ID + APP_KEY.
Set them as environment variables:
    ADZUNA_APP_ID=your_id
    ADZUNA_APP_KEY=your_key
"""
import os, requests, time
from datetime import datetime

ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
BASE_URL       = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

# In-memory cache: { "query|location": { jobs: [...], fetched_at: ts } }
_cache: dict = {}


def fetch_jobs(query="data engineer", location="London", results_per_page=20) -> list:
    """Fetch jobs from Adzuna and store in cache. Returns list of job dicts."""
    cache_key = f"{query}|{location}"

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        # Return realistic mock data when no API key is set
        _cache[cache_key] = {"jobs": _mock_jobs(query, location), "fetched_at": time.time()}
        return _cache[cache_key]["jobs"]

    params = {
        "app_id":          ADZUNA_APP_ID,
        "app_key":         ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what":            query,
        "where":           location,
        "content-type":    "application/json",
        "sort_by":         "date",
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        raw_jobs = resp.json().get("results", [])
    except Exception as e:
        print(f"[jobs] Adzuna fetch failed: {e} — falling back to mock data")
        _cache[cache_key] = {"jobs": _mock_jobs(query, location), "fetched_at": time.time()}
        return _cache[cache_key]["jobs"]

    jobs = []
    for r in raw_jobs:
        jobs.append({
            "id":          r.get("id"),
            "title":       r.get("title", ""),
            "company":     r.get("company", {}).get("display_name", ""),
            "location":    r.get("location", {}).get("display_name", ""),
            "salary_min":  r.get("salary_min"),
            "salary_max":  r.get("salary_max"),
            "description": r.get("description", ""),
            "url":         r.get("redirect_url", ""),
            "posted":      r.get("created", ""),
            "category":    r.get("category", {}).get("label", ""),
        })

    _cache[cache_key] = {"jobs": jobs, "fetched_at": time.time()}
    return jobs


def get_cached_jobs(query="data engineer", location="London") -> dict:
    """Return cached jobs with metadata, fetching fresh if cache is empty."""
    cache_key = f"{query}|{location}"
    if cache_key not in _cache:
        fetch_jobs(query, location)

    entry = _cache.get(cache_key, {})
    fetched_at = entry.get("fetched_at", 0)
    return {
        "jobs":        entry.get("jobs", []),
        "count":       len(entry.get("jobs", [])),
        "fetched_at":  datetime.fromtimestamp(fetched_at).isoformat() if fetched_at else None,
        "next_refresh": int(300 - (time.time() - fetched_at)) if fetched_at else 0,
        "query":       query,
        "location":    location,
    }


def _mock_jobs(query: str, location: str) -> list:
    """Realistic placeholder data used when no Adzuna credentials are set."""
    templates = [
        {
            "id": "mock-1",
            "title": "Junior Data Engineer",
            "company": "Revolut",
            "location": location,
            "salary_min": 38000,
            "salary_max": 50000,
            "description": "Build and maintain scalable data pipelines using Python, Spark, and Airflow. Work with SQL, dbt, and cloud infrastructure (AWS). Strong Python and SQL required.",
            "url": "https://www.adzuna.co.uk",
            "posted": datetime.utcnow().isoformat(),
            "category": "IT Jobs",
        },
        {
            "id": "mock-2",
            "title": "Data Analyst",
            "company": "HSBC Technology",
            "location": location,
            "salary_min": 32000,
            "salary_max": 45000,
            "description": "Analyse large datasets using Python and SQL. Build dashboards in PowerBI and Tableau. Experience with machine learning models is a plus.",
            "url": "https://www.adzuna.co.uk",
            "posted": datetime.utcnow().isoformat(),
            "category": "IT Jobs",
        },
        {
            "id": "mock-3",
            "title": "ML Engineer (Graduate)",
            "company": "Palantir Technologies",
            "location": location,
            "salary_min": 55000,
            "salary_max": 70000,
            "description": "Deploy machine learning models into production. Python, TensorFlow/PyTorch, Docker required. Knowledge of data pipelines and REST APIs essential.",
            "url": "https://www.adzuna.co.uk",
            "posted": datetime.utcnow().isoformat(),
            "category": "IT Jobs",
        },
        {
            "id": "mock-4",
            "title": "Backend Python Developer",
            "company": "Monzo",
            "location": location,
            "salary_min": 42000,
            "salary_max": 58000,
            "description": "Build microservices in Python/Flask. Strong SQL, Docker, and REST API design skills needed. Experience with cloud (AWS/GCP) preferred.",
            "url": "https://www.adzuna.co.uk",
            "posted": datetime.utcnow().isoformat(),
            "category": "IT Jobs",
        },
        {
            "id": "mock-5",
            "title": "Cybersecurity Analyst",
            "company": "BAE Systems Applied Intelligence",
            "location": location,
            "salary_min": 35000,
            "salary_max": 48000,
            "description": "Perform vulnerability assessments and penetration testing. Python scripting for automation. Familiarity with SIEM tools and threat modelling.",
            "url": "https://www.adzuna.co.uk",
            "posted": datetime.utcnow().isoformat(),
            "category": "IT Jobs",
        },
    ]
    return templates
