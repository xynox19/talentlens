# TalentLens 🔍
> Real-time job market intelligence — live job search, CV skill matching, and AI-generated cover letters.

Built with Python/Flask · Adzuna API · Claude API · Vanilla React

---

## Features

- **Live job feed** — fetches fresh jobs from Adzuna every 5 minutes automatically
- **CV parsing** — upload your PDF/text CV; extracts 80+ skills across 8 categories
- **Skill match scoring** — every job is scored 0–100% against your CV profile
- **AI cover letters** — one click generates a tailored letter + interview prep questions using Claude
- **Dark, minimal dashboard UI** — ready to screenshot for your portfolio

---

## Quick start

### 1. Get free API keys

| Service | Where | Free tier |
|---|---|---|
| Adzuna | https://developer.adzuna.com/ | 250 req/day |
| Anthropic | https://console.anthropic.com/ | $5 credit |

### 2. Backend

```bash
cd backend
cp .env.example .env
# fill in ADZUNA_APP_ID, ADZUNA_APP_KEY, ANTHROPIC_API_KEY

pip install -r requirements.txt
python app.py
# → running on http://localhost:5000
```

### 3. Frontend

Open `frontend/index.html` directly in your browser — no build step needed.

Or serve it:
```bash
cd frontend
python -m http.server 3000
# → http://localhost:3000
```

> **No API keys?** The app runs in demo mode with realistic mock data — fully functional for portfolio demos.

---

## Project structure

```
talentlens/
├── backend/
│   ├── app.py           # Flask API + background refresh loop
│   ├── jobs.py          # Adzuna job fetching + in-memory cache
│   ├── cv_parser.py     # Skill extraction + job match scoring
│   ├── cover_letter.py  # Claude API cover letter generation
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html       # Full React SPA (no build step)
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jobs?q=...&location=...` | Live job feed (cached, refreshes every 5min) |
| POST | `/api/parse-cv` | Parse CV text/PDF → structured profile |
| POST | `/api/match` | Score jobs against candidate profile |
| POST | `/api/cover-letter` | Generate cover letter + interview prep |

---

## Deploying to Render (free)

1. Push to GitHub
2. Create a new **Web Service** on https://render.com
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `gunicorn backend.app:app`
5. Add environment variables in Render dashboard
6. Deploy frontend to GitHub Pages (just push `frontend/index.html` and update `API` constant to your Render URL)

---

## CV line

> **TalentLens** — Full-stack job market intelligence platform. Python/Flask REST API with background ETL pipeline ingesting live job data every 5 minutes via Adzuna API. NLP-based CV skill extraction engine scoring 80+ skills across 8 domains. Integrated Claude LLM for personalised cover letter generation. Deployed on Render with a zero-build React frontend.
