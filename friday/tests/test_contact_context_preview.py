from friday.app.contact_context_preview import (
    ContactContextPreview,
    build_contact_context_preview,
    normalize_contact_name,
    normalize_contact_type,
)


def test_build_contact_context_preview_sets_preview_flags() -> None:
    preview = build_contact_context_preview("Max Mustermann", "kunde")

    assert isinstance(preview, ContactContextPreview)
    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False


def test_build_contact_context_preview_normalizes_name_and_type() -> None:
    preview = build_contact_context_preview("  MAX   Mustermann ", "Kollege")

    assert preview.normalized_name == "max mustermann"
    assert preview.contact_type == "kollege"


def test_build_contact_context_preview_defaults_unknown_type() -> None:
    preview_none = build_contact_context_preview("Alex", None)
    preview_empty = build_contact_context_preview("Alex", "")

    assert preview_none.contact_type == "unbekannt"
    assert preview_empty.contact_type == "unbekannt"


def test_build_contact_context_preview_maps_invalid_type_to_sonstiges() -> None:
    preview = build_contact_context_preview("Alex", "chef")

    assert preview.contact_type == "sonstiges"


def test_build_contact_context_preview_keeps_optional_local_context() -> None:
    preview = build_contact_context_preview(
        "Alex",
        "freund",
        nickname="Al",
        relationship_context="Projekt Alpha",
        source_context="nachricht",
    )

    assert preview.nickname == "Al"
    assert preview.relationship_context == "Projekt Alpha"
    assert preview.source_context == "nachricht"


def test_normalize_contact_name() -> None:
    assert normalize_contact_name("  Max   Mustermann ") == "max mustermann"


def test_normalize_contact_type() -> None:
    assert normalize_contact_type("  KOLLEGE  ") == "kollege"
    assert normalize_contact_type("Chef") == "sonstiges"
    assert normalize_contact_type("") == "unbekannt"
    assert normalize_contact_type(None) == "unbekannt"


def test_contact_context_preview_does_not_persist_or_lookup_external_data() -> None:
    preview = build_contact_context_preview(
        "Alex",
        "dienstleister",
        source_context="auftrag",
    )

    assert preview.persisted is False
    assert preview.external_lookup_used is False
    assert preview.source_context == "auftrag"
