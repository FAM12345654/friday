# Task Contact Export Gate 17C

## Ziel

17C definiert, wann Kontaktinformationen im lokalen Task-Markdown-Export erscheinen dürfen.

## Regel

Kontaktinformationen dürfen im Export erscheinen, wenn sie als expliziter lokaler Task-Notiz-Snapshot vorhanden sind.

Erlaubt:

- Quelle,
- Kontaktart,
- Beziehungskontext nur bei `user_approved_persistence = 1` und `sensitivity_checked = 1`.

Nicht erlaubt:

- sensible Daten ohne Freigabe,
- externe Lookup-Daten,
- automatisch importierte Kontakte.

## Safety-Bewertung

- Kein externer Export.
- Nur lokaler Markdown-Export.
- Keine Datenbankschema-Änderung.
- Keine neuen Provider.

## Empfehlung für Build Step 17D

Nächster Schritt: `17D — Task Contact Integration`.
