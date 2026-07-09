# Friday AI Draft Quality Report

## Ziel

Lokaler Qualitaetsvergleich fuer Aufgaben-Weiterleiten-Drafts mit `qwen3:8b` und `qwen3:14b`.
Die Evaluation nutzt die bestehende Friday-Draft-Pipeline und aendert keine Produkt-Config.

## Safety

- Nur lokales Ollama unter `http://localhost:11434`.
- Keine Cloud-KI.
- Kein Versand.
- Keine Credentials.
- Die pytest-Suite bleibt ohne laufendes Ollama gruen.

## Entscheidungsregel

- 8b-Durchschnitt >= 9/12 und kein Draft < 6: 8b bleibt.
- Sonst 14b nur, wenn Durchschnitt >= 9 und mindestens 2 Punkte besser als 8b.
- Sonst keine Config-Aenderung.

## Ergebnisuebersicht

| Modell | Durchschnitt | Minimum | Durchschnitt Zeit | Ergebnis |
|---|---:|---:|---:|---|
| `qwen3:8b` | 10.60/12 | 9/12 | 21.90s | bestanden |
| `qwen3:14b` | 11.10/12 | 10/12 | 38.87s | bestanden |

## Entscheidung

8b bleibt aktiv. Entscheidungsregel erfuellt: 8b-Durchschnitt 10.60/12 und kein Draft unter 6 Punkten.

## Modell `qwen3:8b`

### S01 - Kurzer Alltagstask per WhatsApp an Partnerin

- Kanal: `whatsapp`
- Kontakt: `Anna`
- Zeit: `19.44s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `239`
- Gesamtpunkte: `10/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 0 | Anrede oder Gruss fehlen oder sind nicht kontaktbezogen. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Anna, du bist mir eine große Hilfe! Ich werde den Einkauf erledigen. Bitte gib mir Bescheid, wenn du etwas bestimmtes benötigst. Ich melde mich bei dir, sobald ich mit dem Einkauf fertig bin.

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S02 - Task mit Faelligkeit morgen und Notiz per E-Mail

- Kanal: `email`
- Kontakt: `Mia`
- Zeit: `19.81s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `248`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: morgen. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Mia, vielen Dank für Ihre Anfrage. Die Unterlagen für den Kundentermin sind bereits vorbereitet. Bitte find Sie die aktuellen Preise in der angehängten Preisliste. Mit freundlichen Grüßen

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S03 - Heikler Ton: ueberfaellige Zusage

- Kanal: `email`
- Kontakt: `Herr Bauer`
- Zeit: `25.31s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `330`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Antwort, Rueckmeldung. |
| Ton | 2 | Der Draft nutzt eine passende formelle Ansprache. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrter Herr Bauer, vielen Dank für Ihre Übernahme der Aufgabe. Um den Ablauf zu klären, bitten wir Sie höflich, bis heute um Rückmeldung zur überfälligen Zusage. Ihre Bestätigung ist uns sehr wichtig, um den weiteren Prozess zeitnah weiterzuverfolgen. Mit freundlichen Grüßen

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S04 - Umlaute, Eszett und Sonderzeichen

- Kanal: `whatsapp`
- Kontakt: `Jörg`
- Zeit: `28.86s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `323`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Oelstand. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte(r) Jörg, wir möchten Sie freundlicherweise um eine Rückfrage zum Schliessfach A-7 und der Größe 42/44 bitten. Die Prüfung des Ölstands, der Masse sowie des Geräteschlüssels ist für den 12.07.2026 geplant. Vielen Dank für Ihre Rückmeldung. Mit freundlichen Grüßen

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S05 - Sehr langer Task-Titel

- Kanal: `email`
- Kontakt: `Nora`
- Zeit: `22.12s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `291`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Freitag. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Liebe Nora, bitte prüfen Sie die vollständige Vorbereitung der Quartalsunterlagen – inklusive Zahlenabgleich, Rückfragenliste, Präsentationsentwurf und finale Ablage. Nur die wichtigsten Punkte kurz zusammenfassen. Vielen Dank und viele Grüße.

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S06 - Minimalfall ohne Faelligkeit und Notizen

