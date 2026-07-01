from backend import cover_letter


def test_cover_letter_fallback_is_structured(monkeypatch):
    class DummyMessages:
        def create(self, *args, **kwargs):
            raise RuntimeError("API unavailable")

    monkeypatch.setattr(cover_letter, "client", type("C", (), {"messages": DummyMessages()})())

    profile = {
        "name": "Test User",
        "all_skills": ["python", "flask"],
        "experience_years": 3,
        "education": [{"line": "BSc Computer Science"}],
    }
    job = {
        "title": "Backend Developer",
        "company": "Acme Inc.",
        "description": "Build backend services using Python and Flask.",
    }

    result = cover_letter.generate_cover_letter(profile, job)

    assert "cover_letter" in result
    assert "subject_line" in result
    assert isinstance(result["key_selling_points"], list)
    assert isinstance(result["questions_to_prep"], list)
    assert result["subject_line"].startswith("Application for Backend Developer")
