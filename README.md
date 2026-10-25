# ProofLayer

### Image & Text Authenticity Risk Analysis

ProofLayer is a web-based application that analyzes images and text for potential AI-generated content using machine-learning inference. It generates risk scores, calculates SHA-256 content fingerprints, and produces certificate-style reports with public verification links.

> **Note:** Risk scores are model predictions, not definitive proof of whether content is AI-generated or human-created.

---

## Project Links

* **GitHub Repository:** https://github.com/Aarik03/ProofLayer---Website-

---

## Overview

The growing availability of AI-generated images and text makes content authenticity increasingly difficult to assess. ProofLayer provides a single interface for submitting content, evaluating model-generated risk scores, and reviewing verification reports.

The application combines machine-learning inference, content fingerprinting, report storage, and a dashboard to present the results in an accessible format.

### Key Objectives

* Analyze images and text using configurable inference endpoints.
* Generate risk scores and corresponding risk categories.
* Create SHA-256 fingerprints for submitted content.
* Store verification results and generate report links.
* Present scan statistics through a dashboard.
* Demonstrate backend API development, deployment, and CI automation.


---

## Features

### 1. Image Verification

Users upload an image for model-based analysis. The application returns a risk score, calculates a content fingerprint, and stores the verification result.

### 2. Text Verification

Users submit text for analysis through the configured inference service. The result includes a risk score and a SHA-256 fingerprint of the submitted content.

### 3. Public Verification Reports

Each completed scan receives a verification identifier. The associated report can be opened through its public link.

### 4. Dashboard

The dashboard presents total scans, risk distribution, and recent verification activity.

### 5. Responsive User Interface

The interface uses a dark glass-inspired visual design, with loading and error states intended to make the verification workflow easier to understand.

### 6. Input Validation

The application is designed to handle invalid image uploads, empty text submissions, oversized inputs, and missing report identifiers.

---

## Screenshots

<img width="1827" height="846" alt="website1" src="https://github.com/user-attachments/assets/5c67bc6c-9547-46f4-9264-f0b140d186f8" />
<img width="1781" height="883" alt="website2" src="https://github.com/user-attachments/assets/d33f76e6-0fbb-427e-aba9-9c38fc9d4ef9" />
<img width="1545" height="622" alt="website4" src="https://github.com/user-attachments/assets/2dda0e01-929b-4228-8244-3598aa9b5a03" />
<img width="1812" height="883" alt="website3" src="https://github.com/user-attachments/assets/57717e77-e4d9-4d05-a963-3d11ccc71d77" />
<img width="1301" height="682" alt="website5" src="https://github.com/user-attachments/assets/a5463218-9f31-443a-af00-c9e2ff985592" />
<img width="1449" height="605" alt="website6" src="https://github.com/user-attachments/assets/ea83090c-7dde-46d4-930c-59ac93d62b66" />


---

## System Architecture

The application consists of a web frontend, a FastAPI backend, a SQLite database, and an external machine-learning inference service.

```text
                 User
                   |
                   v
          Web Frontend
       HTML + Tailwind + JS
                   |
                   v
             FastAPI API
          /       |       \
         v        v        v
   ML Inference  SQLite  SHA-256
      Service    Storage Fingerprint
          \       |       /
                   v
          Verification Report
                   |
                   v
          Public Report Link
```

The frontend communicates with the backend API. The backend processes submissions, requests model inference, calculates content fingerprints, and stores verification results for report retrieval and dashboard statistics.

---

## API Endpoints

| Method | Endpoint                    | Description                      |
| ------ | --------------------------- | -------------------------------- |
| `POST` | `/verify-image`             | Submit an image for verification |
| `POST` | `/verify-text`              | Submit text for verification     |
| `GET`  | `/report/{verification_id}` | Retrieve a verification report   |
| `GET`  | `/dashboard-stats`          | Retrieve dashboard statistics    |

Interactive API documentation is available at `/docs` when the FastAPI backend is running.

---

## Technology Stack

| Component                  | Technology                     |
| -------------------------- | ------------------------------ |
| Backend                    | FastAPI, Python                |
| Database                   | SQLite                         |
| Image Processing           | Pillow                         |
| HTTP Requests              | Requests                       |
| Frontend                   | HTML, Tailwind CSS, JavaScript |
| Charts                     | Chart.js                       |
| Machine-Learning Inference | Hugging Face Inference API     |
| Content Fingerprinting     | SHA-256                        |
| Backend Deployment         | Render                         |
| Frontend Deployment        | Vercel                         |
| Version Control            | Git and GitHub                 |
| Continuous Integration     | Jenkins                        |

---

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
├── screenshots/
└── uploads/
```

---

## Local Setup

### Prerequisites

* Python 3.10 or later
* Git
* A Hugging Face account and access token for the configured inference service

### 1. Clone the Repository

```bash
git clone https://github.com/Aarik03/ProofLayer---Website-.git
cd ProofLayer---Website-
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a reference.

