"""
cover_letter.py — generate tailored cover letters using the Anthropic API.

Set ANTHROPIC_API_KEY as an environment variable.
"""
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


def generate_cover_letter(profile: dict, job: dict) -> dict:
    """
    Generate a personalised cover letter and application checklist.

    Returns:
        {
            "cover_letter": str,        # full letter text
            "subject_line": str,        # suggested email subject
            "key_selling_points": list, # 3 bullet points to highlight
            "questions_to_prep": list,  # likely interview questions
        }
    """
    candidate_name    = profile.get("name", "the candidate")
    candidate_skills  = ", ".join(profile.get("all_skills", [])[:20])
    candidate_exp     = profile.get("experience_years", 0)
    education         = "; ".join(e["line"] for e in profile.get("education", []))
    matched_skills    = ", ".join(job.get("matched_skills", []))
    missing_skills    = ", ".join(job.get("missing_skills", []))

    job_title   = job.get("title", "this role")
    company     = job.get("company", "the company")
    description = job.get("description", "")[:800]  # keep prompt lean

    prompt = f"""You are an expert careers advisor and professional writer.

Candidate profile:
- Name: {candidate_name}
- Skills: {candidate_skills}
- Approx. years of experience: {candidate_exp}
- Education: {education}
- Skills that match this job: {matched_skills}
- Skills the job asks for that the candidate is still learning: {missing_skills}

Job details:
- Role: {job_title} at {company}
- Description excerpt: {description}

Produce a JSON response (no markdown fences) with exactly these keys:
{{
  "cover_letter": "Full 3-paragraph cover letter. Paragraph 1: strong opening, name the role and company, hook. Paragraph 2: 2-3 specific examples from the candidate's background that match the JD. Paragraph 3: forward-looking close, enthusiasm, CTA. Tone: confident, human, not robotic. Max 280 words.",
  "subject_line": "Crisp email subject line under 10 words",
  "key_selling_points": ["point 1", "point 2", "point 3"],
  "questions_to_prep": ["likely interview question 1", "likely interview question 2", "likely interview question 3", "likely interview question 4"]
}}"""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()

        import json
        # strip stray markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
    except Exception as e:
        # Fallback: return a structured placeholder
        result = {
            "cover_letter": (
                f"Dear Hiring Team at {company},\n\n"
                f"I am writing to express my strong interest in the {job_title} position. "
                f"With a background in {candidate_skills[:120]}, I am confident I can contribute "
                f"meaningfully from day one.\n\n"
                f"[Configure your ANTHROPIC_API_KEY to generate a fully personalised letter.]\n\n"
                f"Thank you for your time. I would welcome the opportunity to discuss my application further.\n\n"
                f"Best regards,\n{candidate_name}"
            ),
            "subject_line": f"Application for {job_title} — {candidate_name}",
            "key_selling_points": [
                f"Strong match on: {matched_skills or 'core skills'}",
                f"Relevant background in data engineering and Python",
                "Proactive learner actively developing missing skills",
            ],
            "questions_to_prep": [
                "Tell me about a data pipeline you've built end-to-end.",
                "How do you handle schema changes in production pipelines?",
                "Describe a time you debugged a difficult data quality issue.",
                "Where do you see yourself in 3 years in this field?",
            ],
            "_error": str(e),
        }

    return result
