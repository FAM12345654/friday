# Safety Flag Regression Scanner

## Ziel

Lokaler Scanner fuer zentrale Friday-Safety-Flags.

## Umfang

- liest lokale Python-Dateien
- nutzt AST
- erkennt boolesche Flag-Zuweisungen
- erkennt fehlende Flags
- erkennt falsche Werte
- erkennt nicht-literal/dynamische Werte
- fuehrt keine Dateien aus
- importiert keine gescannten Module
- veraendert keine Dateien

## Erwartete Flags

| Flag | Erwarteter Wert |
|---|---:|
| `LOCAL_MODE` | `True` |
| `ENABLE_REAL_EMAIL` | `False` |
| `ENABLE_REAL_WHATSAPP` | `False` |
| `ENABLE_REAL_SMS` | `False` |
| `ENABLE_REAL_CALENDAR` | `False` |
| `ENABLE_REAL_WEATHER` | `False` |
| `ENABLE_REAL_MUSIC` | `False` |
| `REQUIRE_USER_APPROVAL` | `True` |
| `USE_REAL_TODAY` | `False` |
| `USE_SQLITE_STORAGE` | `True` |
| `OBSIDIAN_WRITE_ENABLED` | `False` |
| `ENABLE_LOCAL_OLLAMA` | `False` |

## Implementierte Bausteine

- `SafetyFlagAssignment`
- `SafetyFlagFinding`
- `SafetyFlagRegressionScanResult`
- `scan_python_source_for_safety_flags`
- `scan_python_file_for_safety_flags`
- `evaluate_safety_flag_assignments`
- `scan_paths_for_safety_flag_regressions`

## Safety

- keine Netzwerkaktionen
- keine Provideraufrufe
- keine Ausfuehrung gepruefter Dateien
- keine Produktlogik
- keine DB-Schreiboperation
- keine Obsidian-Schreiboperation

## Tests

- `test_safety_flag_regression_scanner.py`

## Empfehlung

Naechster sinnvoller Schritt:

Approval Token Scanner oder Scanner Smoke Script.
