from backend.cv_parser import parse_cv, score_job_match


def test_parse_cv_extracts_basic_profile():
    text = (
        "Jane Doe\n"
        "jane.doe@example.com\n"
        "Experienced Python developer with AWS and Flask.\n"
        "2018 - 2023\n"
    )

    profile = parse_cv(text)

    assert profile["name"] == "Jane Doe"
    assert profile["email"] == "jane.doe@example.com"
    assert "python" in profile["all_skills"]
    assert "flask" in profile["all_skills"]
    assert profile["experience_years"] >= 4


def test_score_job_match_with_exact_skill_match():
    profile = {"all_skills": ["python", "sql", "flask"]}
    job = {
        "title": "Python Backend Engineer",
        "description": "Build REST APIs with Python, Flask and SQL databases.",
    }

    scored = score_job_match(profile, job)

    assert scored["match_score"] == 100
    assert set(scored["matched_skills"]) == {"python", "sql", "flask"}
    assert scored["demanded_count"] == 3
