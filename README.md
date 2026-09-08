# 🎤 AI Mock Interview Coach

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-interview-coach-8uu8yxrozsx2hvvcmkh2nn.streamlit.app/)

An AI-powered mock interview application built with **Python, Streamlit, and Google Gemini**. It turns a job description and optional resume into a structured interview session, evaluates answers, and produces an actionable readiness report.

## Why I built it

Interview preparation often requires tailoring questions to a specific role and receiving consistent feedback. This project explores how an LLM can support that workflow through structured prompts and a multi-stage application rather than a single chatbot response.

## Features

- Generate technical and behavioral questions from a job description and optional resume
- Evaluate answers for relevance, clarity, and depth
- Return structured feedback and improvement suggestions
- Aggregate question-level scores into a final readiness report
- Multi-stage Streamlit interface for setup, interview, and report views

## Architecture

```text
Job Description + Resume
          ↓
    Gemini Prompt Layer
          ↓
 Question Generation
          ↓
 Candidate Answers
          ↓
    Answer Evaluation
          ↓
 Local Score Aggregation
          ↓
  Readiness Report
```

## Project structure

```text
ai-interview-coach/
├── app.py             # Streamlit UI and application flow
├── utils.py           # Gemini calls, prompts, JSON parsing and scoring
├── requirements.txt   # Python dependencies
└── README.md
```

## Run locally

```bash
git clone https://github.com/pallavi12-code/ai-interview-coach.git
cd ai-interview-coach
pip install -r requirements.txt
streamlit run app.py
```

Set a Gemini API key using the method described by the application before generating an interview.

## How it works

1. `generate_questions()` sends role context to Gemini and requests structured question data.
2. The candidate answers each question in the Streamlit interface.
3. `evaluate_answer()` sends the question, answer, and role context to Gemini for structured scoring and feedback.
4. `build_final_report()` aggregates the scores locally into a final readiness assessment.

## Tech stack

**Python · Streamlit · Google Gemini API · Prompt Engineering · JSON · LLM Application Development**

## Future improvements

- Persist interview sessions with SQLite
- Add resume-to-job skill-gap analysis
- Add speech input and transcription
- Add evaluation against configurable competency rubrics
- Support local models through Ollama
- Add automated tests and CI

## Author

**Pallavi Reddy**  
B.E. Artificial Intelligence & Machine Learning, CBIT Hyderabad

**Live demo:** https://ai-interview-coach-8uu8yxrozsx2hvvcmkh2nn.streamlit.app/
