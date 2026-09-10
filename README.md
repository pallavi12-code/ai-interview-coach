# AI Mock Interview Coach

[![CI](https://github.com/pallavi12-code/ai-interview-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/pallavi12-code/ai-interview-coach/actions/workflows/ci.yml)

An open-source Streamlit application that uses Google Gemini to generate role-specific interview questions, evaluate typed answers, and present a local readiness report. It is a practice aid, not a hiring decision tool or a measurement of interview performance.

## Features

- Tailored technical and behavioral questions from a job description and optional resume text
- Per-answer relevance, clarity, and depth feedback
- Robust handling of Gemini JSON wrapped in Markdown or explanatory text
- Local aggregation of scores into a readable report
- No persistence of resumes, answers, or API keys by the application

## Architecture

```text
Streamlit UI
    |
    +--> utils.get_api_key() --> environment / Streamlit secrets
    |
    +--> utils.call_gemini() --> Gemini REST API
    |          |
    |          +--> validated question/evaluation JSON
    |
    +--> utils.build_final_report() --> local score aggregation
```

The UI flow is split into setup, interview, and report stages in `app.py`. API access, prompt construction, response parsing, schema validation, and score aggregation live in `utils.py`, which can be tested without a network connection.

## Setup

Requirements: Python 3.9+ and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/pallavi12-code/ai-interview-coach.git
cd ai-interview-coach
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
export GEMINI_API_KEY="your-key" # Windows PowerShell: $env:GEMINI_API_KEY="your-key"
streamlit run app.py
```

Alternatively, configure Streamlit secrets in `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key"
```

`.streamlit/secrets.toml` and `.env` files are ignored by Git. Never put a real key in source code, issue reports, screenshots, or committed files. The application checks `GEMINI_API_KEY` first and falls back to the Streamlit secret.

## Testing

The tests do not call Gemini and do not require an API key:

```bash
python -m pip install -r requirements.txt pytest
pytest -q
```

GitHub Actions runs the same test command for pushes to `main` and pull requests targeting `main`.

## Project structure

```text
ai-interview-coach/
├── app.py                  # Streamlit interface and session flow
├── utils.py                # Gemini client, prompts, parsing, validation, scoring
├── tests/test_utils.py     # Offline unit tests
├── requirements.txt        # Runtime dependencies
├── .env.example            # Safe configuration template
└── .github/workflows/ci.yml
```

## Limitations

- Gemini output quality depends on the supplied job description, resume text, and model behavior.
- Scores are qualitative coaching signals, not validated assessments or predictions of hiring outcomes.
- The app currently supports typed answers and in-memory sessions only; refreshing the page loses the current session.
- Requests require network access and a valid Gemini API key.

## Live demo

https://ai-interview-coach-8uu8yxrozsx2hvvcmkh2nn.streamlit.app/

## Author

**Pallavi Reddy** — B.E. Artificial Intelligence & Machine Learning, CBIT Hyderabad
