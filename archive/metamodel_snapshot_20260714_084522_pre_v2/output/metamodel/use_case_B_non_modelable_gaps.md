# Anwendungsfall B: Nicht modellierbare Elemente und harte Luecken

Stand: 2026-07-07

Task: 9.3 `Nicht modellierbare B-Elemente markieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Abgrenzung

Eine harte Luecke liegt hier nur dann vor, wenn ein fachliches Element weder durch eine vorhandene Klasse, noch durch ein vorhandenes Attribut, noch durch eine vorhandene Beziehung, noch durch eine dokumentierte Trace-Konvention sinnvoll abbildbar ist.

Nicht als harte Luecke gilt ein Element, wenn es fuer den aktuellen Beispielzweck nachvollziehbar als `Condition.expression`, `Event.expression`, `StateAssertion.expectedState`, `Capability.intent`, `RuntimeAction`-Schema, `ValidationCase.expectedOutcome` oder dokumentierter Trace beschrieben werden kann. Solche Elemente sind in Task 9.2 als indirekt, unscharf oder grenzwertig markiert.

Diese Datei entscheidet noch nicht, ob eine Luecke durch eine Kernanpassung oder durch ein Ergaenzungsmodell geschlossen werden soll. Diese Entscheidung folgt bewusst erst in Task 9.4.

## Ergebnis

Fuer den aktuell abgegrenzten Anwendungsfall B gibt es keine harte Luecke, die die Abbildung des Beispiels blockiert. Requirements, UseCase, Actor, Agent, Entity, Scenarios, Steps, Events, Conditions, StateAssertions, Capabilities, RuntimeBindings, RuntimeActions und ValidationCases koennen mit dem aktuellen kompakten Metamodell modelliert werden.

Es gibt jedoch harte Lueckenkandidaten unter erweiterter Praezisionsanforderung. Das heisst: Sobald die unten genannten Inhalte nicht nur textuell dokumentiert, sondern als eigenstaendige, maschinenlesbare Modellobjekte verarbeitet, validiert oder generiert werden sollen, passt keine vorhandene Klasse mehr sauber.

## Harte Lueckenkandidaten

| Gap-ID | Betroffenes Element | Warum keine vorhandene Klasse passt | Warum nicht nur 9.2-Unschaerfe? | Aktueller Workaround | Blockiert B jetzt? |
| --- | --- | --- | --- | --- | --- |
| `B-GAP-01` | Strukturierte Interaktionsobjekt-Affordances der Kaffeemaschine | `Entity` kann `CoffeeMachine` benennen und `Condition`/`StateAssertion` koennen Objektzustaende ausdruecken. Keine vorhandene Klasse beschreibt aber Bedienpunkte wie Starttaste, Programmauswahl, Tassenbereich, erlaubte Manipulationen, Aktivierungsbedingungen und objektseitige Reaktionen als eigene Modellobjekte. | Wird hart, sobald aus dem Modell interaktive Bedienoberflaechen, VR-Hotspots oder pruefbare Affordance-Constraints generiert werden sollen. | Affordances stehen in `Event.expression`, `Condition.expression`, `StateAssertion.expectedState` und RuntimeAction-Schemas. | Nein, solange die Kaffeemaschine nur fachliches Objekt mit beobachtbaren Zustaenden ist. |
| `B-GAP-02` | Expliziter Objektzustandsautomat fuer Kaffeemaschine und BrewingRequest | `StateAssertion` beschreibt Zielzustaende, `Condition` beschreibt Guards, `Event` beschreibt Ausloeser und `StepRelation` beschreibt Ablauf. Keine Klasse bindet Source-State, Target-State, Trigger, Guard und Effect zu einer formalen Transition. | Wird hart, wenn erlaubte oder verbotene Uebergaenge wie `ready -> brewing`, `notReady -> blocked` oder `requested -> confirmed -> startIssued` maschinenlesbar geprueft werden sollen. | Verteilung auf Conditions, Events, ScenarioSteps und StateAssertions. | Nein, solange der szenariobasierte Trace genuegt. |
| `B-GAP-03` | Strukturierter Vivian-Dialog und Guidance-Content | `Capability` kann Vivians fachliche Faehigkeit beschreiben und `RuntimeAction` kann technische Ausgabe vorbereiten. Keine Klasse beschreibt aber Dialogakt, Inhalt, Zielgruppe, Modalitaet, Sprache, Erklaerstrategie, Wiederholung oder Bezug auf konkrete Affordances als eigenes fachliches Objekt. | Wird hart, wenn Vivian-Hinweise automatisch erzeugt, verglichen, lokalisiert oder didaktisch bewertet werden sollen. | GuidanceTopic und FeedbackState stehen als Strings in StateAssertions, Capabilities und RuntimeAction-Schemas. | Nein, solange Vivian-Hinweise nur fachlich nachvollziehbar beschrieben werden. |
| `B-GAP-04` | Explizite Benutzerbestaetigungs- und Autorisierungssemantik | `ScenarioStep`, `Event`, `Condition` und `BrewingRequest` koennen eine Bestaetigung beschreiben. Es fehlt aber ein eigenes Element fuer Autorisierung, Antwortstatus, Ablehnung, Timeout, Widerruf, Gueltigkeitsdauer und Verantwortlichkeit. | Wird hart, sobald der assistierte Start beweisbar nur mit gueltiger, aktueller Benutzerfreigabe ausgefuehrt werden darf. | `B-MAIN-G07`, `B-MAIN-G08`, `SA-B-BREWING-CONFIRMED` und RuntimeAction-Schemas. | Nein fuer den aktuellen positiven Pfad; relevant bei Abbruch, Timeout oder Safety-Nachweis. |
| `B-GAP-05` | Strukturierte Bereitschaftspruefung als RuleSet oder Decision-Objekt | `Condition.expression` kann die Bereitschaftslogik ausdruecken und `Capability` kann `CAP-B-CHECK-MACHINE-READY` beschreiben. Es fehlt aber ein eigenes Modellobjekt fuer geordnete Readiness-Regeln, Diagnosen, Prioritaeten, Entscheidungsergebnis und Korrekturvorschlag. | Wird hart, wenn Readiness-Logik automatisch ausgewertet, begruendet oder als wiederverwendbarer Sub-Use-Case beziehungsweise Regelkatalog generiert werden soll. | `B-MAIN-G06`, `B-EX-G01`, `B-EFF-READINESS-RESULT-PRODUCED` und RuntimeAction `B-RA-CM-EVALUATE-READINESS`. | Nein, solange die Bereitschaftspruefung als fachlicher Schritt plus Guard reicht. |
| `B-GAP-06` | Strukturierte Event-Quelle, Event-Ziel und Payload | `Event.expression` kann `pressed(Visitor, CoffeeMachine.startButton)` oder `stateChanged(CoffeeMachine.cupPresent, true)` ausdruecken. `Event` hat aber keine eigene Beziehung zu Quelle, Zielobjekt, Payload, Kanal, Zeitstempel, Verbrauchsstatus oder Korrelation. | Wird hart, wenn Events automatisch korreliert, konsumiert, mit Runtime-Signalen abgeglichen oder fuer Testautomatisierung ausgewertet werden sollen. | Source, Target und Payload bleiben im Ausdruck oder in Tabellen beschrieben. | Nein, solange Events nur Szenarioschritte ausloesen. |
| `B-GAP-07` | Ordnung, Abhaengigkeit und Fehlerbehandlung innerhalb einer `RuntimeBinding` | `RuntimeBinding` besitzt mehrere `RuntimeAction`-Instanzen, aber keine eigene Reihenfolge, keine Abhaengigkeitskante, keine Transaktionsgruppe, keine Retry-/Timeout-Regel und keine Rollback-Semantik. | Wird hart, wenn aus dem Modell ein ausfuehrbarer Aktionsplan fuer Vivian-, VR- und Kaffeemaschinenruntime entstehen soll. | Reihenfolge wird im Text der RuntimeAction-Datei dokumentiert. | Nein, solange RuntimeActions nur nachvollziehbare technische Bindungen sind. |
| `B-GAP-08` | Strukturierte RuntimeProfile und Schemas | `RuntimeBinding` benennt Laufzeitkontexte und `RuntimeAction` referenziert `Schema.*`. Es fehlt aber ein eigenes Element fuer Plattformprofil, Version, Adapterfaehigkeit, Deployment, Schemafelder, Typen, Constraints und Kompatibilitaet. | Wird hart, wenn Toolchain-Integration oder Codegenerierung aus dem Modell erfolgen soll. | Runtime-Kontexte und Schemas stehen als Tabellenwerte und Schema-Beschreibungen. | Nein, solange die technische Ebene dokumentarisch bleibt. |
| `B-GAP-09` | Formale Trace-Kante von `Effect` zu konkreter `StateAssertion` und zu ValidationOutcome | Vor v0.5 fehlte eine explizite `Effect -> StateAssertion`-Kante. Im aktuellen Kern ist dieser Teil durch `Effect.evidencedBy -> StateAssertion [0..*]` geloest; eine eigene `ValidationOutcome -> StateAssertion`-Struktur gehoert weiterhin nicht in den Kern. | Wird nur noch fuer formale ValidationOutcome-Logik hart; der Effect-StateAssertion-Trace ist im Kern modellierbar. | `Effect.evidencedBy` fuer Effect-Traces; ValidationCase-Details bleiben dokumentarisch oder optionales Validation-Modul. | Teilweise in v0.5 geloest; ValidationOutcome bleibt Ergaenzungsmodell. |
| `B-GAP-10` | Cross-Scenario Entry-/Return- und VariationPoint-Semantik | `StepRelation` kann von einem Step in einen Alternativ- oder Exception-Step zeigen. Es fehlt aber ein eigenes Element fuer BranchPoint, EntryPoint, ReturnPoint, VariationPoint, RecoveryPolicy und Nicht-Rueckkehr-Semantik. | Wird hart, wenn Alternativen, Exceptions, Wiedereinstieg und Varianten automatisch analysiert oder transformiert werden sollen. | `StepRelation.kind = alternative|exception|sequence` und textuelle Branch-Anker. | Nein, solange die drei B-Scenarios manuell nachvollziehbar bleiben. |
| `B-GAP-11` | Safety- und Hazard-Argumentation fuer sicheren Nicht-Start | `Condition` und `StateAssertion` koennen `safeState = true`, `startPermission = blocked` und `lifecycleState != brewing` ausdruecken. Es fehlt aber ein Modell fuer Hazard, SafetyGoal, Risiko, ASIL/Sicherheitsklassifikation, Mitigation und SafetyCase-Bezug. | Wird hart, wenn aus dem Beispiel ein sicherheitsargumentierbares automotive-nahes Modell entstehen soll. | Sicherer Zustand wird als Exception-Postcondition und StateAssertion modelliert. | Nein fuer das Beispiel; relevant bei Safety- oder AUTOSAR/EAST-ADL-Safety-Argumentation. |
| `B-GAP-12` | Formale Abbruch-, Timeout- und Recovery-Pfade | Der Handlungskatalog nennt Abbruch, fehlende Bestaetigung und Korrekturen; formal instanziiert sind nur fehlende Tasse und fehlgeschlagene Bereitschaft. Keine vorhandene Klasse fehlt fuer einfache Pfade, aber es fehlt ein dediziertes Recovery-/Timeout-Konzept mit Policies und Wiederaufnahmebedingungen. | Wird hart, wenn der B-Use-Case nicht nur beispielhaft, sondern vollstaendig gegen Abbruch, Timeout, Ablehnung und Runtime-Ausfall spezifiziert werden soll. | Weitere Scenarios und StepRelations koennten manuell ergaenzt werden; Policy bleibt textuell. | Nein, solange die aktuelle Baseline nur Main, eine Alternative und eine Exception fordert. |

## Nicht als harte Luecke fuer B gewertet

| Element | Warum keine harte Luecke |
| --- | --- |
| Visitor als externe Rolle | `Actor` mit `interactsWith` und `ScenarioStep.performedBy` reicht fuer die aktuelle Benutzerrolle aus. |
| Vivian als Agent/Entity | `Agent` plus `Entity` reicht fuer die aktuelle Systemgrenze; alternative Actor-Sicht ist eine Systemgrenzenfrage, keine direkte Modellierungsluecke. |
| Kaffeemaschine als fachliche Entity | `Entity` reicht fuer die aktuelle Objektidentitaet und StateAssertion-Subjekte aus. |
| Haupt-, Alternativ- und Exception-Szenario | `Scenario.kind` und `StepRelation.kind` reichen fuer den aktuellen Ablauf aus. |
| Tasse und BrewingRequest als Kontextobjekte | Minimal als `Entity` und `StateAssertion.subjectRef` abbildbar; tieferer Lifecycle ist nur bei erweiterter Praezision noetig. |
| Vorbedingungen, Guards und Nachbedingungen | `Condition.kind` und `Condition.expression` bilden die Aussagen nachvollziehbar ab. |
| Beobachtbare Objektzustaende | `StateAssertion` mit `subjectRef` und `expectedState` reicht fuer die aktuelle fachliche Validierung. |
| Fachliche Faehigkeiten von Vivian und Kaffeemaschine | `CapabilityUse`, `Capability` und `Effect` trennen Schritt, fachliche Faehigkeit und erwartete Wirkung ausreichend. |
| Technische Anbindung | `RuntimeBinding` und `RuntimeAction` verhindern die verbotene direkte Abkuerzung von `ScenarioStep` zu technischer Aktion. |
| ValidationCases | `ValidationCase` reicht fuer Stimulus und ExpectedOutcome, solange keine vollautomatische Testorakel-Sprache gefordert wird. |
| Low-Level-VR-Rendering, Physik und Asset-Erzeugung | Diese Themen sind fuer den fachlichen B-Trace out of scope und deshalb keine Luecken des aktuellen Metamodells. |

## Harte Luecke versus Scope-Grenze

Ein wichtiges Ergebnis ist die Trennung zwischen Modellierungsluecke und Scope-Grenze:

- Wenn ein Element fuer den fachlichen Trace von Requirement ueber ScenarioStep und Capability bis RuntimeBinding benoetigt wird, ist es modellrelevant.
- Wenn ein Element nur die konkrete Engine-Implementierung, grafische Darstellung, Avataranimation, Physiksimulation oder Geraeteintegration betrifft, ist es fuer B out of scope.
- Wenn ein Element aktuell textuell abbildbar ist, aber fuer automatische Pruefung, Generierung, Safety-Argumentation oder Runtime-Ausfuehrung als eigenes Modellobjekt benoetigt wird, ist es ein harter Lueckenkandidat fuer 9.4.

## Priorisierung fuer die Entscheidung in 9.4

| Prioritaet | Gap-ID | Grund |
| --- | --- | --- |
| hoch | `B-GAP-01` | Interaktionsobjekt-Affordances sind zentral fuer den zweiten Beispieltyp: Bedienung einer Kaffeemaschine mit Vivian. |
| hoch | `B-GAP-02` | Objektzustandsautomaten betreffen Kaffeemaschine, BrewingRequest und sichere Startlogik. |
| hoch | `B-GAP-03` | Vivian-Dialog und GuidanceContent sind zentral fuer die Assistenzsemantik. |
| hoch | `B-GAP-05` | Readiness-Logik ist die wichtigste fachliche Entscheidungsstelle vor dem Bruehstart. |
| mittel | `B-GAP-04` | Autorisierung ist fuer assistierten Start wichtig, aber in der Baseline ueber Guards abbildbar. |
| mittel | `B-GAP-07` | Runtime-Orchestrierung ist wichtig fuer Ausfuehrbarkeit, aber nicht fuer die fachliche Baseline. |
| mittel | `B-GAP-09` | Formale Trace-Kanten verbessern Nachweisbarkeit, blockieren aber das Beispiel nicht. |
| mittel | `B-GAP-10` | Cross-Scenario-Semantik wird bei vielen Alternativen/Exceptions wichtiger. |
| niedrig bis mittel | `B-GAP-06`, `B-GAP-08`, `B-GAP-11`, `B-GAP-12` | Wichtig bei Automatisierung, Safety oder Vollstaendigkeit, aber nicht blockierend fuer die aktuelle B-Demonstration. |

## Abnahmekontrolle

| Kriterium aus Task 9.3 | Erfuellung |
| --- | --- |
| Liste harter Luecken vorhanden | Die Tabelle `Harte Lueckenkandidaten` enthaelt zwoelf Gap-IDs. |
| Jede Luecke nennt, warum bestehende Klassen nicht ausreichen | Jede Zeile erklaert, welche vorhandenen Klassen nur unvollstaendig passen. |
| 9.2-Unschaerfen nicht blind zu harten Luecken gemacht | Jede Zeile nennt, ab welcher Praezisionsanforderung der Kandidat hart wird. |
| Aktueller B-Use-Case bewertet | Ergebnis ist: keine blockierende harte Luecke fuer die aktuelle B-Abbildung. |
| Keine Entscheidung zu Kern oder Ergaenzung vorweggenommen | Die Datei priorisiert fuer 9.4, entscheidet aber noch nicht. |

## Konsequenz fuer Task 9.4

Task 9.4 soll fuer `B-GAP-01` bis `B-GAP-12` entscheiden, ob jeweils eine Kernanpassung, ein optionales Ergaenzungsmodell oder kein Modellbedarf vorliegt. Besonders wichtig sind dabei die Trennung zwischen Vivian-spezifischen Erweiterungen, Interaktionsobjekt-Erweiterungen, Runtime-/Schema-Erweiterungen und Safety-/Validation-Erweiterungen.
