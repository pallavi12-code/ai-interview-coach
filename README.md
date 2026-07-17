

# 🎤 AI Mock Interview Coach

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-interview-coach-8uu8yxrozsx2hvvcmkh2nn.streamlit.app/)

An AI-powered mock interview simulator built with **Streamlit** + **Google Gemini**.
Paste a job description (and optionally your resume), get tailored technical +
behavioral interview questions, submit typed answers, and receive scored,
actionable feedback plus a final readiness report.

**🔗 Live Demo:** [ai-interview-coach-8uu8yxrozsx2hvvcmkh2nn.streamlit.app](https://ai-interview-coach-8uu8yxrozsx2hvvcmkh2nn.streamlit.app/)

## Why this project 

- Demonstrates **prompt engineering** (structured JSON output from an LLM),
  **agentic multi-step flow** (generate → answer → evaluate → aggregate),
  and a deployed, usable **GenAI product** — not just a notebook.
- Covers ATS-friendly keywords: LLM, Prompt Engineering, Gemini API, Streamlit,
  GenAI, REST API integration, JSON parsing, product design.
- Personally relevant story for interviews: *"I built a tool to help candidates
  like me practice for interviews using GenAI."*

## Features

- Tailored question generation (mix of technical + behavioral) based on JD + resume
- Per-answer scoring: relevance, clarity, depth (0–10 each)
- Actionable feedback: strengths, specific improvement, and a model answer
- Final aggregated readiness report with an overall verdict
- Clean multi-stage Streamlit UI (setup → interview → report), no page reloads needed

## Project structure

```
ai-interview-coach/
├── app.py             # Streamlit UI and app flow
├── utils.py           # Gemini API calls, prompt templates, JSON parsing, scoring
├── requirements.txt    # Dependencies
└── README.md
```

## Setup

1. **Get a free Gemini API key**: https://aistudio.google.com/apikey

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

4. Paste your Gemini API key in the sidebar, enter a job title + job description,
   optionally paste your resume, and click **Generate interview**.



## How it works (architecture)

1. **Question generation**: `generate_questions()` sends the JD + resume to
   Gemini with a strict JSON-array prompt, producing a mix of technical and
   behavioral questions with unique IDs.
2. **Answer evaluation**: `evaluate_answer()` sends each question + the
   candidate's answer + JD context to Gemini, which returns structured scores
   (relevance, clarity, depth), qualitative feedback, and a model answer.
3. **Reporting**: `build_final_report()` aggregates all per-question scores
   locally (no extra API call) into an overall readiness verdict.

## Possible extensions (good "future work" talking points)

- Add speech-to-text (e.g. `streamlit-webrtc` + Whisper) for spoken answers
- Store session history in SQLite to track improvement over multiple attempts
- Add a resume-gap analysis step before questions are generated
- Swap Gemini for a local open-source model via Ollama for offline use

## Tech stack

`Python` · `Streamlit` · `Google Gemini API` · `Prompt Engineering` · `JSON parsing`

---

## 👩‍💻 Author

** (Marikanti Pallavi Reddy)**
B.E. Artificial Intelligence & Machine Learning
Chaitanya Bharathi Institute of Technology, Hyderabad
