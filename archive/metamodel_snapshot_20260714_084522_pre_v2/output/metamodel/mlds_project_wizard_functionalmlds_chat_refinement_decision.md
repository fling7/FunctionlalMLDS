# FunctionalMLDS Chat-Refinement Decision

## Entscheidung

FunctionalMLDS-Chat-Refinement verwendet Option B:

- Chat schreibt keine FunctionalMLDS-Artefakte direkt um.
- Chat speichert Nutzerwuensche als `refinement_requests` in der Wizard-Session.
- Der aktuelle FunctionalMLDS-Draft wird mit `validation_stale=true` und `refinement_status=stale` markiert.
- Commit muss spaeter eine vollstaendige Regeneration der Pipeline ausfuehren, damit die Wuensche in Semantics, AgentRoles, Knowledge, FunctionalMLDS, TraceMap und Validierungsartefakten sichtbar werden.

## Begruendung

FunctionalMLDS-Dateien sind nur dann wissenschaftlich belastbar, wenn sie aus einem konsistenten Pipeline-Lauf stammen. Einzelne Chat-Patches an Draft-Schichten koennten Kardinalitaeten, Traceability, RuntimeBindings oder ValidationCases inkonsistent machen. Deshalb wird ein Chat-Wunsch nicht als Modellzustand, sondern als Eingabe fuer die naechste Regeneration behandelt.

## Laufzeitvertrag

Analyze:
- erzeugt einen validierten FunctionalMLDS-Preview-Draft.
- setzt `validation_stale=false`, solange keine Chat-Wuensche vorliegen.

Chat:
- akzeptiert im FunctionalMLDS-Modus den Nutzertext.
- haengt einen Eintrag an `refinement_requests` an.
- setzt `validation_stale=true`.
- gibt den bisherigen Draft mit klarer Assistant-Nachricht zurueck.
- ruft kein LLM auf und schreibt keine FunctionalMLDS-Dateien.

Commit:
- darf stale FunctionalMLDS-Drafts nicht unveraendert materialisieren.
- muss die gespeicherten `refinement_requests` als Zusatzinstruktionen in eine vollstaendige Pipeline-Regeneration einspeisen.
- muss danach alle Validierungen erneut ausfuehren.

## Akzeptanzkriterien

- FunctionalMLDS-Chat speichert mindestens einen Refinement-Request.
- Der Draft meldet `validation_stale=true`.
- Der Assistant weist darauf hin, dass der aktuelle FunctionalMLDS-Stand nicht final validiert ist.
- Legacy-Chat bleibt unveraendert.
- Die finale Sichtbarkeit von Aenderungen im FunctionalMLDS-Artefakt wird beim spaeteren Commit-Regeneration-Task geprueft.
