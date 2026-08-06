# Anwendungsfall A: Nicht modellierbare Elemente und harte Luecken

Stand: 2026-07-07

Task: 5.3 `Alle nicht modellierbaren Elemente markieren`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Abgrenzung

Eine harte Luecke liegt hier nur dann vor, wenn ein fachliches Element weder durch eine vorhandene Klasse, noch durch ein vorhandenes Attribut, noch durch eine vorhandene Beziehung, noch durch eine dokumentierte Trace-Konvention sinnvoll abbildbar ist.

Nicht als harte Luecke gilt ein Element, wenn es fuer den aktuellen Beispielzweck nachvollziehbar als `Condition.expression`, `Event.expression`, `StateAssertion.expectedState`, `RuntimeAction`-Schema, `ValidationCase.expectedOutcome` oder dokumentierter Trace beschrieben werden kann. Solche Elemente sind in Task 5.2 als indirekt, unscharf oder grenzwertig markiert.

Diese Datei entscheidet noch nicht, ob eine Luecke durch eine Kernanpassung oder durch ein Ergaenzungsmodell geschlossen werden soll. Diese Entscheidung folgt bewusst erst in Task 5.4.

## Ergebnis

Fuer den aktuell abgegrenzten Anwendungsfall A gibt es keine harte Luecke, die die Abbildung des Beispiels blockiert. Requirements, UseCase, Actors, Scenarios, Steps, Events, Conditions, StateAssertions, Capabilities, RuntimeBindings, RuntimeActions und ValidationCases koennen mit dem aktuellen kompakten Metamodell modelliert werden.

Es gibt jedoch harte Lueckenkandidaten unter erweiterter Praezisionsanforderung. Das heisst: Sobald die unten genannten Inhalte nicht nur textuell dokumentiert, sondern als eigenstaendige, maschinenlesbare Modellobjekte verarbeitet, validiert oder generiert werden sollen, passt keine vorhandene Klasse mehr sauber.

## Harte Lueckenkandidaten

| Gap-ID | Betroffenes Element | Warum keine vorhandene Klasse passt | Warum nicht nur 5.2-Unschaerfe? | Aktueller Workaround | Blockiert A jetzt? |
| --- | --- | --- | --- | --- | --- |
| A-GAP-01 | Strukturierte Raumsemantik fuer `inside`, `at`, `near`, `reachable` und `movingTo` | `Entity` kann `TriggerZone`, `SceneBoundary` oder `TargetZone` benennen, aber keine Koordinate, Flaeche, Volumen, Toleranz, Referenzrahmen oder Raumrelation instanziieren. `Condition` und `StateAssertion` enthalten nur Ausdruecke. | Wird hart, sobald automatische raeumliche Konsistenzpruefung oder Geometrie-nahe Generierung gefordert ist. Dann reicht ein String wie `at(AgentBody, TargetZone)` nicht aus. | Ausdruck in `Condition.expression` oder `StateAssertion.expectedState`. | Nein, solange qualitative Zielzustaende genuegen. |
| A-GAP-02 | Explizite Zustandsuebergaenge des Agenten | `StateAssertion` beschreibt Zielzustaende, `Condition` beschreibt Vorbedingungen, `Event` beschreibt Ausloeser und `StepRelation` beschreibt Ablauf. Keine Klasse bindet Source-State, Target-State, Trigger, Guard und Effect zu einem eigenen Transitionselement. | Wird hart, wenn erlaubte oder verbotene Rollen-/Aktivitaetswechsel formal geprueft werden muessen. | Verteilung auf Guard, Event, Step und StateAssertion. | Nein, solange der Trace vom Schritt zum erwarteten Zustand reicht. |
| A-GAP-03 | Strukturierte Event-Quelle, Event-Ziel und Payload | `Event.expression` kann `entered(SceneParticipant, TriggerZone)` ausdruecken, aber `Event` hat keine eigene Beziehung zu Quelle, Ziel, Payload, Kanal, Verbrauchsstatus oder Zeitstempel. `Actor` ist eine externe Rolle und nicht die Ereignisinstanz. | Wird hart, wenn Events automatisch korreliert, konsumiert oder mit Runtime-Signalen abgeglichen werden sollen. | Source, Target und Payload bleiben im Ausdruck oder in Tabellen beschrieben. | Nein, solange Events nur Szenarioschritte ausloesen. |
| A-GAP-04 | Ordnung, Abhaengigkeit und Transaktion innerhalb einer `RuntimeBinding` | `RuntimeBinding` besitzt mehrere `RuntimeAction`-Instanzen, aber keine eigene Reihenfolge, keine Abhaengigkeitskante, keine Transaktionsgruppe und keine Rollback-Semantik. | Wird hart, wenn aus dem Modell ein ausfuehrbarer Aktionsplan mit Reihenfolge und Fehlerbehandlung entstehen soll. | Reihenfolge wird im Text der RuntimeAction-Liste dokumentiert. | Nein, solange RuntimeActions nur nachvollziehbare technische Bindungen sind. |
| A-GAP-05 | Formale Testorakel fuer zusammengesetzte erwartete Ergebnisse | `ValidationCase.expectedOutcome` kann mehrere erwartete Aussagen aufnehmen, aber es gibt keine Klasse fuer logische Operatoren, temporale Operatoren, Negation, Toleranzen oder Prioritaeten. | Wird hart, wenn ValidationCases automatisch ausgewertet werden sollen und nicht nur pruefbare Textaussagen enthalten. | Erwartete Outcomes werden als StateAssertion-Liste und Strukturregeltext dokumentiert. | Nein, solange manuell oder halbformal validiert wird. |
| A-GAP-06 | Explizite Typisierung und Rolle von `Entity`-Instanzen | Vor v0.5 war die Entity-Typisierung nur Tabellenkonvention. Im aktuellen Kern ist sie durch `Entity.kind [0..1]` mit den Werten `agent`, `asset`, `zone`, `signal` und `stateObject` optional modellierbar. | War hart, wenn Generatoren oder Pruefer Entity-Arten unterscheiden mussten; ist im Kern fuer grobe Typisierung geloest. | `Entity.kind`; fehlende Werte bleiben wegen `0..1` zulaessig. | In v0.5 geloest; feingranulare Objektontologien bleiben Ergaenzungsmodelle. |
| A-GAP-07 | Objekt-Affordances fuer interaktive Szenenobjekte | `InteractionAsset` kann als `Entity` modelliert werden, und ein Agent kann eine `Capability` besitzen. Es fehlt aber ein eigenes Element fuer Bedienpunkte, erlaubte Manipulationen, erforderliche Inputs, Objektreaktionen und objektseitige Constraints. | Fuer A nur vorbereitend; wird hart, sobald ein Objekt nicht nur Zustandstraeger, sondern bedienbares Interaktionsobjekt ist. | Generische `Entity`, Events, Conditions und Capabilities. | Nein fuer A; voraussichtlich relevant fuer Anwendungsfall B. |
| A-GAP-08 | Feingranulare Trace-Kante von `Effect` zu konkreter `StateAssertion` | Vor v0.5 war der Trace nur dokumentarisch. Im aktuellen Kern existiert `Effect.evidencedBy -> StateAssertion [0..*]` als optionale, nicht-kompositive Referenz. | War hart, wenn Nachweiswerkzeuge automatisch pruefen sollten, welche konkrete Zustandsaussage einen Effect realisiert; ist fuer den Effect-StateAssertion-Trace geloest. | `Effect.evidencedBy`; ValidationCases bleiben separate Testartefakte. | In v0.5 geloest; formale Testorakel bleiben Ergaenzungsmodell. |

