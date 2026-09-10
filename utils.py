"""
utils.py
Prompt-engineering and parsing helpers for the AI Mock Interview Coach.

All Gemini calls go through call_gemini() so the model / API version
can be swapped in one place.
"""

import json
import os
from typing import Any

import requests

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


class GeminiError(RuntimeError):
    """Raised when Gemini cannot be reached or returns an unusable response."""


class ResponseParseError(ValueError):
    """Raised when a model response is not valid JSON in the expected shape."""


def get_api_key(secrets: Any = None) -> str:
    """Read the Gemini key from the environment, then an optional secrets mapping."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key
    if secrets is not None:
        secret_key = str(secrets.get("GEMINI_API_KEY", "")).strip()
        if secret_key:
            return secret_key
    return ""


def call_gemini(api_key: str, prompt: str, temperature: float = 0.7) -> str:
    """Send a single-turn prompt to Gemini and return the raw text response."""
    if not api_key.strip():
        raise GeminiError("Gemini API key is not configured.")
    if not prompt.strip():
        raise ValueError("Gemini prompt cannot be empty.")

    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 1024},
    }
    try:
        resp = requests.post(
            GEMINI_URL, headers=headers, params=params, json=body, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise GeminiError("Gemini request failed. Check the API key and network connection.") from exc
    except ValueError as exc:
        raise GeminiError("Gemini returned an invalid response.") from exc

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError("Gemini returned no usable text response.") from exc


def _extract_json(text: str) -> Any:
    """Extract the first decodable JSON object or array from model output.

    Gemini sometimes wraps valid JSON in Markdown or short explanatory text. A
    JSON decoder is used instead of a greedy regex so nested objects and braces
    inside quoted strings are handled correctly.
    """
    if not isinstance(text, str) or not text.strip():
        raise ResponseParseError("Model response was empty.")

    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
            return value
        except json.JSONDecodeError:
            continue
    raise ResponseParseError("Model response did not contain valid JSON.")


def _validate_questions(value: Any, expected_count: int) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != expected_count:
        raise ResponseParseError(f"Expected exactly {expected_count} interview questions.")

    questions = []
    for index, question in enumerate(value, start=1):
        if not isinstance(question, dict):
            raise ResponseParseError(f"Question {index} is not an object.")
        question_type = question.get("type")
        text = question.get("question")
        if question_type not in {"technical", "behavioral"} or not isinstance(text, str) or not text.strip():
            raise ResponseParseError(f"Question {index} has an invalid type or text.")
        questions.append(
            {"id": question.get("id", index), "type": question_type, "question": text.strip()}
        )
    return questions


def _validate_evaluation(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ResponseParseError("Evaluation response must be a JSON object.")
    required = ("relevance_score", "clarity_score", "depth_score", "strengths", "improvements", "model_answer")
    if any(key not in value for key in required):
        raise ResponseParseError("Evaluation response is missing required fields.")

    result = dict(value)
    for key in ("relevance_score", "clarity_score", "depth_score"):
        try:
            score = int(result[key])
        except (TypeError, ValueError) as exc:
            raise ResponseParseError(f"{key} must be an integer from 0 to 10.") from exc
        result[key] = max(0, min(10, score))
    for key in ("strengths", "improvements", "model_answer"):
        if not isinstance(result[key], str):
            raise ResponseParseError(f"{key} must be text.")
    return result


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
    if not isinstance(num_questions, int) or not 3 <= num_questions <= 10:
        raise ValueError("num_questions must be between 3 and 10.")
    raw = call_gemini(api_key, prompt, temperature=0.8)
    return _validate_questions(_extract_json(raw), num_questions)


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
    return _validate_evaluation(_extract_json(raw))


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
    try:
        avg_rel = sum(float(e["relevance_score"]) for e in evaluations) / n
        avg_clarity = sum(float(e["clarity_score"]) for e in evaluations) / n
        avg_depth = sum(float(e["depth_score"]) for e in evaluations) / n
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Evaluations must contain numeric score fields.") from exc
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
