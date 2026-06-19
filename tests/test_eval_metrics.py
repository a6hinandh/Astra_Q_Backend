from evals.metrics import (
    contains_all_keywords,
    exact_match,
    mean_score,
    precision_recall_f1,
    reciprocal_rank,
    routing_accuracy,
    tool_selection_accuracy,
)


def test_exact_match_identical():
    assert exact_match("kg", "kg") is True


def test_exact_match_different():
    assert exact_match("kg", "rag") is False


def test_contains_all_keywords_all_present():
    assert contains_all_keywords("hello world foo", ["hello", "world"]) is True


def test_contains_all_keywords_missing():
    assert contains_all_keywords("hello world", ["hello", "missing"]) is False


def test_contains_all_keywords_case_insensitive():
    assert contains_all_keywords("Hello World", ["hello", "world"]) is True


def test_contains_all_keywords_empty_list():
    assert contains_all_keywords("anything", []) is True


def test_precision_recall_f1_perfect():
    prf = precision_recall_f1(["a", "b"], ["a", "b"])
    assert prf["precision"] == 1.0
    assert prf["recall"] == 1.0
    assert prf["f1"] == 1.0


def test_precision_recall_f1_partial():
    prf = precision_recall_f1(["a", "b", "c"], ["a", "d"])
    assert prf["precision"] < 1.0
    assert prf["recall"] < 1.0


def test_precision_recall_f1_empty_predicted():
    prf = precision_recall_f1([], ["a", "b"])
    assert prf["precision"] == 0.0
    assert prf["recall"] == 0.0
    assert prf["f1"] == 0.0


def test_precision_recall_f1_empty_expected():
    prf = precision_recall_f1(["a", "b"], [])
    assert prf["precision"] == 0.0
    assert prf["recall"] == 0.0
    assert prf["f1"] == 0.0


def test_routing_accuracy_all_correct():
    results = [
        {"mode_matched": True, "tools_matched": True},
        {"mode_matched": True, "tools_matched": False},
    ]
    assert routing_accuracy(results) == 1.0


def test_routing_accuracy_half():
    results = [
        {"mode_matched": True},
        {"mode_matched": False},
    ]
    assert routing_accuracy(results) == 0.5


def test_routing_accuracy_empty():
    assert routing_accuracy([]) == 0.0


def test_tool_selection_accuracy_all_correct():
    results = [
        {"tools_matched": True},
        {"tools_matched": True},
    ]
    assert tool_selection_accuracy(results) == 1.0


def test_tool_selection_accuracy_empty():
    assert tool_selection_accuracy([]) == 0.0


def test_mean_score():
    results = [{"score": 1.0}, {"score": 0.5}]
    assert mean_score(results) == 0.75


def test_mean_score_empty():
    assert mean_score([]) == 0.0


def test_mean_score_custom_key():
    results = [{"x": 10}, {"x": 20}]
    assert mean_score(results, key="x") == 15.0


def test_reciprocal_rank_first_rank():
    sources = ["INSAT-3D doc", "Oceansat-3 doc"]
    rr = reciprocal_rank(sources, ["INSAT-3D"])
    assert rr == 1.0


def test_reciprocal_rank_second_rank():
    sources = ["Oceansat-3 doc", "INSAT-3D doc"]
    rr = reciprocal_rank(sources, ["INSAT-3D"])
    assert rr == 0.5


def test_reciprocal_rank_no_match():
    sources = ["Oceansat-3 doc"]
    rr = reciprocal_rank(sources, ["NOTPRESENT"])
    assert rr == 0.0


def test_reciprocal_rank_empty_keywords():
    assert reciprocal_rank(["a"], []) == 0.0
