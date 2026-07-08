from friday.app.review_batch_selection_parser import (
    REVIEW_BATCH_SELECTION_INVALID_MESSAGE,
    ReviewBatchSelectionParseResult,
    normalize_review_batch_selection_input,
    parse_review_batch_selection,
)


def test_parse_review_batch_selection_selects_visible_ids() -> None:
    parsed = parse_review_batch_selection("1,2,3", visible_ids=[1, 2, 3])

    assert parsed.status == "selected"
    assert parsed.selected_ids == (1, 2, 3)
    assert parsed.invalid_tokens == ()
    assert parsed.message is None


def test_parse_review_batch_selection_handles_whitespace() -> None:
    parsed = parse_review_batch_selection("  1, 2 , 3  ", visible_ids=[1, 2, 3])

    assert parsed.status == "selected"
    assert parsed.normalized_input == "1, 2 , 3"
    assert parsed.selected_ids == (1, 2, 3)


def test_parse_review_batch_selection_deduplicates_ids_preserving_order() -> None:
    parsed = parse_review_batch_selection("2,1,2,3,1", visible_ids=[1, 2, 3])

    assert parsed.status == "selected"
    assert parsed.selected_ids == (2, 1, 3)


def test_parse_review_batch_selection_all_selects_all_visible_ids() -> None:
    parsed = parse_review_batch_selection("ALL", visible_ids=[3, 1, 2, 1])

    assert parsed.status == "all"
    assert parsed.selected_ids == (3, 1, 2)
    assert parsed.message is None


def test_parse_review_batch_selection_none_selects_nothing() -> None:
    parsed = parse_review_batch_selection(" none ", visible_ids=[1, 2, 3])

    assert parsed.status == "none"
    assert parsed.selected_ids == ()
    assert parsed.message is None


def test_parse_review_batch_selection_z_goes_back() -> None:
    parsed = parse_review_batch_selection(" z ", visible_ids=[1, 2, 3])

    assert parsed.status == "back"
    assert parsed.selected_ids == ()
    assert parsed.message is None


def test_parse_review_batch_selection_empty_input_is_empty() -> None:
    parsed = parse_review_batch_selection("   ", visible_ids=[1, 2, 3])

    assert parsed.status == "empty"
    assert parsed.selected_ids == ()
    assert parsed.message is None


def test_parse_review_batch_selection_none_raw_input_is_empty() -> None:
    parsed = parse_review_batch_selection(None, visible_ids=[1, 2, 3])

    assert parsed.status == "empty"
    assert parsed.raw_input == ""
    assert parsed.normalized_input == ""


def test_parse_review_batch_selection_rejects_unknown_visible_id() -> None:
    parsed = parse_review_batch_selection("1,4", visible_ids=[1, 2, 3])

    assert parsed.status == "invalid"
    assert parsed.selected_ids == ()
    assert parsed.invalid_tokens == ("4",)
    assert parsed.message == REVIEW_BATCH_SELECTION_INVALID_MESSAGE


def test_parse_review_batch_selection_rejects_negative_and_decimal_ids() -> None:
    parsed = parse_review_batch_selection("-1,2.5", visible_ids=[1, 2, 3])

    assert parsed.status == "invalid"
    assert parsed.invalid_tokens == ("-1", "2.5")
    assert parsed.message == REVIEW_BATCH_SELECTION_INVALID_MESSAGE


def test_parse_review_batch_selection_rejects_special_characters() -> None:
    parsed = parse_review_batch_selection("!@#", visible_ids=[1, 2, 3])

    assert parsed.status == "invalid"
    assert parsed.invalid_tokens == ("!@#",)
    assert parsed.message == REVIEW_BATCH_SELECTION_INVALID_MESSAGE


def test_parse_review_batch_selection_rejects_review_actions_and_approval_tokens() -> None:
    for user_input in ("a", "r", "JA", "SPEICHERN"):
        parsed = parse_review_batch_selection(user_input, visible_ids=[1, 2, 3])
        assert parsed.status == "invalid"
        assert parsed.selected_ids == ()
        assert parsed.message == REVIEW_BATCH_SELECTION_INVALID_MESSAGE


def test_parse_review_batch_selection_rejects_empty_comma_tokens() -> None:
    parsed = parse_review_batch_selection("1,,2", visible_ids=[1, 2, 3])

    assert parsed.status == "invalid"
    assert parsed.invalid_tokens == ("",)
    assert parsed.message == REVIEW_BATCH_SELECTION_INVALID_MESSAGE


def test_parse_review_batch_selection_has_safe_flags() -> None:
    parsed = parse_review_batch_selection("1", visible_ids=[1])

    assert parsed.preview_only is True
    assert parsed.persisted is False
    assert parsed.external_action_used is False


def test_parse_review_batch_selection_result_type_fields() -> None:
    parsed = parse_review_batch_selection("1", visible_ids=[1])

    assert isinstance(parsed, ReviewBatchSelectionParseResult)
    assert parsed.raw_input == "1"
    assert parsed.normalized_input == "1"


def test_normalize_review_batch_selection_input() -> None:
    assert normalize_review_batch_selection_input("  ALL  ") == "all"
    assert normalize_review_batch_selection_input(None) == ""
