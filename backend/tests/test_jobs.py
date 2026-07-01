import os
from backend import jobs


def test_mock_jobs_are_returned_without_keys(monkeypatch):
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    jobs._cache.clear()

    fetched = jobs.fetch_jobs(query="data analyst", location="London")

    assert isinstance(fetched, list)
    assert fetched, "Mock jobs should be returned when no Adzuna keys are configured"
    assert all(isinstance(job.get("id"), str) for job in fetched)


def test_get_cached_jobs_returns_metadata(monkeypatch):
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    jobs._cache.clear()

    result = jobs.get_cached_jobs(query="software engineer", location="London")

    assert "jobs" in result
    assert "count" in result
    assert "fetched_at" in result
    assert result["query"] == "software engineer"
    assert result["location"] == "London"