- Kanal: `email`
- Kontakt: `Tom`
- Zeit: `14.86s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `186`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 1 | Name und ein Teil von Anrede oder Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrter Tom, bitte prüfen Sie die Rechnung und senden Sie ggf. Rückfragen an unsere Mailadresse. Vielen Dank für Ihre Unterstützung.

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S07 - Formeller Kontakt: Vermieter

- Kanal: `email`
- Kontakt: `Frau Schneider`
- Zeit: `20.58s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `271`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Rueckfrage, naechste Woche. |
| Ton | 2 | Der Draft nutzt eine passende formelle Ansprache. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Frau Schneider, vielen Dank für Ihre Nachricht. Der Termin für die Heizungswartung ist bestätigt. Bitte bestätigen Sie mir kurz, dass der Termin für nächste Woche für Sie in Ordnung ist. Mit freundlichen Grüßen

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S08 - WhatsApp an Freund

- Kanal: `whatsapp`
- Kontakt: `Chris`
- Zeit: `15.01s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `168`
- Gesamtpunkte: `10/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: heute Abend. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 1 | Name und ein Teil von Anrede oder Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hi Chris, hast du das Werkzeug aus dem Keller mitgebracht? Falls nicht, sag mal, ob ich es für dich holen kann. Danke! 😊

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S09 - Delegation an Kollegin mit Deadline

- Kanal: `email`
- Kontakt: `Lea`
- Zeit: `31.66s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `422`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: 2026-07-15. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Lea, vielen Dank für Ihr Angebot für das Projekt Phoenix. Wir haben es nun final gegenlesen und sind mit den Inhalten insgesamt zufrieden. Besonders möchten wir auf das Zahlungsziel und den Lieferumfang achten, um sicherzustellen, dass alles korrekt und einvernehmlich ist. Wir freuen uns auf Ihre Rückmeldung bis zum 15.07.2026. Mit freundlichen Grüßen, [Name]

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S10 - WhatsApp Bitte um schnelle Rueckmeldung

- Kanal: `whatsapp`
- Kontakt: `Sam`
- Zeit: `21.33s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `246`
- Gesamtpunkte: `9/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Freigabe. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 0 | Anrede oder Gruss fehlen oder sind nicht kontaktbezogen. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hi Sam, ich melde mich via WhatsApp unter +491701010101. Könntest du bitte den Layout-Entwurf freigeben? Die Frist ist in 2 Stunden. Es wäre schön, wenn du dich zeitlich etwas bewusst sein könntest.

KI-Draft: qwen3:8b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

## Modell `qwen3:14b`

### S01 - Kurzer Alltagstask per WhatsApp an Partnerin

- Kanal: `whatsapp`
- Kontakt: `Anna`
- Zeit: `49.62s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `165`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 1 | Name und ein Teil von Anrede oder Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hallo Anna, ich muss heute noch einkaufen und wollte fragen, ob du kurzfristig helfen kannst? Vielen Dank im Voraus!

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S02 - Task mit Faelligkeit morgen und Notiz per E-Mail

- Kanal: `email`
- Kontakt: `Mia`
- Zeit: `47.65s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `395`
- Gesamtpunkte: `12/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Mia, wie besprochen habe ich die Unterlagen für den Kundentermin vorbereitet. Bitte finden Sie sie in dieser E-Mail angehängt. Zusätzlich habe ich die aktuelle Preisliste beigefügt, wie Sie angemerkt haben. Der Termin ist für morgen geplant. Sollten Sie noch Fragen haben, stehe ich Ihnen gerne zur Verfügung. Mit freundlichen Grüßen

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S03 - Heikler Ton: ueberfaellige Zusage

