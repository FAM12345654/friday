"""Evaluate Friday AI forwarding drafts with local Ollama models.

This script is intentionally not part of the regular smoke check. It performs
local-only Ollama calls against the existing Friday draft pipeline and writes a
markdown quality report.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import time
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from friday import config  # noqa: E402
from friday.app.ai_task_forwarding_draft import (  # noqa: E402
    AI_FORWARD_DRAFT_SCHEMA,
    AITaskForwardingDraft,
    build_ai_task_forwarding_draft,
)
from friday.app.local_model_provider import (  # noqa: E402
    LocalModelProvider,
    ProviderConfig,
    ProviderHealth,
    ProviderResult,
)
from friday.app.local_ollama_runtime import (  # noqa: E402
    check_ollama_health,
    generate_ollama_json,
)


CRITERIA = (
    "Deutsch/Grammatik",
    "Fakten",
    "Ton",
    "Laenge",
    "Anrede/Gruss",
    "Technisch sauber",
)


GERMAN_MARKERS = (
    "bitte",
    "danke",
    "hallo",
    "guten",
    "freundliche",
    "gruesse",
    "grüße",
    "kannst",
    "koenntest",
    "könntest",
    "uebernehmen",
    "übernehmen",
    "aufgabe",
)


ENGLISH_MARKERS = (
    "task",
    "deadline",
    "channel",
    "target",
    "please",
    "thanks",
    "best regards",
)


FORMAL_MARKERS = ("sie", "ihnen", "ihr", "ihre", "guten tag", "sehr geehrte")
INFORMAL_MARKERS = ("du", "dir", "dich", "kannst", "koenntest", "könntest")
GREETING_MARKERS = ("hallo", "liebe", "lieber", "guten tag", "sehr geehrte", "sehr geehrter")
GOODBYE_MARKERS = (
    "danke",
    "viele gruesse",
    "viele grüße",
    "beste gruesse",
    "beste grüße",
    "lg",
    "mit freundlichen gruessen",
    "mit freundlichen grüßen",
)
TECHNICAL_NOISE = ("<think>", "</think>", "```", "{", "}", "\"draft_text\"", "|---", "- ")


@dataclass(frozen=True)
class DraftScenario:
    """One deterministic Friday forwarding scenario."""

    scenario_id: str
    title: str
    task: dict[str, Any]
    contact: dict[str, Any]
    channel: str
    expected_formality: str
    expected_keywords: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class CriterionScore:
    """One criterion score with a short reason."""

    points: int
    reason: str


@dataclass(frozen=True)
class DraftEvaluation:
    """Evaluation result for one model/scenario pair."""

    scenario: DraftScenario
    model: str
    elapsed_seconds: float
    draft: AITaskForwardingDraft
    think_tag_residue: bool
    text_length: int
    scores: dict[str, CriterionScore]

    @property
    def total_score(self) -> int:
        return sum(score.points for score in self.scores.values())


class EvaluationOllamaProvider(LocalModelProvider):
    """Local Ollama provider with a script-only model override."""

    def __init__(self, *, model: str, timeout_seconds: int) -> None:
        self.config = ProviderConfig(
            provider="ollama",
            model=model,
            mode="local_ollama_eval",
            timeout_seconds=timeout_seconds,
            external_enabled=True,
        )

    def health_check(self) -> ProviderHealth:
        result = check_ollama_health(config.OLLAMA_BASE_URL, self.config.timeout_seconds)
        return ProviderHealth(
            provider=self.config.provider,
            model=self.config.model,
            available=result.available,
            is_mock=False,
            external_call_used=result.external_call_used,
            safety_flags_locked=True,
            message="Lokales Ollama ist verfügbar." if result.available else (result.error or "Ollama ist nicht verfügbar."),
        )

    def generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult:
        result = generate_ollama_json(
            prompt=prompt,
            schema=schema,
            base_url=config.OLLAMA_BASE_URL,
            model=self.config.model,
            timeout_seconds=self.config.timeout_seconds,
        )
        return ProviderResult(
            provider=self.config.provider,
            model=self.config.model,
            prompt=(prompt or "").strip(),
            output=result.output,
            schema=dict(schema or {}),
            is_mock=False,
            external_call_used=result.external_call_used,
            product_flow_connected=False,
            error=result.error or ("; ".join(result.validation_errors) if result.validation_errors else None),
        )


def build_scenarios() -> tuple[DraftScenario, ...]:
    """Return the fixed German forwarding scenarios for model comparison."""
    return (
        DraftScenario(
            scenario_id="S01",
            title="Kurzer Alltagstask per WhatsApp an Partnerin",
            task={"id": 1, "title": "Einkauf erledigen", "due_date": "", "notes": ""},
            contact={"id": 101, "name": "Anna", "whatsapp_target": "+491701111111", "email_address": "anna@example.test"},
            channel="whatsapp",
            expected_formality="informal",
            expected_keywords=("Einkauf",),
            notes="Informell, kurz, alltaeglich.",
        ),
        DraftScenario(
            scenario_id="S02",
            title="Task mit Faelligkeit morgen und Notiz per E-Mail",
            task={
                "id": 2,
                "title": "Unterlagen fuer Kundentermin vorbereiten",
                "due_date": "morgen",
                "notes": "Bitte die aktuelle Preisliste anhaengen.",
            },
            contact={"id": 102, "name": "Mia", "whatsapp_target": "+491702222222", "email_address": "mia@example.test"},
            channel="email",
            expected_formality="semi_formal",
            expected_keywords=("Unterlagen", "morgen", "Preisliste"),
            notes="Halbformell, klar und freundlich.",
        ),
        DraftScenario(
            scenario_id="S03",
            title="Heikler Ton: ueberfaellige Zusage",
            task={
                "id": 3,
                "title": "Rueckmeldung zur ueberfaelligen Zusage einholen",
                "due_date": "heute",
                "notes": "Bitte hoeflich, aber bestimmt um Antwort bitten.",
            },
            contact={"id": 103, "name": "Herr Bauer", "email_address": "bauer@example.test", "whatsapp_target": "+491703333333"},
            channel="email",
            expected_formality="formal",
            expected_keywords=("Rueckmeldung", "Zusage", "Antwort"),
            notes="Hoeflich, aber bestimmt.",
        ),
        DraftScenario(
            scenario_id="S04",
            title="Umlaute, Eszett und Sonderzeichen",
            task={
                "id": 4,
                "title": "Pruefung: Oelstand, Masse & Geraeteschluessel klaeren",
                "due_date": "2026-07-12",
                "notes": "Bitte Rueckfrage zu Groesse 42/44 und Schliessfach A-7.",
            },
            contact={"id": 104, "name": "Jörg", "whatsapp_target": "+491704444444", "email_address": "joerg@example.test"},
            channel="whatsapp",
            expected_formality="informal",
            expected_keywords=("Oelstand", "Masse", "A-7"),
            notes="Sonderzeichen und Umlaut-Ersatz muessen stabil bleiben.",
        ),
        DraftScenario(
            scenario_id="S05",
            title="Sehr langer Task-Titel",
            task={
                "id": 5,
                "title": (
                    "Die vollstaendige Vorbereitung der Quartalsunterlagen inklusive Zahlenabgleich, "
                    "Rueckfragenliste, Praesentationsentwurf und finaler Ablage pruefen"
                ),
                "due_date": "Freitag",
                "notes": "Bitte nur die wichtigsten Punkte kurz zusammenfassen.",
            },
            contact={"id": 105, "name": "Nora", "email_address": "nora@example.test", "whatsapp_target": "+491705555555"},
            channel="email",
            expected_formality="semi_formal",
            expected_keywords=("Quartalsunterlagen", "Freitag", "kurz"),
            notes="Langer Titel soll nicht zu langem Draft fuehren.",
        ),
        DraftScenario(
            scenario_id="S06",
            title="Minimalfall ohne Faelligkeit und Notizen",
            task={"id": 6, "title": "Rechnung pruefen", "due_date": "", "notes": ""},
            contact={"id": 106, "name": "Tom", "email_address": "tom@example.test", "whatsapp_target": "+491706666666"},
            channel="email",
            expected_formality="semi_formal",
            expected_keywords=("Rechnung",),
            notes="Keine fehlenden Felder halluzinieren.",
        ),
        DraftScenario(
            scenario_id="S07",
            title="Formeller Kontakt: Vermieter",
            task={
                "id": 7,
                "title": "Termin fuer Heizungswartung bestaetigen",
                "due_date": "naechste Woche",
                "notes": "Bitte in Sie-Form und mit kurzer Rueckfrage.",
            },
            contact={"id": 107, "name": "Frau Schneider", "email_address": "schneider@example.test", "whatsapp_target": "+491707777777"},
            channel="email",
            expected_formality="formal",
            expected_keywords=("Heizungswartung", "naechste Woche", "Rueckfrage"),
            notes="Sie-Form und formeller Ton.",
        ),
        DraftScenario(
            scenario_id="S08",
            title="WhatsApp an Freund",
            task={"id": 8, "title": "Werkzeug vom Keller mitbringen", "due_date": "heute Abend", "notes": "Kurz und locker."},
            contact={"id": 108, "name": "Chris", "whatsapp_target": "+491708888888", "email_address": "chris@example.test"},
            channel="whatsapp",
            expected_formality="informal",
            expected_keywords=("Werkzeug", "Keller", "heute Abend"),
            notes="Locker, kurz, du-Form.",
        ),
        DraftScenario(
            scenario_id="S09",
            title="Delegation an Kollegin mit Deadline",
            task={
                "id": 9,
                "title": "Angebot fuer Projekt Phoenix final gegenlesen",
                "due_date": "2026-07-15",
                "notes": "Besonders auf Zahlungsziel und Lieferumfang achten.",
            },
            contact={"id": 109, "name": "Lea", "email_address": "lea@example.test", "whatsapp_target": "+491709999999"},
            channel="email",
            expected_formality="semi_formal",
            expected_keywords=("Phoenix", "2026-07-15", "Zahlungsziel"),
            notes="Kollegial, aber praezise.",
        ),
        DraftScenario(
            scenario_id="S10",
            title="WhatsApp Bitte um schnelle Rueckmeldung",
            task={
                "id": 10,
                "title": "Kurze Freigabe fuer Layout-Entwurf einholen",
                "due_date": "in 2 Stunden",
                "notes": "Nicht draengeln, aber zeitkritisch nennen.",
            },
            contact={"id": 110, "name": "Sam", "whatsapp_target": "+491701010101", "email_address": "sam@example.test"},
            channel="whatsapp",
            expected_formality="informal",
            expected_keywords=("Freigabe", "Layout", "2 Stunden"),
            notes="Kurz, freundlich, zeitkritisch.",
        ),
    )


def message_body(draft_text: str) -> str:
    """Return the user-facing message body without Friday status labels."""
    lines = []
    for line in (draft_text or "").splitlines():
        clean = line.strip()
        if clean.startswith("KI-Draft:"):
            continue
        if clean == "Noch nicht gesendet.":
            continue
        if clean.startswith("Kanal:") or clean.startswith("Ziel:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def count_sentences(text: str) -> int:
    """Count simple German sentence endings."""
    return sum(1 for char in text if char in ".!?")


def contains_any(text: str, markers: Sequence[str]) -> bool:
    lower = text.lower()
    return any(marker.lower() in lower for marker in markers)


def fact_score(scenario: DraftScenario, body: str) -> CriterionScore:
    lower = body.lower()
    matched = [keyword for keyword in scenario.expected_keywords if keyword.lower() in lower]
    if len(matched) == len(scenario.expected_keywords):
        return CriterionScore(2, "Alle erwarteten Task-Fakten sind enthalten.")
    if matched:
        missing = sorted(set(scenario.expected_keywords) - set(matched))
        return CriterionScore(1, f"Ein Teil der Fakten ist enthalten; es fehlt: {', '.join(missing)}.")
    return CriterionScore(0, "Die zentralen Task-Fakten fehlen.")


def language_score(body: str) -> CriterionScore:
    if not body:
        return CriterionScore(0, "Der Draft ist leer.")
    if contains_any(body, ENGLISH_MARKERS):
        return CriterionScore(0, "Der Draft enthaelt englische oder Denglisch-Marker.")
    if contains_any(body, GERMAN_MARKERS):
        return CriterionScore(2, "Der Draft ist klar als natuerlicher deutscher Text erkennbar.")
    return CriterionScore(1, "Der Draft ist deutsch lesbar, aber sprachlich knapp belegt.")


def tone_score(scenario: DraftScenario, body: str) -> CriterionScore:
    lower = body.lower()
    if scenario.expected_formality == "formal":
        if contains_any(lower, FORMAL_MARKERS) and not contains_any(lower, (" du ", " dir ", " dich ")):
            return CriterionScore(2, "Der Draft nutzt eine passende formelle Ansprache.")
        if contains_any(lower, FORMAL_MARKERS):
            return CriterionScore(1, "Der Draft ist teilweise formell, aber nicht ganz konsistent.")
        return CriterionScore(0, "Die erwartete Sie-Form fehlt.")
    if scenario.expected_formality == "informal":
        if contains_any(lower, INFORMAL_MARKERS):
            return CriterionScore(2, "Der Draft nutzt eine passende lockere Du-Form.")
        return CriterionScore(1, "Der Draft ist freundlich, aber fuer den informellen Kanal wenig persoenlich.")
    if contains_any(lower, FORMAL_MARKERS) or contains_any(lower, INFORMAL_MARKERS):
        return CriterionScore(2, "Der Draft trifft einen passenden halbformellen Ton.")
    return CriterionScore(1, "Der Ton ist neutral, aber wenig deutlich auf den Kontakt zugeschnitten.")


def length_score(body: str) -> CriterionScore:
    sentences = count_sentences(body)
    words = len(body.split())
    if 2 <= sentences <= 6 and 12 <= words <= 120:
        return CriterionScore(2, "Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend.")
    if 1 <= sentences <= 7 and 6 <= words <= 150:
        return CriterionScore(1, "Die Laenge ist nutzbar, aber nicht ideal fuer die Vorgabe 2 bis 6 Saetze.")
    return CriterionScore(0, "Der Draft ist zu kurz, zu lang oder ohne klare Satzstruktur.")


def greeting_score(scenario: DraftScenario, body: str) -> CriterionScore:
    lower = body.lower()
    has_name = str(scenario.contact["name"]).split()[0].lower() in lower
    has_greeting = contains_any(lower, GREETING_MARKERS)
    has_goodbye = contains_any(lower, GOODBYE_MARKERS)
    if has_name and has_greeting and has_goodbye:
        return CriterionScore(2, "Anrede mit Name und Abschluss sind vorhanden.")
    if has_name and (has_greeting or has_goodbye):
        return CriterionScore(1, "Name und ein Teil von Anrede oder Abschluss sind vorhanden.")
    return CriterionScore(0, "Anrede oder Gruss fehlen oder sind nicht kontaktbezogen.")


def technical_score(draft: AITaskForwardingDraft, full_text: str, think_tag_residue: bool) -> CriterionScore:
    if think_tag_residue or contains_any(full_text, TECHNICAL_NOISE):
        return CriterionScore(0, "Der Draft enthaelt Think-Reste, JSON/Markdown-Muell oder technische Artefakte.")
    if draft.provider_output_used and draft.validation_accepted and not draft.blocked_reasons:
        return CriterionScore(2, "Validator akzeptiert, keine technischen Artefakte sichtbar.")
    if draft.validation_accepted:
        return CriterionScore(1, "Validator akzeptiert, aber der Draft hat kleinere Blockierhinweise.")
    return CriterionScore(0, "Validator oder Produktpipeline haben den Draft nicht voll akzeptiert.")


def score_evaluation(scenario: DraftScenario, draft: AITaskForwardingDraft) -> dict[str, CriterionScore]:
    """Score one generated draft with deterministic local rules."""
    full_text = draft.draft_text or ""
    body = message_body(full_text)
    think_residue = "<think>" in full_text.lower() or "</think>" in full_text.lower()
    return {
        "Deutsch/Grammatik": language_score(body),
        "Fakten": fact_score(scenario, body),
        "Ton": tone_score(scenario, body),
        "Laenge": length_score(body),
        "Anrede/Gruss": greeting_score(scenario, body),
        "Technisch sauber": technical_score(draft, full_text, think_residue),
    }


def evaluate_model(model: str, scenarios: Sequence[DraftScenario], timeout_seconds: int) -> list[DraftEvaluation]:
    """Run all scenarios for one model through the existing Friday draft pipeline."""
    provider = EvaluationOllamaProvider(model=model, timeout_seconds=timeout_seconds)
    evaluations: list[DraftEvaluation] = []
    for scenario in scenarios:
        started = time.perf_counter()
        draft = build_ai_task_forwarding_draft(
            task=scenario.task,
            contact=scenario.contact,
            channel=scenario.channel,
            provider=provider,
        )
        elapsed = time.perf_counter() - started
        full_text = draft.draft_text or ""
        evaluations.append(
            DraftEvaluation(
                scenario=scenario,
                model=model,
                elapsed_seconds=elapsed,
                draft=draft,
                think_tag_residue="<think>" in full_text.lower() or "</think>" in full_text.lower(),
                text_length=len(full_text),
                scores=score_evaluation(scenario, draft),
            )
        )
    return evaluations


def average_score(evaluations: Sequence[DraftEvaluation]) -> float:
    if not evaluations:
        return 0.0
    return sum(item.total_score for item in evaluations) / len(evaluations)


def min_score(evaluations: Sequence[DraftEvaluation]) -> int:
    if not evaluations:
        return 0
    return min(item.total_score for item in evaluations)


def decide(evaluations_by_model: Mapping[str, Sequence[DraftEvaluation]]) -> str:
    """Apply the fixed decision rule from the evaluation prompt."""
    eval_8b = list(evaluations_by_model.get("qwen3:8b", ()))
    eval_14b = list(evaluations_by_model.get("qwen3:14b", ()))
    avg_8b = average_score(eval_8b)
    avg_14b = average_score(eval_14b)
    min_8b = min_score(eval_8b)

    if avg_8b >= 9 and min_8b >= 6:
        return (
            "8b bleibt aktiv. Entscheidungsregel erfuellt: "
            f"8b-Durchschnitt {avg_8b:.2f}/12 und kein Draft unter 6 Punkten."
        )
    if avg_14b >= 9 and avg_14b >= avg_8b + 2:
        return (
            "14b objektiv empfohlen. Entscheidungsregel erfuellt: "
            f"14b-Durchschnitt {avg_14b:.2f}/12, mindestens 2 Punkte besser als 8b ({avg_8b:.2f}/12)."
        )
    return (
        "Keine Config-Aenderung. Beide Modelle verfehlen die feste Wechselregel; "
        "eine spaetere gegatete Cloud-Option waere nur als dokumentierte Eskalation zu pruefen."
    )


def render_report(evaluations_by_model: Mapping[str, Sequence[DraftEvaluation]]) -> str:
    """Render a full markdown report with all drafts and scores."""
    lines: list[str] = [
        "# Friday AI Draft Quality Report",
        "",
        "## Ziel",
        "",
        "Lokaler Qualitaetsvergleich fuer Aufgaben-Weiterleiten-Drafts mit `qwen3:8b` und `qwen3:14b`.",
        "Die Evaluation nutzt die bestehende Friday-Draft-Pipeline und aendert keine Produkt-Config.",
        "",
        "## Safety",
        "",
        "- Nur lokales Ollama unter `http://localhost:11434`.",
        "- Keine Cloud-KI.",
        "- Kein Versand.",
        "- Keine Credentials.",
        "- Die pytest-Suite bleibt ohne laufendes Ollama gruen.",
        "",
        "## Entscheidungsregel",
        "",
        "- 8b-Durchschnitt >= 9/12 und kein Draft < 6: 8b bleibt.",
        "- Sonst 14b nur, wenn Durchschnitt >= 9 und mindestens 2 Punkte besser als 8b.",
        "- Sonst keine Config-Aenderung.",
        "",
        "## Ergebnisuebersicht",
        "",
        "| Modell | Durchschnitt | Minimum | Durchschnitt Zeit | Ergebnis |",
        "|---|---:|---:|---:|---|",
    ]

    for model, evaluations in evaluations_by_model.items():
        avg = average_score(evaluations)
        minimum = min_score(evaluations)
        avg_time = sum(item.elapsed_seconds for item in evaluations) / len(evaluations) if evaluations else 0.0
        result = "bestanden" if avg >= 9 and minimum >= 6 else "nicht ausreichend"
        lines.append(f"| `{model}` | {avg:.2f}/12 | {minimum}/12 | {avg_time:.2f}s | {result} |")

    lines.extend(["", "## Entscheidung", "", decide(evaluations_by_model), ""])

    for model, evaluations in evaluations_by_model.items():
        lines.extend([f"## Modell `{model}`", ""])
        for evaluation in evaluations:
            draft = evaluation.draft
            lines.extend(
                [
                    f"### {evaluation.scenario.scenario_id} - {evaluation.scenario.title}",
                    "",
                    f"- Kanal: `{evaluation.scenario.channel}`",
                    f"- Kontakt: `{evaluation.scenario.contact['name']}`",
                    f"- Zeit: `{evaluation.elapsed_seconds:.2f}s`",
                    f"- Validator akzeptiert: `{draft.validation_accepted}`",
                    f"- Provider Output genutzt: `{draft.provider_output_used}`",
                    f"- Think-Tag-Reste: `{evaluation.think_tag_residue}`",
                    f"- Textlaenge: `{evaluation.text_length}`",
                    f"- Gesamtpunkte: `{evaluation.total_score}/12`",
                    "",
                    "| Kriterium | Punkte | Begruendung |",
                    "|---|---:|---|",
                ]
            )
            for criterion in CRITERIA:
                score = evaluation.scores[criterion]
                lines.append(f"| {criterion} | {score.points} | {score.reason} |")
            lines.extend(
                [
                    "",
                    "#### Draft",
                    "",
                    "```text",
                    draft.draft_text,
                    "```",
                    "",
                    "#### Blockierte Gruende",
                    "",
                    ", ".join(draft.blocked_reasons) if draft.blocked_reasons else "Keine.",
                    "",
                ]
            )

    lines.extend(
        [
            "## Rollback-Hinweis",
            "",
            "Falls spaeter ein Modellwechsel rueckgaengig gemacht werden muss, betrifft das nur die Config-Zeile:",
            "",
            "```python",
            'OLLAMA_MODEL = "qwen3:8b"',
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate local Friday AI forwarding drafts.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=[config.OLLAMA_MODEL],
        help="Local Ollama model names to evaluate. Default: current config model.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=config.OLLAMA_TIMEOUT_SECONDS,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "friday" / "docs" / "FRIDAY_AI_DRAFT_QUALITY_REPORT.md"),
        help="Markdown report output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenarios = build_scenarios()
    evaluations_by_model: dict[str, list[DraftEvaluation]] = {}

    for model in args.models:
        evaluations_by_model[model] = evaluate_model(model, scenarios, args.timeout)

    report = render_report(evaluations_by_model)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"Report written: {output_path}")
    for model, evaluations in evaluations_by_model.items():
        print(f"{model}: average={average_score(evaluations):.2f}/12 min={min_score(evaluations)}/12")
    print(decide(evaluations_by_model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
