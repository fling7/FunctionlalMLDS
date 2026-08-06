# Anwendungsfall B: Include/Extend-Entscheidung

Stand: 2026-07-07

Task: 7.8 `Include/Extend fuer B pruefen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Quelle:

- `dynamic_functional_mlds_specification.md`
- `invariants.md`
- `use_case_B_main_use_case.md`
- `use_case_B_conditions.md`
- `use_case_B_step_relations.md`
- `use_case_B_error_exception_cases.md`

## Zweck

Diese Datei prueft, ob Verhalten aus Anwendungsfall B auf Use-Case-Ebene als `Include` oder `Extend` modelliert werden soll.

Die Entscheidung folgt der EAST-ADL-nahen Semantik im aktuellen Metamodell:

- `Include` ist verpflichtend. Der inkludierende Use Case ist ohne das inkludierte Verhalten nicht korrekt ausfuehrbar.
- `Extend` ist optional oder bedingt. Der Basis-Use-Case bleibt ohne die Erweiterung eigenstaendig sinnvoll.
- Alternative und Exception innerhalb eines Szenarios sind nicht automatisch `Extend`.
- Ein `Extend` muss mindestens einen `ExtensionPoint` des erweiterten Basis-Use-Cases adressieren.

## Baseline-Entscheidung fuer die aktuelle B-Instanziierung

In der aktuellen kompakten B-Instanziierung werden keine formalen `Include`- oder `Extend`-Instanzen neu angelegt.

Begruendung:

- Der Hauptpfad ist bereits als vollstaendige Sequenz von `B-MAIN-S01` bis `B-MAIN-S20` modelliert.
- Die Bereitschaftspruefung ist verpflichtend, aber aktuell noch als ScenarioStep `B-MAIN-S11` plus nachfolgende Objektreaktion `B-MAIN-S12` abgebildet.
- Ein formales `Include` wuerde einen zusaetzlichen Use Case einfuehren. Dieser muesste nach der Modellregel selbst mindestens ein `Scenario.kind = main` besitzen. Das wird in dieser Taskliste nicht separat ausgearbeitet.
- Optionale Vivian-Erklaerungen, Korrekturpfade und Fehlerbehandlung sind besser als `StepRelation.kind = alternative|exception` oder spaeter als eigener Extend-Kandidat zu behandeln, nicht als Pflicht-Include.

Damit bleibt 7.8 eine saubere semantische Entscheidung, ohne unfertige UseCase-Objekte in das Modell einzuschleusen.

## Entscheidungsregeln

| Regel-ID | Frage | Entscheidung |
| --- | --- | --- |
| `B-IE-R01` | Ist das Verhalten fuer den Basis-Use-Case zwingend erforderlich? | Nur dann ist `Include` zulaessig. |
| `B-IE-R02` | Ist das Verhalten optional, bedingt oder nur in bestimmten Modi aktiv? | Dann ist `Extend` oder eine `StepRelation.kind = alternative|exception` zulaessig, kein `Include`. |
| `B-IE-R03` | Ist das Verhalten ein lokaler Schritt oder eine fachliche Capability-Nutzung? | Dann bleibt es `ScenarioStep -> CapabilityUse`, kein eigener Use Case. |
| `B-IE-R04` | Ist das Verhalten ein korrigierbarer anderer Ablauf? | Dann ist es ein alternatives Scenario oder eine alternative StepRelation, nicht automatisch `Extend`. |
| `B-IE-R05` | Ist das Verhalten ein Fehlerpfad mit sicherem/erklaerbarem Ende? | Dann ist es ein Exception Scenario oder eine Exception StepRelation, kein `Include`. |
| `B-IE-R06` | Soll ein `Extend` angelegt werden? | Dann muss ein konkreter `ExtensionPoint` am erweiterten Use Case existieren. |

## Entscheidungsmatrix

| Kandidat | Pflicht? | Optional/bedingt? | Wiederverwendbar als eigener Use Case? | Entscheidung fuer aktuelle Baseline | Begruendung |
| --- | --- | --- | --- | --- | --- |
| Bereitschaft der Kaffeemaschine pruefen | Ja, vor assistiertem Start | Nein | Ja, potentiell | Kein formales Include jetzt; gueltiger Include-Kandidat fuer eine spaetere UseCase-Reuse-Schicht | In B zwingend, aber derzeit bereits als `B-MAIN-S11`/`B-MAIN-S12` und spaeter `CapabilityUse(CAP-B-CHECK-MACHINE-READY)` abbildbar. |
| Vivian-Grundfuehrung geben | Ja, fuer `UC-B-01` | Nein | Bedingt | Kein Extend | Der Use Case heisst explizit assistierte Bedienung mit Vivian; Grundfuehrung ist Kernverhalten, keine optionale Erweiterung. |
| Explizite Startbestaetigung einholen | Ja, fuer assistierten Start | Nein | Eher nein | Kein Include, kein Extend | Das ist ein lokales Sicherheits-/Freigabegate im Hauptpfad. |
| Bruehvorgang fachlich starten | Ja, fuer Erfolgsfall | Nein | Eher Capability als Use Case | Kein Include | Der Start ist Zielverhalten des Use Case und wird spaeter ueber `CapabilityUse -> Capability` angebunden. |
| Zusaetzliche Trainings- oder Detailerklaerung durch Vivian | Nein | Ja | Ja | Gueltiger Extend-Kandidat, aber nicht Teil der Baseline | Der Basis-Use-Case bleibt ohne Detailerklaerung sinnvoll. |
| Fehlende Tasse oder fehlendes Programm korrigieren | Nein fuer Hauptpfad, aber gueltiger anderer Pfad | Bedingt | Eher Scenario als Use Case | Alternative, kein Extend in Baseline | Korrigierbarer Ablauf kehrt zur Bereitschaftspruefung zurueck und wird in 7.9 ausformuliert. |
| Maschine nicht verfuegbar oder Fehlerzustand erklaeren | Nein fuer Hauptpfad | Bedingt durch Fehler | Eher Exception Scenario | Exception, kein Extend in Baseline | Fehlerbehandlung endet sicher oder erklaerbar und wird in 7.10 ausformuliert. |
| Unassistierte Bedienung ohne Vivian | Nein fuer `UC-B-01` | Alternative Systemnutzung | Ja, als eigener Use Case moeglich | Kein Extend von `UC-B-01` | `UC-B-01` ist explizit assistiert; unassistierte Bedienung waere eher separater Basis-Use-Case oder Alternative in einem breiteren Use Case. |
| Optionaler Vivian-Fortschrittskommentar | Nein | Ja | Ja | Gueltiger Extend-Kandidat | Maschinenfortschritt ist bereits sichtbar; zusaetzliche Vivian-Kommentare waeren optional. |

## Gueltige Include-Kandidaten

Die folgende Beziehung ist semantisch gueltig, wird aber in der aktuellen Baseline noch nicht formal instanziiert:

| Include-Kandidat | includingCase | addition | Warum gueltig? | Voraussetzung fuer formale Instanziierung |
| --- | --- | --- | --- | --- |
| `B-INC-CAND-01` | `UC-B-01 Assistierte Kaffeemaschinenbedienung mit Vivian` | `UC-B-02 Kaffeemaschinenbereitschaft pruefen` | Die Bereitschaftspruefung ist vor dem assistierten Start verpflichtend und potentiell in weiteren Use Cases wiederverwendbar. | `UC-B-02` muss als eigener Use Case mit genau einem Main Scenario spezifiziert werden. |

Wenn `UC-B-02` spaeter eingefuehrt wird, muss das Include ungefaehr so interpretiert werden:

`UC-B-01 --include--> UC-B-02`

Dabei bleibt `UC-B-02` fachlich:

- keine Controller-, API-, Tool- oder Topic-Aufrufe,
- Preconditions wie Verfuegbarkeit, Strom, Wasser, Tasse und Programmauswahl,
- Ergebnis als `ReadinessCheck.result` und passende `StateAssertion`, z. B. `CoffeeMachine.lifecycleState = ready`.

## Gueltige Extend-Kandidaten

Die folgenden Beziehungen sind semantisch gueltig, werden aber in der aktuellen Baseline noch nicht formal instanziiert:

| Extend-Kandidat | extendingCase | extendedCase | moeglicher ExtensionPoint | Bedingung | Warum kein Include? |
| --- | --- | --- | --- | --- | --- |
| `B-EXT-CAND-01` | `UC-B-03 Vivian erklaert Bedienlogik im Trainingsmodus` | `UC-B-01` | `EP-B-01 AfterStartCommand` nach `B-MAIN-S10` | `trainingMode = true` | Die Erklaerung ist optional; der Basis-Use-Case bleibt ohne sie korrekt. |
| `B-EXT-CAND-02` | `UC-B-04 Vivian kommentiert Bruehfortschritt` | `UC-B-01` | `EP-B-02 DuringBrewingProgress` bei `B-MAIN-S17` | `progressNarrationEnabled = true` | Fortschritt ist bereits sichtbar; Vivian-Kommentar ist Zusatzverhalten. |
| `B-EXT-CAND-03` | `UC-B-05 Vivian gibt Abschlusszusammenfassung` | `UC-B-01` | `EP-B-03 AfterCompletionFeedback` nach `B-MAIN-S19` | `summaryRequested = true` | Die Abschlussmeldung in `B-MAIN-S20` reicht fuer den Basis-Use-Case; eine Zusammenfassung waere Zusatz. |

Vor einer formalen `Extend`-Instanziierung muessen die ExtensionPoints als Teile von `UC-B-01` angelegt werden. Ohne gueltigen ExtensionPoint waere ein `Extend` im aktuellen Metamodell nicht korrekt.

## Nicht als Include oder Extend modellieren

| Verhalten | Richtige Modellierung | Grund |
| --- | --- | --- |
| Schrittfolge des erfolgreichen Hauptpfads | `ScenarioStep` plus `StepRelation.kind = sequence` | Das ist der normale Ablauf, keine Wiederverwendung. |
| Starttaste druecken | `ScenarioStep.kind = actorIntent` mit `performedBy = ACT-B-01 Visitor` | Lokale Benutzerhandlung, kein Use Case. |
| Vivian bestaetigt eine erkannte Absicht | `ScenarioStep.kind = systemResponse` plus spaeter `CapabilityUse` | Systemreaktion, kein eigenstaendiger Use Case noetig. |
| Fehlende Tasse korrigieren | `Scenario.kind = alternative` oder `StepRelation.kind = alternative` | Korrigierbarer anderer Pfad, nicht optionales Zusatzverhalten an einem eigenstaendig vollstaendigen Basis-Use-Case. |
| Maschinenfehler erklaeren | `Scenario.kind = exception` oder `StepRelation.kind = exception` | Fehlerpfad mit sicherem/erklaerbarem Ende, kein Include. |
| Fehlende RuntimeBinding | Mapping-/Validierungs-Exception | Keine fachliche Use-Case-Erweiterung und keine direkte technische Kante im ScenarioStep. |

## Konkrete Baseline-Entscheidung

| Entscheidung-ID | Entscheidung | Status |
| --- | --- | --- |
| `B-IE-D01` | In der aktuellen kompakten B-Baseline wird kein formales `Include` instanziiert. | beschlossen |
| `B-IE-D02` | Die Bereitschaftspruefung ist der einzige fachlich starke Include-Kandidat, falls eine wiederverwendbare UseCase-Schicht eingefuehrt wird. | beschlossen |
| `B-IE-D03` | In der aktuellen B-Baseline wird kein formales `Extend` instanziiert. | beschlossen |
| `B-IE-D04` | Optionale Vivian-Zusatzerklaerungen und Fortschrittskommentare sind gueltige Extend-Kandidaten, aber nicht Teil des aktuellen Hauptpfads. | beschlossen |
| `B-IE-D05` | Korrigierbare Ablaeufe und Fehlerablaeufe werden in 7.9 und 7.10 als Alternative/Exception behandelt, nicht als Include. | beschlossen |

## Abnahmekontrolle

| Kriterium aus Task 7.8 | Erfuellung |
| --- | --- |
| Entscheidung zu Include vorhanden | Ja. Kein formales Include in der Baseline; Bereitschaftspruefung als gueltiger Include-Kandidat bei spaeterer UseCase-Reuse-Schicht. |
| Entscheidung zu Extend vorhanden | Ja. Kein formales Extend in der Baseline; optionale Vivian-Zusatzerklaerungen als gueltige Extend-Kandidaten. |
| Include-Semantik verpflichtend eingehalten | Ja. Nur die verpflichtende Bereitschaftspruefung wird als Include-Kandidat zugelassen. |
| Extend-Semantik optional/bedingt eingehalten | Ja. Nur optionale oder bedingte Zusatzablaeufe werden als Extend-Kandidaten zugelassen. |
| ExtensionPoint-Regel beachtet | Ja. Extend-Kandidaten nennen moegliche ExtensionPoints und werden erst formal, wenn diese angelegt sind. |
| Alternative und Exception nicht verwechselt | Ja. Korrigierbare und fehlerhafte Pfade bleiben fuer 7.9 und 7.10 reserviert. |
| Keine technische Direktkopplung | Ja. Kein Include/Extend-Kandidat enthaelt API, Topic, Tool, Controller oder RuntimeAction. |

## Konsequenz fuer Task 7.9

Task 7.9 kann nun ein alternatives Szenario formulieren, ohne es faelschlich als `Extend` zu behandeln. Besonders geeignet ist ein korrigierbarer Pfad, z. B. fehlende Tasse oder fehlende Programmauswahl, der nach Korrektur zur Bereitschaftspruefung zurueckkehrt.
