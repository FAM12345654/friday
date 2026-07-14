# Claude Code – Arbeitsweise für dieses Repository

## Orchestrierung
- Das Hauptmodell (Fable 5) orchestriert nur: Planung, Aufgabenzerlegung,
  Review der Ergebnisse, Integration, Commits/PRs/Merges.
- Die eigentlichen Implementierungs-Tasks werden an Subagenten mit dem
  Modell **Opus** delegiert (Agent-Tool mit `model: "opus"`).
- Kleine Fixes, bei denen Delegation mehr kostet als nutzt (Ein-Zeilen-Änderungen,
  Doku-Tippfehler), darf der Orchestrator direkt erledigen.

## Bestehende Konventionen (aus der bisherigen Arbeit)
- Tests sind hermetisch: niemals die echte `local_data`-Datenbank oder echte
  Token-Dateien lesen — immer `tmp_path`/Injection verwenden.
- Externe Dienste nur hinter Opt-in-Flags in `friday/config.py`
  (z. B. ENABLE_PUSH_NOTIFICATIONS); lokale KI/TTS/STT nur über
  localhost-Guards.
- Fehlermeldungen und UI-Texte auf Deutsch, Code/Kommentare auf Englisch.
- Nach jedem Feature: kompletter Testlauf (`python -m pytest friday/tests
  friday-api/tests`), dann Commit auf den Arbeitsbranch, PR erstellen und
  mergen (etablierter Auto-Merge-Workflow).
- Whisper-STT bleibt auf CPU (`VOICE_STT_DEVICE = "cpu"`); die 8-GB-GPU ist
  für die deutsche Orpheus-Stimme reserviert.
