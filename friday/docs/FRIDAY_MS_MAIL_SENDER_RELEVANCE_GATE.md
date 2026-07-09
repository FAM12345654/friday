# Friday MS-Mail Absender-Fix und Office-Relevanzfilter

## Ziel

Dieser Schritt stabilisiert die lokale Microsoft-Mail-Anzeige:

- Absender werden lesbar angezeigt.
- X.500-/interne Exchange-Adressen werden nicht mehr als leere oder rohe technische Werte angezeigt.
- Das geteilte `office@familienhelden.at`-Postfach wird lokal nach Relevanz gefiltert.
- Persoenliche Postfaecher wie `philip@familienhelden.at` bleiben voll sichtbar.

## Absender-Regel

Friday nutzt weiterhin nur Microsoft Graph `Mail.Read`.

Die lokale Vorschau bildet Absender so ab:

- Name und Adresse: `Name <adresse@example.test>`
- Nur Adresse: `adresse@example.test`
- Interne X.500-Adresse mit Name: Name
- Interne X.500-Adresse ohne Name: `Intern <kurzer technischer Schluessel>`
- Fallback: `Unbekannter Absender`

Mail-Bodies werden seit dem Full-Body-Gate bewusst lokal in SQLite gespeichert, damit die lokale KI die Relevanz auf dem ganzen Inhalt pruefen kann. Sie werden nicht in Git oder Cloud-KI geschrieben.

## Office-Relevanzfilter

Das geteilte Office-Postfach zeigt in der Standardansicht nur relevante lokale Vorschauen.

Relevant ist eine Office-Mail, wenn:

- Philip, Phips, PH oder Zeitler im Betreff, Absender, Empfaenger oder per lokaler KI im vollen Body vorkommt,
- alle drei Partner Philip, Alex und Flo erwaehnt werden,
- der Absender als Kunde mit `betreuer=philip` lokal gespeichert ist.

Nicht relevante Office-Mails bleiben lokal erhalten, sind aber standardmaessig ausgeblendet.

## Alle anzeigen

Die API unterstuetzt:

```text
/api/messages/ms-mail?include_all=true
```

Die mobile App zeigt dafuer den Knopf `Alle anzeigen`.
Die CLI hat den Menuepunkt `Alle Microsoft-Mails anzeigen`.

## Safety

- Keine neuen Microsoft-Scopes.
- Kein `Mail.ReadWrite`.
- Kein `Mail.Send`.
- Keine echten Sendungen.
- Keine Provider-Schreibaktion.
- Keine externe Aktion durch den Relevanzfilter.
- Speicherung bleibt lokal in SQLite; Volltexte bleiben lokal und werden nur an lokales Ollama bzw. Mock-Tests gegeben.

## Tests

Abgedeckt sind:

- normale Absender,
- reine Namen,
- X.500-/interne Absender,
- Fallback auf `sender`,
- Empfaenger-Mapping,
- Office-Defaultfilter,
- `include_all=true`,
- keine Vorschlaege aus irrelevanten Office-Mails,
- CLI-Ansicht fuer alle lokalen Microsoft-Mails.
