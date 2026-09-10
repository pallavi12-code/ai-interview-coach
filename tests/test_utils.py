import pytest

from utils import (
    GeminiError,
    ResponseParseError,
    _extract_json,
    build_final_report,
    call_gemini,
    get_api_key,
    _validate_evaluation,
    _validate_questions,
)


def test_extract_json_array_from_markdown_fence():
    assert _extract_json('```json\n[{"id": 1}]\n```') == [{"id": 1}]


def test_extract_json_handles_nested_objects_and_prefix_text():
    output = 'Here is the result: {"items": [{"text": "use {braces}"}]}'
    assert _extract_json(output)["items"][0]["text"] == "use {braces}"


def test_extract_json_rejects_missing_json():
    with pytest.raises(ResponseParseError):
        _extract_json("No structured response")


def test_validate_questions_requires_expected_shape():
    questions = _validate_questions(
        [{"id": 1, "type": "technical", "question": "Explain embeddings."}], 1
    )
    assert questions[0]["question"] == "Explain embeddings."

    with pytest.raises(ResponseParseError):
        _validate_questions([{"type": "other", "question": "Bad"}], 1)


def test_validate_evaluation_clamps_scores_and_requires_fields():
    result = _validate_evaluation(
        {
            "relevance_score": 12,
            "clarity_score": -1,
            "depth_score": "7",
            "strengths": "Clear.",
            "improvements": "Add detail.",
            "model_answer": "A stronger answer.",
        }
    )
    assert (result["relevance_score"], result["clarity_score"], result["depth_score"]) == (10, 0, 7)


def test_get_api_key_prefers_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", " env-key ")
    assert get_api_key({"GEMINI_API_KEY": "secret-key"}) == "env-key"


def test_call_gemini_rejects_missing_key_without_network_call():
    with pytest.raises(GeminiError, match="not configured"):
        call_gemini("", "Generate questions.")


def test_build_final_report_aggregates_scores():
    report = build_final_report(
        [
            {
                "relevance_score": 8,
                "clarity_score": 7,
                "depth_score": 9,
            }
        ],
        "AI Engineer",
    )
    assert report["overall_score"] == 8.0
    assert report["avg_relevance"] == 8.0
    assert "AI Engineer" in report["readiness"]
