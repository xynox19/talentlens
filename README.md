# TalentLens 🔍
> Real-time job market intelligence — live job search, CV skill matching, and AI-generated cover letters.

Built with Python/Flask · Adzuna API · Anthropic Claude · Vanilla React

---

## Features

- **Live job feed** — fetches fresh roles from Adzuna and caches them locally
- **Persistent cache** — job results are saved to SQLite so the app stays fast after restart
- **CV parsing** — upload text or PDF CVs; extracts skills, experience, email, and education
- **Skill match scoring** — jobs are ranked by relevance to the candidate profile
- **AI cover letters** — tailored letters, subject lines, prep questions, and selling points
- **Offline-friendly demo mode** — works without API keys using realistic mock data
- **Deployment-ready** — includes Docker support and GitHub Actions CI

---

## Quick start

### 1. Get API keys

| Service | Where | Free tier |
|---|---|---|
| Adzuna | https://developer.adzuna.com/ | 250 req/day |
| Anthropic | https://console.anthropic.com/ | free credit |

### 2. Backend

```bash
cd backend
cp .env.example .env
# fill in ADZUNA_APP_ID, ADZUNA_APP_KEY, and ANTHROPIC_API_KEY if available

pip install -r requirements.txt
python app.py
# → running on http://localhost:5000
```

### 3. Frontend

Open `frontend/index.html` directly in your browser — no build step needed.

Or serve it locally:

```bash
cd frontend
python -m http.server 3000
# → http://localhost:3000
```

> **No API keys?** The backend falls back to mock job data and placeholder cover letters.

---

## Project structure

```
talentlens/
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── jobs.py
│   ├── cv_parser.py
│   ├── cover_letter.py
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
├── frontend/
│   └── index.html
├── backend/Dockerfile
├── .dockerignore
└── .github/workflows/ci.yml
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jobs?q=...&location=...` | Live job feed (cached and persisted) |
| POST | `/api/parse-cv` | Parse CV text or PDF → structured profile |
| POST | `/api/match` | Score jobs against candidate profile |
| POST | `/api/cover-letter` | Generate personalized cover letter + prep guide |
| GET | `/api/health` | Health check |

---

## Testing

```bash
pytest backend/tests
```

---

## Docker

Build and run the backend with Docker:

```bash
docker build -t talentlens-backend -f backend/Dockerfile backend
docker run --rm -p 5000:5000 talentlens-backend
```

---

## Deploying to Render

1. Push to GitHub
2. Create a new **Web Service** on https://render.com
3. Set the build command to `pip install -r backend/requirements.txt`
4. Set the start command to `gunicorn backend.app:app`
5. Add environment variables in Render dashboard
6. Deploy frontend as a static page or update `API` to point to the deployed backend

---

## CV line

> **TalentLens** — A Python/Flask job market intelligence platform with SQLite-backed job caching, NLP-driven CV skill extraction, relevance scoring, and AI-generated cover letters. Includes a zero-build React-style frontend and CI-ready Docker deployment.
