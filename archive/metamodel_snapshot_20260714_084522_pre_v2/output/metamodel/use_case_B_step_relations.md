# Anwendungsfall B: StepRelations des Hauptszenarios

Stand: 2026-07-07

Task: 7.7 `StepRelations fuer B definieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Main Scenario: `SC-B-01-MAIN`

Quelle:

- `use_case_B_main_scenario_steps.md`
- `use_case_B_conditions.md`
- `use_case_B_state_assertions.md`
- `use_case_B_error_exception_cases.md`

## Zweck

Diese Datei definiert die Ablaufkanten fuer das Hauptszenario von Anwendungsfall B. Eine `StepRelation` verbindet genau einen Quellschritt mit genau einem Zielschritt.

Im aktuellen Stand existieren formal nur die 20 Hauptpfad-Schritte `B-MAIN-S01` bis `B-MAIN-S20`. Deshalb werden in dieser Datei:

1. die formalen `StepRelation`-Instanzen fuer den Hauptpfad angelegt,
2. die Branch-Anker fuer spaetere Alternative- und Exception-Szenarien festgelegt,
3. die spaeteren Ziel-Szenarien aus 6.8 referenziert, ohne deren Schritte bereits vor Task 7.9 und 7.10 zu erfinden.

Diese Trennung ist wichtig, weil `StepRelation.source` und `StepRelation.target` jeweils genau einen vorhandenen `ScenarioStep` referenzieren muessen.

## Modellierungsregel

Im Metamodell gilt:

- `Scenario -> StepRelation [0..*]` als Komposition.
- `StepRelation.source -> ScenarioStep [1]`
- `StepRelation.target -> ScenarioStep [1]`
- `StepRelation.kind in {sequence, alternative, exception, fork, join, loop}`
- `StepRelation.guard [0..1]`

Fuer den linearen erfolgreichen Hauptpfad wird `kind = sequence` verwendet.

Alternativen und Exceptions werden als Branch-Anker vorbereitet, aber erst dann als formale `StepRelation.kind = alternative|exception` angelegt, wenn ihre Zielschritte in 7.9 und 7.10 existieren. Andernfalls wuerde eine Relation auf nicht existente Steps zeigen und damit die Kardinalitaet `target [1]` nur scheinbar erfuellen.

Nach Task 7.9 ist der Branch-Anker `B-BRANCH-A02` durch das alternative Szenario `SC-B-01-ALT01` formal konkretisiert.
Nach Task 7.10 ist der Branch-Anker `B-BRANCH-E02` durch das Exception-Szenario `SC-B-01-EX01` formal konkretisiert.

## Formale StepRelations des Hauptpfads

| Relation-ID | source step | target step | relation kind | guardRef | Wahrscheinlichkeit | Begruendung |
| --- | --- | --- | --- | --- | ---: | --- |
| `B-MAIN-R01` | `B-MAIN-S01` | `B-MAIN-S02` | `sequence` | - | `1.0` | Nach Hilfewunsch wechselt Vivian in den Fuehrungsmodus. |
| `B-MAIN-R02` | `B-MAIN-S02` | `B-MAIN-S03` | `sequence` | `B-MAIN-G02` | `1.0` | Bei aktivem Fuehrungsmodus gibt Vivian den ersten Bedienhinweis. |
| `B-MAIN-R03` | `B-MAIN-S03` | `B-MAIN-S04` | `sequence` | - | `1.0` | Der Benutzer folgt dem Hinweis und platziert die Tasse. |
| `B-MAIN-R04` | `B-MAIN-S04` | `B-MAIN-S05` | `sequence` | - | `1.0` | Nach der Tassenplatzierung wird die Tassenerkennung beobachtet. |
| `B-MAIN-R05` | `B-MAIN-S05` | `B-MAIN-S06` | `sequence` | `B-MAIN-G03` | `1.0` | Nach erkannter Tasse fuehrt Vivian zur Programmauswahl. |
| `B-MAIN-R06` | `B-MAIN-S06` | `B-MAIN-S07` | `sequence` | - | `1.0` | Der Benutzer waehlt nach Vivians Hinweis das Programm. |
| `B-MAIN-R07` | `B-MAIN-S07` | `B-MAIN-S08` | `sequence` | - | `1.0` | Nach Auswahl bestaetigt die Kaffeemaschine die Programmauswahl. |
| `B-MAIN-R08` | `B-MAIN-S08` | `B-MAIN-S09` | `sequence` | `B-MAIN-G04` | `1.0` | Der Startwunsch folgt im Hauptpfad nur auf vorhandene Programmauswahl. |
| `B-MAIN-R09` | `B-MAIN-S09` | `B-MAIN-S10` | `sequence` | - | `1.0` | Vivian bestaetigt den erkannten Startwunsch. |
| `B-MAIN-R10` | `B-MAIN-S10` | `B-MAIN-S11` | `sequence` | `B-MAIN-G05` | `1.0` | Die erkannte, nicht abgebrochene Startanforderung fuehrt zur Bereitschaftspruefung. |
| `B-MAIN-R11` | `B-MAIN-S11` | `B-MAIN-S12` | `sequence` | `B-MAIN-G06` | `1.0` | Nur bestandene Bereitschaftspruefung fuehrt in den erfolgreichen Hauptpfad. |
| `B-MAIN-R12` | `B-MAIN-S12` | `B-MAIN-S13` | `sequence` | - | `1.0` | Nach positiver Startbereitschaft fordert Vivian die explizite Freigabe an. |
| `B-MAIN-R13` | `B-MAIN-S13` | `B-MAIN-S14` | `sequence` | `B-MAIN-G07` | `1.0` | Die Benutzerbestaetigung ist nur nach Vivians Rueckfrage gueltig. |
| `B-MAIN-R14` | `B-MAIN-S14` | `B-MAIN-S15` | `sequence` | `B-MAIN-G08` | `1.0` | Bestaetigte Freigabe und Startpermission fuehren zum fachlichen Startsignal. |
| `B-MAIN-R15` | `B-MAIN-S15` | `B-MAIN-S16` | `sequence` | - | `1.0` | Nach fachlichem Startsignal wird der Bruehzustand beobachtet. |
| `B-MAIN-R16` | `B-MAIN-S16` | `B-MAIN-S17` | `sequence` | `B-MAIN-G09` | `1.0` | Fortschritt wird nur im Bruehzustand angezeigt. |
| `B-MAIN-R17` | `B-MAIN-S17` | `B-MAIN-S18` | `sequence` | - | `1.0` | Nach sichtbarem Fortschritt erreicht die Maschine den Abschlusszustand. |
| `B-MAIN-R18` | `B-MAIN-S18` | `B-MAIN-S19` | `sequence` | `B-MAIN-G10` | `1.0` | Abschlussfeedback folgt erst auf `CoffeeMachine.lifecycleState = finished`. |
| `B-MAIN-R19` | `B-MAIN-S19` | `B-MAIN-S20` | `sequence` | `B-MAIN-G11` | `1.0` | Vivian meldet Abschluss nach sichtbarer Abschlussrueckmeldung. |

## Branch-Anker fuer Alternativen und Exceptions

Die folgenden Eintraege sind noch keine formalen `StepRelation`-Instanzen, weil die Zielschritte der Alternativ- und Exception-Szenarien erst in 7.9 und 7.10 angelegt werden. Sie legen aber fest, an welchen Hauptpfadstellen spaeter `StepRelation.kind = alternative` oder `StepRelation.kind = exception` aushaengen darf.

| Anchor-ID | source step im Hauptpfad | spaeterer relation kind | Guard/Anlass | Ziel-Szenario-Kandidat aus 6.8 | Grund fuer Branch |
| --- | --- | --- | --- | --- | --- |
| `B-BRANCH-A01` | vor oder bei `B-MAIN-S01` | `alternative` | `helpRequested = false` oder `not B-COND-005` | `B-ALT-SC02 ControlledUserAbort` oder unassistierter Bedienpfad | Benutzer startet keinen assistierten Vivian-Pfad. |
| `B-BRANCH-A02` | `B-MAIN-S05` | `alternative` | `CoffeeMachine.cupPresent = false` | `B-ALT-SC01 CorrectMissingCupOrProgram` | Tasse fehlt, kann aber korrigiert werden. |
| `B-BRANCH-A03` | `B-MAIN-S08` | `alternative` | `CoffeeMachine.selectedProgram = none` | `B-ALT-SC01 CorrectMissingCupOrProgram` | Programm fehlt, kann aber korrigiert werden. |
| `B-BRANCH-A04` | `B-MAIN-S11` | `alternative` | `CoffeeMachine.waterLevel = low` und Korrektur moeglich | `B-ALT-SC01 CorrectMissingCupOrProgram` | Wasserstand ist korrigierbar, danach Rueckkehr zur Bereitschaftspruefung. |
| `B-BRANCH-A05` | `B-MAIN-S13` | `alternative` | `BrewingRequest.confirmed != true` | `B-ALT-SC02 ControlledUserAbort` | Benutzer bestaetigt nicht; Warten, erneute Frage oder Abbruch ist ein valider anderer Pfad. |
| `B-BRANCH-A06` | `B-MAIN-S14` oder `B-MAIN-S15` | `alternative` | `BrewingRequest.state = cancelled` | `B-ALT-SC02 ControlledUserAbort` | Benutzer bricht kontrolliert ab. |
| `B-BRANCH-E01` | vor oder bei `B-MAIN-S01` | `exception` | `CoffeeMachine.availabilityState != available` oder `CoffeeMachine.powerState != on` | `B-EX-SC01 MachineNotReady` | Bedienung kann nicht starten. |
| `B-BRANCH-E02` | `B-MAIN-S11` | `exception` | `ReadinessCheck.result = failed` und keine Korrektur im Scope | `B-EX-SC01 MachineNotReady` | Bereitschaftspruefung verhindert den Bruehstart. |
| `B-BRANCH-E03` | `B-MAIN-S11` | `exception` | `CoffeeMachine.waterLevel = low` und Korrektur nicht moeglich | `B-EX-SC01 MachineNotReady` | Bruehstart bleibt blockiert und muss erklaert enden. |
| `B-BRANCH-E04` | `B-MAIN-S15` | `exception` | `CoffeeMachine.startPermission = blocked` | `B-EX-SC01 MachineNotReady` | Startsignal darf nicht ausgegeben werden. |
| `B-BRANCH-E05` | `B-MAIN-S15` | `exception` | `CoffeeMachine.lifecycleState = brewing` vor neuem Start | `B-EX-SC02 UnsafeOrErrorState` | Doppelter Start wird verhindert. |
| `B-BRANCH-E06` | beliebiger Schritt ab `B-MAIN-S11` | `exception` | `CoffeeMachine.lifecycleState = error` oder `CoffeeMachine.safeState != true` | `B-EX-SC02 UnsafeOrErrorState` | Fehler- oder unsicherer Zustand verhindert den Hauptpfad. |
| `B-BRANCH-E07` | `B-MAIN-S15` | `exception` | fachliche Capability vorhanden, aber spaeter keine RuntimeBinding verfuegbar | `B-EX-SC03 RuntimeBindingMissing` | Mapping-/Validierungsfehler ohne technische Direktkante im ScenarioStep. |

## Nach 7.9 formalisierte Alternative

Der folgende Teil konkretisiert `B-BRANCH-A02`. Die Zielschritte existieren seit Task 7.9 in `SC-B-01-ALT01`.

| Relation-ID | source step | target step | relation kind | guardRef | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `B-ALT-R-IN01` | `B-MAIN-S05` | `B-ALT-S01` | `alternative` | `B-ALT-G01` | Wenn nach der Tassenplatzierung keine Tasse erkannt wird, verlaesst der Ablauf den Hauptpfad. |
| `B-ALT-R01` | `B-ALT-S01` | `B-ALT-S02` | `sequence` | `B-ALT-G01` | Vivian reagiert auf die fehlende Tassenerkennung mit einem Korrekturhinweis. |
| `B-ALT-R02` | `B-ALT-S02` | `B-ALT-S03` | `sequence` | - | Der Visitor kann auf Vivians Hinweis hin die Tasse korrigieren. |
| `B-ALT-R03` | `B-ALT-S03` | `B-ALT-S04` | `sequence` | - | Nach der Korrektur wird die Tassenerkennung erneut beobachtet. |
| `B-ALT-R-OUT01` | `B-ALT-S04` | `B-MAIN-S06` | `sequence` | `B-ALT-G02` | Sobald `cupPresent = true` gilt, kehrt der Ablauf zur Programmauswahl-Fuehrung des Hauptpfads zurueck. |

## Nach 7.10 formalisierte Exception

Der folgende Teil konkretisiert `B-BRANCH-E02`. Die Zielschritte existieren seit Task 7.10 in `SC-B-01-EX01`.

| Relation-ID | source step | target step | relation kind | guardRef | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `B-EX-R-IN01` | `B-MAIN-S11` | `B-EX-S01` | `exception` | `B-EX-G01` | Die negative Bereitschaftspruefung verlaesst den Hauptpfad. |
| `B-EX-R01` | `B-EX-S01` | `B-EX-S02` | `sequence` | - | Nach der negativen Pruefung erklaert Vivian die Ursache. |
| `B-EX-R02` | `B-EX-S02` | `B-EX-S03` | `sequence` | `B-EX-G02` | Nach der Erklaerung bleibt der Start fachlich blockiert. |
| `B-EX-R03` | `B-EX-S03` | `B-EX-S04` | `sequence` | - | Der sichere Zustand erlaubt einen erklaerbaren Abschluss der Exception. |

## Graphsicht

Der formale Hauptpfad ist eine lineare Sequenz:

`B-MAIN-S01 -> B-MAIN-S02 -> B-MAIN-S03 -> B-MAIN-S04 -> B-MAIN-S05 -> B-MAIN-S06 -> B-MAIN-S07 -> B-MAIN-S08 -> B-MAIN-S09 -> B-MAIN-S10 -> B-MAIN-S11 -> B-MAIN-S12 -> B-MAIN-S13 -> B-MAIN-S14 -> B-MAIN-S15 -> B-MAIN-S16 -> B-MAIN-S17 -> B-MAIN-S18 -> B-MAIN-S19 -> B-MAIN-S20`

Die fachlich relevanten Branch-Zonen sind:

| Branch-Zone | Hauptpfadstelle | Alternative | Exception |
| --- | --- | --- | --- |
| Start und Assistenzwahl | `B-MAIN-S01` | unassistierter oder kontrollierter Nicht-Assistenzpfad | Maschine nicht verfuegbar oder ausgeschaltet |
| Vorbereitung | `B-MAIN-S05`, `B-MAIN-S08` | Tasse oder Programm korrigieren | nur bei nicht korrigierbarer Ursache |
| Bereitschaftspruefung | `B-MAIN-S11` | korrigierbare fehlende Voraussetzung | nicht korrigierbare fehlende Voraussetzung |
| Startfreigabe | `B-MAIN-S13` bis `B-MAIN-S15` | Benutzer wartet, bestaetigt nicht oder bricht ab | Startfreigabe blockiert, Doppelstart, Fehlerzustand |
| Runtime-Mapping | `B-MAIN-S15` | keine fachliche Alternative | fehlende RuntimeBinding spaeter als Validierungs-/Mapping-Exception |

## Kardinalitaets- und Konsistenzcheck

| Regel | Bewertung fuer B |
| --- | --- |
| Jede formale StepRelation hat genau einen source step | Erfuellt: `B-MAIN-R01` bis `B-MAIN-R19` haben je einen Quellschritt. |
| Jede formale StepRelation hat genau einen target step | Erfuellt: `B-MAIN-R01` bis `B-MAIN-R19` haben je einen Zielschritt. |
| Relation kind ist erlaubt | Erfuellt: alle formalen Hauptpfadrelationen nutzen `sequence`. |
| Branch-Anker verletzen keine target-Kardinalitaet | Erfuellt: sie sind bewusst noch keine formalen StepRelations. |
| StepRelation.guard [0..1] eingehalten | Erfuellt: jede formale Relation besitzt hoechstens einen Guard-Verweis. |
| Keine technische Direktkopplung | Erfuellt: RuntimeBinding-Fehler bleibt spaeterer Mapping-/Validierungsfall und kein direkter ScenarioStep-Endpoint. |

## Abnahmekontrolle

| Kriterium aus Task 7.7 | Erfuellung |
| --- | --- |
| source step, target step und relation kind vorhanden | Die formale Hauptpfadtabelle enthaelt alle drei Angaben fuer 19 Relationen. |
| Hauptablauf als Graph nachvollziehbar | Der Hauptpfad ist als lineare Kette von `B-MAIN-S01` bis `B-MAIN-S20` definiert. |
| Alternative als Graph vorbereitbar | Branch-Anker zeigen, von welchen Hauptpfadstellen spaetere alternative Zielschritte ausgehen. |
| Exception als Graph vorbereitbar | Branch-Anker zeigen, von welchen Hauptpfadstellen spaetere Exception-Zielschritte ausgehen. |
| Keine Zielschritte vorweggenommen | Alternative- und Exception-Zielsteps werden erst in 7.9 und 7.10 formal angelegt. |
| EAST-ADL-nahe Semantik bleibt sauber | Pflichtfluss bleibt `sequence`; bedingte Abweichungen werden nicht als `include` missbraucht. |

## Konsequenz fuer Task 7.8

Task 7.8 kann nun pruefen, ob wiederverwendbare Pflichtablaeufe als `Include` oder optionale Zusatzablaeufe als `Extend` modelliert werden muessen. Besonders relevant ist die Abgrenzung zwischen:

- verpflichtender Bereitschaftspruefung vor dem assistierten Start,
- optionaler Vivian-Hilfe beziehungsweise unassistiertem Bedienpfad,
- korrigierbaren Alternativen,
- echten Exceptions mit sicherem oder erklaerbarem Ende.