## Nicht als harte Luecke fuer A gewertet

| Element | Warum keine harte Luecke |
| --- | --- |
| Haupt-, Alternativ- und Exception-Szenario | `Scenario.kind` und `StepRelation.kind` reichen fuer die aktuelle Ablaufstruktur aus. |
| Agent als modelliertes Subjekt | `Agent` als Spezialisierung von `Entity` reicht fuer `AgentBody`; Rollenstatus wird als Zustand des Agenten modelliert. |
| Rollenstatus `AgentBody.roleState` | Kein eigenes Subjekt noetig; der Status ist sauber als `StateAssertion.expectedState` des Agenten abbildbar. |
| Vorbedingungen, Guards und Nachbedingungen | `Condition.kind` und `Condition.expression` bilden die Aussagen nachvollziehbar ab. |
| Beobachtbare Zielzustaende | `StateAssertion` mit `subjectRef` und `expectedState` reicht fuer die aktuelle fachliche Validierung. |
| Fachliche Faehigkeiten | `CapabilityUse`, `Capability` und `Effect` trennen Schritt, fachliche Faehigkeit und erwartete Wirkung ausreichend. |
| Technische Anbindung | `RuntimeBinding` und `RuntimeAction` verhindern die verbotene direkte Abkuerzung von `ScenarioStep` zu technischer Aktion. |
| Kardinalitaeten und Invarianten | Die bisherige A-Abbildung verletzt keine bekannte Kardinalitaet und keine Invariante. |
| Low-Level-Pathfinding, Physik, Rendering und Asset-Erzeugung | Diese Themen sind laut Systemgrenze out of scope und deshalb keine Luecken des aktuellen A-Metamodells. |

## Harte Luecke versus Scope-Grenze

Ein wichtiges Ergebnis ist die Trennung zwischen Modellierungsluecke und Scope-Grenze:

- Wenn ein Element fuer den fachlichen Trace von Requirement ueber ScenarioStep und Capability bis RuntimeBinding benoetigt wird, ist es modellrelevant.
- Wenn ein Element nur die konkrete Engine-Implementierung, geometrische Berechnung, Physiksimulation oder grafische Darstellung betrifft, ist es fuer A out of scope.
- Wenn ein Element aktuell textuell abbildbar ist, aber fuer automatische Pruefung, Generierung oder Validierung als eigenes Modellobjekt benoetigt wird, ist es ein harter Lueckenkandidat fuer 5.4.

## Abnahmekontrolle

| Kriterium aus Task 5.3 | Erfuellung |
| --- | --- |
| Liste harter Luecken vorhanden | Die Tabelle `Harte Lueckenkandidaten` enthaelt acht Gap-IDs. |
| Fuer jede Luecke erklaert, warum keine vorhandene Klasse passt | Jede Zeile benennt explizit, welche vorhandenen Klassen nicht reichen und warum. |
| 5.2-Unschaerfen nicht blind zu harten Luecken gemacht | Fuer jeden Gap wird angegeben, ab welcher Praezisionsanforderung er hart wird. |
| Keine Entscheidung zu Kern oder Ergaenzung vorweggenommen | Die Datei bereitet 5.4 vor, entscheidet aber noch nicht. |
| Aktueller A-Use-Case bewertet | Ergebnis ist: keine blockierende harte Luecke fuer die aktuelle A-Abbildung. |

## Konsequenz fuer Task 5.4

Task 5.4 soll fuer `A-GAP-01` bis `A-GAP-08` entscheiden, ob jeweils eine Kernanpassung, ein optionales Ergaenzungsmodell oder kein Modellbedarf vorliegt. Dabei muss besonders geprueft werden, ob eine Luecke allgemein fuer beide Anwendungsfaelle relevant ist oder nur fuer spezialisierte Ausfuehrungs-, Raum-, Interaktions- oder Testautomatisierung.