- Kanal: `email`
- Kontakt: `Herr Bauer`
- Zeit: `41.66s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `335`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Antwort, Rueckmeldung. |
| Ton | 2 | Der Draft nutzt eine passende formelle Ansprache. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrter Herr Bauer, wir möchten Sie höflich, aber bestimmt bitten, uns um eine Rückmeldung zur überfälligen Zusage zu informieren. Die Fälligkeit liegt heute. Wir wären Ihnen sehr dankbar, wenn Sie uns bis zum Ende des Tages eine Rückmeldung geben könnten. Mit freundlichen Grüßen

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S04 - Umlaute, Eszett und Sonderzeichen

- Kanal: `whatsapp`
- Kontakt: `Jörg`
- Zeit: `46.13s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `264`
- Gesamtpunkte: `10/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 1 | Der Draft ist freundlich, aber fuer den informellen Kanal wenig persoenlich. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 1 | Name und ein Teil von Anrede oder Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hallo Jörg, bitte kläre die Prüfung zu Oelstand, Masse und Geräteschlüssel. Kontaktiere mich per WhatsApp an +491704444444. Fälligkeitsdatum: 2026-07-12. Bitte beachte: Rückfrage zur Größe 42/44 und Schließfach A-7.

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S05 - Sehr langer Task-Titel

- Kanal: `email`
- Kontakt: `Nora`
- Zeit: `46.42s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `320`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: kurz. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Nora, könntest du bitte die vollständige Vorbereitung der Quartalsunterlagen prüfen, inklusive Zahlenabgleich, Rückfragenliste, Präsentationsentwurf und finaler Ablage? Freitag ist der letzte Tag für die Abgabe. Vielen Dank im Voraus! Mit freundlichen Grüßen

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S06 - Minimalfall ohne Faelligkeit und Notizen

- Kanal: `email`
- Kontakt: `Tom`
- Zeit: `24.07s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `144`
- Gesamtpunkte: `12/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hallo Tom, könntest du bitte die Rechnung prüfen? Ich freue mich auf dein Feedback. Viele Grüße

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S07 - Formeller Kontakt: Vermieter

- Kanal: `email`
- Kontakt: `Frau Schneider`
- Zeit: `31.31s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `224`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Rueckfrage, naechste Woche. |
| Ton | 2 | Der Draft nutzt eine passende formelle Ansprache. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Frau Schneider, Ihr Termin zur Heizungswartung ist für nächste Woche bestätigt. Bitte bestätigen Sie kurz, ob dieser Termin für Sie passt. Mit freundlichen Grüßen

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S08 - WhatsApp an Freund

- Kanal: `whatsapp`
- Kontakt: `Chris`
- Zeit: `21.79s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `140`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 2 | Alle erwarteten Task-Fakten sind enthalten. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 1 | Name und ein Teil von Anrede oder Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hey Chris, kannst du heute Abend das Werkzeug aus dem Keller mitbringen? Danke schon mal! 😊

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S09 - Delegation an Kollegin mit Deadline

- Kanal: `email`
- Kontakt: `Lea`
- Zeit: `44.11s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `329`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: 2026-07-15. |
| Ton | 2 | Der Draft trifft einen passenden halbformellen Ton. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Sehr geehrte Lea, bitte finden Sie hier das finale Angebot für das Projekt Phoenix zur Prüfung vor. Besonders auf das Zahlungsziel und den Lieferumfang achten. Die Faelligkeit des Angebots ist am 15.07.2026. Bei Fragen stehen wir Ihnen gerne zur Verfügung. Mit freundlichen Grüßen

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

### S10 - WhatsApp Bitte um schnelle Rueckmeldung

- Kanal: `whatsapp`
- Kontakt: `Sam`
- Zeit: `35.89s`
- Validator akzeptiert: `True`
- Provider Output genutzt: `True`
- Think-Tag-Reste: `False`
- Textlaenge: `242`
- Gesamtpunkte: `11/12`

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Deutsch/Grammatik | 2 | Der Draft ist klar als natuerlicher deutscher Text erkennbar. |
| Fakten | 1 | Ein Teil der Fakten ist enthalten; es fehlt: Freigabe. |
| Ton | 2 | Der Draft nutzt eine passende lockere Du-Form. |
| Laenge | 2 | Der Draft ist mit 2 bis 6 Saetzen knapp und ausreichend. |
| Anrede/Gruss | 2 | Anrede mit Name und Abschluss sind vorhanden. |
| Technisch sauber | 2 | Validator akzeptiert, keine technischen Artefakte sichtbar. |

#### Draft

```text
Hallo Sam, könntest du bitte kurz auf den Layout-Entwurf schauen und ihn bei Bedarf freigeben? Es wäre sehr hilfreich, wenn das in den nächsten 2 Stunden möglich wäre. Vielen Dank im Voraus! LG

KI-Draft: qwen3:14b lokal.
Noch nicht gesendet.
```

#### Blockierte Gruende

Keine.

## Rollback-Hinweis

Falls spaeter ein Modellwechsel rueckgaengig gemacht werden muss, betrifft das nur die Config-Zeile:

```python
OLLAMA_MODEL = "qwen3:8b"
```
