# ClarifAI

ClarifAI is a proof-of-concept patient-portal interface for simplifying clinical language while preserving the original medical meaning.

The demo supports:

- browsing example diagnosis folders;
- opening clinical notes;
- generating a patient-friendly explanation;
- expanding difficult medical terms;
- viewing medication prescriptions with dose, frequency, route, timing, and duration;
- keeping the original clinical record visible beside the simplified version;
- a backend API design for LLM-based simplification.

> **Important:** This is a summer-school proof of concept, not a medical device and not a production clinical system.

---

## Project structure

```text
clarifai/
├── index.html
├── config.js
├── README.md
├── .gitignore
└── backend/
    ├── app.py
    ├── requirements.txt
    └── .env.example
```

---

## 1. Frontend

The frontend is a static webpage and can be hosted on GitHub Pages.

### GitHub Pages

1. Upload all files in this ZIP to your repository.
2. Make sure `index.html` is in the repository root.
3. Go to:

   `Settings -> Pages`

4. Choose:

   `Deploy from a branch`

5. Select:

   - Branch: `main`
   - Folder: `/ (root)`

6. Save.

The page will then be available at:

```text
https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/
```

---

## 2. Demo mode

By default, the site works without a backend.

The built-in examples use predefined simplifications.

The interface includes:

- a schwannoma pathology example;
- a headache / neuropathic-pain example;
- a fictional hypertension example;
- fictional medication examples.

Medication examples are intentionally displayed as existing prescription information rather than generated medical advice.

---

## 3. Connecting a real backend

The frontend reads the backend URL from:

```text
config.js
```

Edit:

```javascript
window.CLARIFAI_API_BASE = "";
```

to:

```javascript
window.CLARIFAI_API_BASE = "https://YOUR-BACKEND.example.com";
```

When a backend URL is configured, clicking **Simplify it for me** sends the original clinical text to:

```text
POST /api/simplify
```

---

## 4. Backend setup

The backend uses FastAPI.

From the project directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy:

```text
.env.example
```

to:

```text
.env
```

and add your API key and model name.

Example:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_name_here
FRONTEND_ORIGIN=https://YOUR_USERNAME.github.io
```

Then run:

```bash
uvicorn app:app --reload
```

The development API will be available at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

## 5. API input

Example request:

```json
{
  "record_type": "clinical_note",
  "text": "Assessment: likely tension-type HA vs early neuropathic pain. Plan: trial NSAIDs, monitor progression."
}
```

---

## 6. API output

Example shape:

```json
{
  "plain_language_summary": "The headaches were thought to be most consistent with tension headaches...",
  "medical_terms": [
    {
      "term": "HA",
      "meaning": "headache"
    }
  ],
  "medication": null,
  "uncertainty_present": true,
  "needs_clinician_review": false,
  "warning": null
}
```

---

## 7. Safety principles

ClarifAI is designed around a conservative simplification objective:

**Change the language while changing the clinical meaning as little as possible.**

The backend prompt therefore requires the model to preserve:

- negation;
- diagnostic uncertainty;
- medication names;
- doses;
- units;
- routes;
- frequencies;
- durations;
- dates;
- measurements.

The model is instructed not to:

- diagnose;
- prescribe;
- change medication;
- remove uncertainty;
- invent new information;
- replace the original clinical record.

For a real deployment, additional safeguards would be required, including clinical validation, audit logging, access control, PHI protection, human review policies, and monitoring for hallucinations.

---

## 8. Doctor feedback and future training

A future version could collect clinician feedback such as:

```text
Correct
Something is wrong
```

That feedback could later be converted into a curated preference dataset for fine-tuning or preference optimization.

This should be periodic model-development work, not immediate online retraining after each click.

---

## 9. Production note

Do not place an LLM API key inside `index.html`, `config.js`, or any other frontend file.

Frontend code is public to the browser.

The API key belongs only on the backend server as an environment variable.

---

## 10. Proof-of-concept status

This repository is intended for demonstration and educational use.

It is not intended for clinical decision-making.
