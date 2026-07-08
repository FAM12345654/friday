from friday.app.contact_context_prompt_input_parser import (
    ContactPromptInputParseResult,
    CONTACT_PROMPT_INVALID_MESSAGE,
    CONTACT_PROMPT_INPUT_TO_TYPE,
    parse_contact_prompt_input,
    normalize_contact_prompt_input,
)


def test_parse_contact_prompt_input_selects_contact_type() -> None:
    for user_input, expected_type in CONTACT_PROMPT_INPUT_TO_TYPE.items():
        parsed = parse_contact_prompt_input(user_input)
        assert parsed.action == "select_contact_type"
        assert parsed.contact_type == expected_type
        assert parsed.error_message is None
        assert parsed.preview_only is True
        assert parsed.persisted is False
        assert parsed.external_lookup_used is False


def test_parse_contact_prompt_input_skips_on_skip_inputs() -> None:
    for skip_input in ("", "8", "z", "zurück", "skip", "überspringen", None):
        parsed = parse_contact_prompt_input(skip_input)
        assert parsed.action == "skip"
        assert parsed.contact_type is None
        assert parsed.error_message is None


def test_parse_contact_prompt_input_normalizes_whitespace_and_case() -> None:
    parsed_1 = parse_contact_prompt_input("  1  ")
    assert parsed_1.action == "select_contact_type"
    assert parsed_1.normalized_input == "1"
    assert parsed_1.contact_type == "kunde"

    parsed_skip = parse_contact_prompt_input("  SKIP  ")
    assert parsed_skip.action == "skip"
    assert parsed_skip.normalized_input == "skip"

    parsed_back = parse_contact_prompt_input("  Zurück  ")
    assert parsed_back.action == "skip"
    assert parsed_back.normalized_input == "zurück"


def test_parse_contact_prompt_input_rejects_invalid_values() -> None:
    for invalid_input in ("9", "kunde", "ja", "delete", "random"):
        parsed = parse_contact_prompt_input(invalid_input)
        assert parsed.action == "invalid"
        assert parsed.contact_type is None
        assert parsed.error_message == CONTACT_PROMPT_INVALID_MESSAGE


def test_normalize_contact_prompt_input() -> None:
    assert normalize_contact_prompt_input("  SKIP  ") == "skip"
    assert normalize_contact_prompt_input(None) == ""


def test_parse_contact_prompt_input_has_safe_flags() -> None:
    parsed = parse_contact_prompt_input("1")
    assert parsed.preview_only is True
    assert parsed.persisted is False
    assert parsed.external_lookup_used is False


def test_parse_contact_prompt_input_does_not_treat_delete_confirmation_as_selection() -> (
    None
):
    parsed = parse_contact_prompt_input("JA")
    assert parsed.action == "invalid"
    assert parsed.contact_type is None
    assert parsed.error_message == CONTACT_PROMPT_INVALID_MESSAGE


def test_parse_contact_prompt_input_result_type_fields() -> None:
    parsed = parse_contact_prompt_input("2")
    assert isinstance(parsed, ContactPromptInputParseResult)
    assert parsed.raw_input == "2"
    assert parsed.normalized_input == "2"
