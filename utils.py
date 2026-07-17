"""
utils.py
Prompt-engineering and parsing helpers for the AI Mock Interview Coach.

All Gemini calls go through call_gemini() so the model / API version
can be swapped in one place.
"""

import json
import re
import requests

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def call_gemini(api_key: str, prompt: str, temperature: float = 0.7) -> str:
    """Send a single-turn prompt to Gemini and return the raw text response."""
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 1024},
    }
    resp = requests.post(GEMINI_URL, headers=headers, params=params, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response: {data}")


def _extract_json(text: str):
    """Pull the first JSON object/array out of a model response, stripping ```json fences."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in model output: {text[:200]}")
    return json.loads(match.group(1))


def generate_questions(api_key: str, job_description: str, resume_text: str, num_questions: int = 6):
    """Return a list of dicts: {id, type, question}."""
    prompt = f"""You are a senior technical interviewer preparing a mock interview.

Job description:
\"\"\"{job_description}\"\"\"

Candidate resume (may be empty):
\"\"\"{resume_text}\"\"\"

Generate exactly {num_questions} interview questions tailored to this job description
and candidate background. Mix technical and behavioral questions
(roughly 60% technical, 40% behavioral). Vary difficulty from easy warm-up
to challenging.

Respond with ONLY a JSON array, no extra text, in this exact format:
[
  {{"id": 1, "type": "technical", "question": "..."}},
  {{"id": 2, "type": "behavioral", "question": "..."}}
]
"""
    raw = call_gemini(api_key, prompt, temperature=0.8)
    return _extract_json(raw)


def evaluate_answer(api_key: str, question: str, question_type: str, answer: str, job_description: str):
    """Return a dict with scores and feedback for one answer."""
    prompt = f"""You are an expert interview coach evaluating a candidate's spoken/typed
answer to a mock interview question.

Job description context:
\"\"\"{job_description}\"\"\"

Question ({question_type}): {question}

Candidate's answer:
\"\"\"{answer}\"\"\"

Evaluate the answer and respond with ONLY a JSON object in this exact format
(no extra text, no markdown fences):
{{
  "relevance_score": <integer 0-10, how directly the answer addresses the question and job context>,
  "clarity_score": <integer 0-10, structure and communication clarity>,
  "depth_score": <integer 0-10, technical/behavioral depth and specificity, use of concrete examples or metrics>,
  "strengths": "<1-2 sentence summary of what the candidate did well>",
  "improvements": "<1-2 sentence, specific, actionable improvement suggestion>",
  "model_answer": "<a strong 3-5 sentence sample answer to this exact question, tailored to the job description>"
}}

If the candidate's answer is empty or "I don't know" style, score honestly low
and still provide a useful model_answer.
"""
    raw = call_gemini(api_key, prompt, temperature=0.4)
    result = _extract_json(raw)
    for key in ("relevance_score", "clarity_score", "depth_score"):
        result[key] = max(0, min(10, int(result.get(key, 0))))
    return result


def build_final_report(evaluations: list, job_title: str):
    """Aggregate per-question evaluations into an overall readiness summary (no API call needed)."""
    if not evaluations:
        return {
            "overall_score": 0,
            "avg_relevance": 0,
            "avg_clarity": 0,
            "avg_depth": 0,
            "readiness": "No answers submitted yet.",
        }

    n = len(evaluations)
    avg_rel = sum(e["relevance_score"] for e in evaluations) / n
    avg_clarity = sum(e["clarity_score"] for e in evaluations) / n
    avg_depth = sum(e["depth_score"] for e in evaluations) / n
    overall = round((avg_rel + avg_clarity + avg_depth) / 3, 1)

    if overall >= 8:
        readiness = f"Strong — you look interview-ready for a {job_title} role. Fine-tune the small gaps noted below."
    elif overall >= 6:
        readiness = f"Good foundation for {job_title}, but a few answers need more depth or structure before a real interview."
    elif overall >= 4:
        readiness = f"Needs more preparation for {job_title} — revisit the model answers and practice structuring responses (e.g. STAR method)."
    else:
        readiness = f"Not yet ready for {job_title} interviews — treat this as a diagnostic and rebuild answers around concrete examples and metrics."

    return {
        "overall_score": overall,
        "avg_relevance": round(avg_rel, 1),
        "avg_clarity": round(avg_clarity, 1),
        "avg_depth": round(avg_depth, 1),
        "readiness": readiness,
    }
