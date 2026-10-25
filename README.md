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
localStorage.setItem("prooflayer_api_base", "http://127.0.0.1:8000");
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
localStorage.setItem("prooflayer_api_base", "https://YOUR-RENDER-API-URL");
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

## Website Changes and Git Commit History

The following changes were made to the ProofLayer website and recorded in Git:

| No. | Commit Message                       | Description                                                                         |
| --- | ------------------------------------ | ----------------------------------------------------------------------------------- |
| 1   | Add ProofLayer website project       | Added the initial website source code to the GitHub repository.                     |
| 2   | Add How ProofLayer Works section     | Added a section explaining how the website's verification process works.            |
| 3   | Add verification FAQ section         | Added frequently asked questions to help users understand the website.              |
| 4   | Add verification limitations notice  | Added information about the limitations of authenticity verification.               |
| 5   | Add responsive navigation footer     | Improved the website's navigation and footer layout.                                |
| 6   | Improve responsive navigation layout | Updated navigation styling to wrap items and adjust text sizing on smaller screens. |

These changes were tracked using Git commits and pushed to the GitHub repository.

## Git and GitHub Workflow

The following Git commands were used to manage and upload the project:

```bash
git init
git add .
git commit -m "Add ProofLayer website project"
git remote add origin https://github.com/Aarik03/ProofLayer---Website-.git
git push -u origin main
```

Subsequent website changes were saved using `git add`, `git commit`, and `git push`. The GitHub repository maintains the commit history of the project.

## Jenkins Integration

Jenkins was used to demonstrate Continuous Integration (CI) for the ProofLayer website.

1. Opened Jenkins and created a Pipeline project.
2. Configured the pipeline to check out the `main` branch from GitHub.
3. Added validation steps to check that the main website files exist.
4. Ran the pipeline using **Build Now**.
5. Checked the Console Output to verify the build result.

**Result:** The Jenkins build completed successfully with `Finished: SUCCESS`. The pipeline checked out the repository and validated the specified website files.

**Scope:** The configured pipeline demonstrates source-code checkout and website-file validation. Automatic deployment is not configured.

## Screenshots and Evidence

The screenshots below provide evidence of the website, GitHub repository, commit history, and Jenkins integration.

### 1. Website

Shows the ProofLayer website and its updated interface.

### 2. GitHub Repository

Shows the repository and uploaded project files.

### 3. Git Commit History

Shows the commits documenting the website changes.

### 4. Jenkins Pipeline Result

Shows the successful Jenkins build and its result.

Screenshots and Evidence

The following screenshots document the ProofLayer website, GitHub repository, Git commit history, and Jenkins integration

## Screenshots and Evidence

### 1. ProofLayer Website Interface

(screenshots/Screenshot%202026-10-25%20233851.png)

### 2. Website - How ProofLayer Works

(screenshots/Screenshot%202026-10-25%20233835.png)

### 3. Website - Verification FAQ

(screenshots/Screenshot%202026-10-25%20233816.png)

### 4. Website - Verification Limitations Notice

(screenshots/Screenshot%202026-10-25%20233802.png)

### 5. Responsive Navigation and Footer

(screenshots/Screenshot%202026-10-25%20233747.png)

### 6. GitHub Repository

(screenshots/Screenshot%202026-10-25%20233735.png)

### 7. Git Commit History

(screenshots/Screenshot%202026-10-25%20233716.png)

### 8. Jenkins Pipeline Configuration

(screenshots/Screenshot%202026-10-25%20233656.png)

### 9. Jenkins Build Result

(screenshots/Screenshot%202026-10-25%20233420.png)

### 10. Jenkins Console Output

(screenshots/Screenshot%202026-10-25%20233407.png)

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
