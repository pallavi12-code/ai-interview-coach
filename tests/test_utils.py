from utils import _extract_json, build_final_report


def test_extract_json_array_from_markdown_fence():
    assert _extract_json('```json\n[{"id": 1}]\n```') == [{"id": 1}]


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
