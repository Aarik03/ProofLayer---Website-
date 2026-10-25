# ProofLayer

ProofLayer verifies image and text authenticity risk using ML scoring + SHA-256 content fingerprints.
Each scan generates a certificate-style report with a public verification link.

## Tech Stack

- Backend: FastAPI, SQLite, Pillow, Requests
- Frontend: HTML + Tailwind CDN + Chart.js
- AI Inference: Hugging Face Inference API
- Deploy: Render (API) + Vercel (frontend)

## Features

- `POST /verify-image` (upload image, score, hash, save report)
- `POST /verify-text` (paste text, score, hash, save report)
- `GET /report/{verification_id}` (public report)
- `GET /dashboard-stats` (total, risk distribution, last 5 scans)
- Premium black glass UI with loading/error states

## Project Structure

```text
ProofLayer/
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── .env.example
├── render.yaml
├── vercel.json
├── Procfile
├── static/
│   ├── index.html
│   ├── verify-image.html
│   ├── verify-text.html
│   ├── dashboard.html
│   └── report.html
└── uploads/
```

## 1. Local Setup

### Prerequisites

- Python 3.10+
- Hugging Face account + token

### Install

```bash
pip install -r requirements.txt
```

### Configure env

Create `.env` in project root:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxx
HF_IMAGE_MODEL_ENDPOINT=https://api-inference.huggingface.co/models/umm-maybe/AI-image-detector
HF_TEXT_MODEL_ENDPOINT=https://api-inference.huggingface.co/models/roberta-base-openai-detector
```

### Run API

```bash
uvicorn main:app --reload
```

Open docs:

- `http://127.0.0.1:8000/docs`

### Open frontend

Open files from `static/` in browser (or via Live Server).
Default API base is `http://127.0.0.1:8000`.

If needed, set API base in browser console:

```js
localStorage.setItem('prooflayer_api_base', 'http://127.0.0.1:8000')
```

## 2. Deploy Backend on Render

### Option A: Blueprint (recommended)

1. Push repo to GitHub
2. In Render: `New` -> `Blueprint`
3. Select this repo (uses `render.yaml`)
4. Set `HF_TOKEN` in Render env vars
5. Deploy

The API URL will look like:

- `https://prooflayer-api.onrender.com`

### Option B: Manual web service

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add persistent disk mount to project path for SQLite durability

## 3. Deploy Frontend on Vercel

1. Import same repo into Vercel
2. Framework preset: `Other`
3. Deploy (uses `vercel.json`)
4. Open site and set API base once in browser console:

```js
localStorage.setItem('prooflayer_api_base', 'https://YOUR-RENDER-API-URL')
```

Now routes work:

- `/`
- `/verify-image`
- `/verify-text`
- `/dashboard`
- `/report?id=PL-2026-XXXXX`

## API Response Notes

- `score` is AI-generation probability from 0 to 1
- `risk_level`: `Low`, `Medium`, `High`
- `hash`: SHA-256 fingerprint of submitted content

## QA Checklist (Use Before Demo)

1. Upload valid image
2. Upload non-image file (should return clean error)
3. Upload very large image >10MB (should block)
4. Submit empty text (should block)
5. Submit long text >20,000 chars (should block)
6. Open dashboard with and without data
7. Open report with fake ID (should show error)
8. Click verify rapidly (button should disable while loading)

## Demo Script (3 Minutes)

1. Start from landing page (`Is This Real?`)
2. Verify one AI-looking image (show High risk)
3. Open generated public report link
4. Verify one human-written text (show lower risk)
5. Open dashboard and explain risk distribution

## Known Limits

- Detector output is probabilistic, not guaranteed truth
- Hugging Face free inference can be slow/cold-started
- Some model endpoints may be unavailable; swap via env vars only (no code changes needed)

## License

Hackathon prototype.