```env
HF_TOKEN=your_hugging_face_token
HF_IMAGE_MODEL_ENDPOINT=your_image_model_endpoint
HF_TEXT_MODEL_ENDPOINT=your_text_model_endpoint
```

Use the actual supported inference endpoint URLs from your project configuration. Keep credentials private and never commit `.env` to GitHub.

### 5. Start the Backend

```bash
uvicorn main:app --reload
```

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

### 6. Open the Frontend

Open the relevant HTML files from the `static/` directory using a local web server, such as VS Code Live Server.

Configure the frontend's API base URL to point to the running backend if necessary.

```javascript
localStorage.setItem(
  "prooflayer_api_base",
  "http://127.0.0.1:8000"
);
```

The frontend must be able to reach the backend, and browser requests must satisfy the backend's CORS configuration.

---

## Deployment

### Backend — Render

The repository includes a `render.yaml` configuration intended to support deployment through Render.

1. Push the project to GitHub.
2. Create a new Blueprint in Render and select the repository.
3. Review the service configuration.
4. Configure `HF_TOKEN` and other required environment variables.
5. Deploy the backend.
6. Verify the API health and documentation endpoints.

**Deployed backend:** `ADD_VERIFIED_RENDER_API_URL`

If the application relies on SQLite or uploaded files, configure persistent storage where required. Confirm that the deployed service can retain data across restarts.

### Frontend — Vercel

1. Import the GitHub repository into Vercel.
2. Review the project settings and deployment configuration.
3. Configure the frontend API base URL to use the deployed backend.
4. Deploy the frontend.
5. Test image verification, text verification, dashboard access, and report retrieval.

**Deployed frontend:** `ADD_VERIFIED_VERCEL_URL`

Deployment configuration and routing must be tested against the actual `vercel.json` file. Do not assume that all routes work until they have been verified.

---

## Jenkins CI Integration

Jenkins is used to demonstrate a basic Continuous Integration workflow for the ProofLayer repository.

### Pipeline Workflow

1. Configure a Jenkins Pipeline job.
2. Connect the job to the GitHub repository.
3. Configure the `main` branch as the source branch.
4. Check out the repository.
5. Run the configured website-file validation steps.
6. Review the build status and Console Output.

### Integration Evidence

**Pipeline Configuration**
<img width="1920" height="906" alt="jenkins2" src="https://github.com/user-attachments/assets/923bd399-7f8c-42c0-9283-7c707cfbdb58" />


**Successful Build**
<img width="1896" height="877" alt="jenkins1" src="https://github.com/user-attachments/assets/94fbd8bf-7289-4acb-a21c-de32beb7fbab" />



### Scope of Integration

The configured pipeline demonstrates repository checkout and website-file validation. It does not provide automatic deployment unless a deployment stage has been separately implemented and verified.

---

## Git and GitHub Workflow

Git is used to track source-code changes, while GitHub hosts the repository and its development history.

Typical workflow:

```bash
git status
git add .
git commit -m "Describe the specific change"
git push origin main
```

The project history should document meaningful changes rather than placing every modification in a single initial commit.

### Repository Evidence
<img width="1888" height="894" alt="repos" src="https://github.com/user-attachments/assets/872e7f28-f7f4-4fed-8880-ef3396517590" />


### Commit History
<img width="1787" height="830" alt="commits" src="https://github.com/user-attachments/assets/d361e156-0d6f-4480-8dd4-7ade226fc81e" />


---

## Testing and Quality Assurance

The following checks should be performed before demonstrating the application.

| Test                         | Expected Behavior                                           |
| ---------------------------- | ----------------------------------------------------------- |
| Upload a valid image         | Returns a verification result                               |
| Upload a non-image file      | Displays a clear validation error                           |
| Upload an oversized image    | Rejects the request if size validation is configured        |
| Submit empty text            | Rejects the request if empty-input validation is configured |
| Submit very long text        | Applies the configured input-size limit                     |
| Open dashboard without scans | Displays an appropriate empty state                         |
| Open a nonexistent report    | Displays a clear error or not-found response                |
| Trigger repeated submissions | Provides appropriate loading and request handling           |

The expected results must be confirmed against the actual implementation before these checks are marked as passed.

---

## Known Limitations

* Risk scores are probabilistic model outputs and cannot conclusively establish content authorship.
* Detection accuracy depends on the selected model, input characteristics, and inference service.
* External inference services may experience latency, rate limits, or temporary unavailability.
* Public report links require appropriate consideration of privacy and data exposure.
* Production deployment requires appropriate configuration for database persistence, uploaded files, API credentials, and error handling.

---

## Future Improvements

Potential improvements include stronger automated testing, structured logging, more robust API validation, improved report privacy controls, and additional CI checks.

---

## License

No license has been specified yet. Add an appropriate license if the project is intended for reuse or distribution.
