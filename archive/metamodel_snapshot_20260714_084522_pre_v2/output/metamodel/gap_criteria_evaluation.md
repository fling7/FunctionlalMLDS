# Bewertung 11.3: Luecken anhand der Kern- und Ergaenzungskriterien

Stand: 2026-07-07

Task: 11.3 `Jede identifizierte Luecke anhand der Kriterien bewerten`

Zweck: Diese Datei konsolidiert die A- und B-Luecken aus den frueheren Entscheidungsmatrizen und bewertet jede identifizierte Luecke mit genau einer der Entscheidungen:

- `Kern`
- `Ergaenzung`
- `kein Modellbedarf`

Bezugsdateien:

- `core_adaptation_criteria.md`
- `extension_model_criteria.md`
- `use_case_A_non_modelable_gaps.md`
- `use_case_A_gap_decision_matrix.md`
- `use_case_B_non_modelable_gaps.md`
- `use_case_B_gap_decision_matrix.md`
- `common_concepts_A_B.md`
- `differences_A_B.md`
- `entity_agent_scene_object_decision.md`
- `state_assertion_object_state_decision.md`
- `capability_runtime_vivian_action_decision.md`
- `spatial_relationship_decision.md`
- `interaction_object_affordance_decision.md`
- `agent_goal_role_runtime_profile_decision.md`

## Bewertungsregel

Die Bewertung nutzt die Kriterien aus 11.1 und 11.2:

| Entscheidung | Regel |
| --- | --- |
| `Kern` | Der Bedarf ist allgemein, kompakt, EAST-ADL-nah, wiederverwendbar, rueckwaertskompatibel und verletzt keine Kerninvariante. |
| `Ergaenzung` | Der Bedarf ist maschinenlesbar relevant, aber domaenen-, runtime-, dialog-, spatial-, interaktions-, test- oder safety-spezifisch und kann optional an den Kern andocken. |
| `kein Modellbedarf` | Der Bedarf ist fuer die aktuelle Baseline ausreichend mit Kernklassen, Expressions, StateAssertions, StepRelations oder Dokumentation abgedeckt. |

`B-GAP-09` enthaelt zwei fachlich trennbare Unterbedarfe. Damit jede Zeile genau eine Entscheidung erhaelt, wird er hier in `B-GAP-09a` und `B-GAP-09b` aufgeteilt.

## Gesamtergebnis

| Kategorie | Gaps | Ergebnis |
| --- | --- | --- |
| `Kern` | `A-GAP-06`, `A-GAP-08`, `B-GAP-09a` | Zwei minimale Kernanpassungen werden bestaetigt: optionale `Entity.kind`-Typisierung und optionale Trace-Kante `Effect -> StateAssertion`. |
| `Ergaenzung` | `A-GAP-01`, `A-GAP-02`, `A-GAP-03`, `A-GAP-04`, `A-GAP-05`, `A-GAP-07`, `B-GAP-01` bis `B-GAP-08`, `B-GAP-09b` | Alle groesseren fachlichen, spatialen, dialogischen, interaktiven, regelbasierten, runtime- oder validationnahen Bedarfe bleiben optionale Module. |
| `kein Modellbedarf` | `B-GAP-10`, `B-GAP-11`, `B-GAP-12` | Fuer die aktuelle B-Baseline reichen vorhandene Scenario-, StepRelation-, Condition- und StateAssertion-Strukturen. |

Die Entscheidung ist bewusst streng: Hohe fachliche Wichtigkeit eines Themas bedeutet nicht automatisch Kernreife.

## Bewertung der A-Luecken

| Gap-ID | Kurzbeschreibung | Entscheidung | Ausschlaggebende Kriterien | Begruendung | Folge fuer 11.4/11.5 |
| --- | --- | --- | --- | --- | --- |
| `A-GAP-01` | Strukturierte Raumsemantik fuer `inside`, `at`, `near`, `reachable`, `movingTo` | `Ergaenzung` | E1, E2, E3, E4 | Raeumliche Semantik ist fuer A wichtig, aber detailreich, geometrie- und runtime-nah. Der Kern kann qualitative Raumangaben bereits ueber `Condition.expression`, `Event.expression` und `StateAssertion.expectedState` tragen. | In 11.5 als `SpatialSemanticsModule` nur bei Bedarf spezifizieren. |
| `A-GAP-02` | Explizite Zustandsuebergaenge des Agenten | `Ergaenzung` | E1, E2, E5, E7 | Agentenrollen und Aktivitaetswechsel sind nachvollziehbar ueber Condition, Event, Capability, Effect und StateAssertion modellierbar. Ein formaler Automat ist maschinenlesbar nuetzlich, aber kein Pflichtkern. | In 11.5 als gemeinsames `StateTransitionModule` vormerken. |
| `A-GAP-03` | Strukturierte Event-Quelle, Event-Ziel und Payload | `Ergaenzung` | E1, E5, E6, E8 | Eventdetails sind fuer Korrelation und Automatisierung relevant, aber `Event.expression` reicht fuer die Baseline. Quelle/Ziel/Payload duerfen Actor- und Entity-Semantik nicht vermischen. | In 11.5 als optionales `EventDetailModule` vormerken. |
| `A-GAP-04` | Ordnung, Abhaengigkeit und Transaktion innerhalb einer RuntimeBinding | `Ergaenzung` | E1, E6, E9, S4 | Reihenfolge, Retry, Rollback und Transaktion sind technische Ausfuehrungssemantik unterhalb von `RuntimeBinding`. Sie duerfen keine direkte Step-zu-RuntimeAction-Kante erzeugen. | In 11.5 als `RuntimeExecutionModule` vormerken. |
| `A-GAP-05` | Formale Testorakel fuer zusammengesetzte Expected Outcomes | `Ergaenzung` | E1, E5, E7 | Formale Assertion-Logik ist fuer Testautomatisierung wertvoll, aber eine eigene Logiksemantik wuerde den Kern ueberladen. | In 11.5 als `ValidationAssertionModule` vormerken. |
| `A-GAP-06` | Explizite Typisierung von Entity-Instanzen | `Kern` | K1, K2, K3, K4, K6, K7 | Eine optionale, grobe `Entity.kind [0..1]`-Typisierung ist allgemein, kompakt, EAST-ADL-nah genug als Identifikationshilfe und in A sowie B wiederverwendbar. Sie verletzt keine Kerntrennung, solange die Kategorien stabil und grob bleiben. | In 11.4 als minimale Kernanpassung spezifizieren. |
| `A-GAP-07` | Objekt-Affordances fuer interaktive Szenenobjekte | `Ergaenzung` | E1, E2, E3, E4 | Affordances sind fuer B stark und fuer A optional, aber nicht jede Entity ist bedienbar. Bedienpunkte, Manipulationsarten und Interaktionszonen sollen an `Entity` andocken statt den Kern zu belasten. | In 11.5 als `InteractionObjectModule` vormerken. |
| `A-GAP-08` | Trace-Kante von `Effect` zu konkreter `StateAssertion` | `Kern` | K1, K2, K3, K4, K5, K6, K7 | Die Rueckbindung von promised Effects auf beobachtbare StateAssertions ist allgemein traceability-relevant, kompakt und rueckwaertskompatibel, wenn sie optional und nicht-kompositiv bleibt. | In 11.4 als minimale Kernanpassung spezifizieren. |

## Bewertung der B-Luecken

| Gap-ID | Kurzbeschreibung | Entscheidung | Ausschlaggebende Kriterien | Begruendung | Folge fuer 11.4/11.5 |
| --- | --- | --- | --- | --- | --- |
| `B-GAP-01` | Strukturierte Interaktionsobjekt-Affordances der Kaffeemaschine | `Ergaenzung` | E1, E2, E3, E4, E5 | Starttaste, Tassenbereich und Programmauswahl sind zentrale B-Semantik, aber nicht allgemeiner Kernbedarf. Ein Modul kann an `Entity`, `Event`, `Condition`, `StateAssertion` und `Capability` andocken. | In 11.5 als hoch priorisiertes `InteractionObjectModule` spezifizieren. |
| `B-GAP-02` | Expliziter Objektzustandsautomat fuer Kaffeemaschine und BrewingRequest | `Ergaenzung` | E1, E2, E5, E7 | Maschinen- und Request-Lifecycle sind fachlich wichtig, aber die Baseline bleibt mit StateAssertions und Guards gueltig. Ein StateMachine-Kern wuerde einfache Use Cases aufblaehen. | In 11.5 als `StateTransitionModule` vormerken. |
| `B-GAP-03` | Strukturierter Vivian-Dialog und Guidance-Content | `Ergaenzung` | E1, E2, E3, E7 | Dialogakte, GuidanceContent, Modalitaet und Erklaerstrategie sind assistenzspezifisch. Sie duerfen `Capability` nicht in ein Dialogmodell verwandeln. | In 11.5 als `AssistantInteractionModule` vormerken. |
| `B-GAP-04` | Benutzerbestaetigungs- und Autorisierungssemantik | `Ergaenzung` | E1, E2, E5, E7 | Positive Bestaetigung ist in der Baseline ueber Event, Condition und StateAssertion abbildbar. Ablehnung, Timeout, Widerruf und Gueltigkeitsdauer brauchen bei erweitertem Scope ein Modul. | In 11.5 als Teil von Assistant-/Authorization-/Recovery-Semantik vormerken. |
| `B-GAP-05` | Bereitschaftspruefung als RuleSet oder Decision-Objekt | `Ergaenzung` | E1, E5, E7, Q8 | Readiness-Regeln sind objekt- und domaenenspezifisch. Sie sind fuer B hoch relevant, aber keine allgemeine Kernsemantik. | In 11.5 als `DecisionRuleModule` vormerken. |
| `B-GAP-06` | Strukturierte Event-Quelle, Event-Ziel und Payload | `Ergaenzung` | E1, E5, E6, E8 | Wie A-GAP-03: Maschinenlesbare Eventdetails sind nuetzlich, aber die Baseline nutzt `Event.expression` ausreichend. | In 11.5 als gemeinsames `EventDetailModule` vormerken. |
| `B-GAP-07` | Ordnung, Abhaengigkeit und Fehlerbehandlung innerhalb einer RuntimeBinding | `Ergaenzung` | E1, E6, E9, S4 | Mehrere RuntimeActions in B brauchen bei Ausfuehrbarkeit Reihenfolge, Retry und Fehlerbehandlung. Das bleibt technische Runtime-Semantik unter `RuntimeBinding`. | In 11.5 als `RuntimeExecutionModule` vormerken. |
| `B-GAP-08` | Strukturierte RuntimeProfile und Schemas | `Ergaenzung` | E1, E3, E9, S4 | Plattformprofile, Adapterversionen und Schemamodelle sind toolchain- und codegenerierungsnah. Sie gehoeren nicht in fachliche Kernklassen. | In 11.5 als `RuntimeProfileModule` beziehungsweise Schema-Ergaenzung vormerken. |
| `B-GAP-09a` | Trace-Kante `Effect -> StateAssertion` | `Kern` | K1, K2, K3, K4, K5, K6, K7 | Dieser Teil bestaetigt A-GAP-08. Die Kante ist fachlich, kompakt, wiederverwendbar und verbessert den automatischen Nachweis von Effects. | In 11.4 gemeinsam mit A-GAP-08 spezifizieren. |
| `B-GAP-09b` | Formale ValidationOutcome-Struktur zu StateAssertions | `Ergaenzung` | E1, E5, E7 | Komplexe Testorakel, Negation, Temporalitaet und zusammengesetzte Outcomes sind wichtig fuer Testautomatisierung, aber zu gross fuer den Kern. | In 11.5 als `ValidationAssertionModule` vormerken. |
| `B-GAP-10` | Cross-Scenario Entry-/Return- und VariationPoint-Semantik | `kein Modellbedarf` | vorhandene Kernabbildung ausreichend | Die aktuelle B-Baseline ist mit `Scenario.kind` und `StepRelation.kind` nachvollziehbar. VariationPoints werden erst bei grosser Variantenautomatisierung relevant. | Nicht in 11.4/11.5 aufnehmen; nur bei erweitertem Varianten-Scope wieder oeffnen. |
| `B-GAP-11` | Safety- und Hazard-Argumentation fuer sicheren Nicht-Start | `kein Modellbedarf` | Scope-Grenze | Sicherer Nicht-Start ist fachlich ueber Conditions, StateAssertions und ValidationCase abbildbar. Ein SafetyCase mit Hazard, ASIL und Mitigation ist ein eigener erweiterter Scope. | Nicht in 11.4/11.5 aufnehmen, solange kein Safety-Scope beschlossen wird. |
| `B-GAP-12` | Formale Abbruch-, Timeout- und Recovery-Pfade | `kein Modellbedarf` | vorhandene Kernabbildung ausreichend | Weitere Abbruch- und Timeout-Pfade koennen als Scenarios und StepRelations modelliert werden. Ein Policy-Modell ist fuer die aktuelle Baseline nicht notwendig. | Nicht in 11.4/11.5 aufnehmen; bei Vollstaendigkeitsscope als Recovery-Modul neu pruefen. |

## Zusammengefuehrte Entscheidungen

Die Einzelauswertung fuehrt zu zwei Kernanpassungen und einer Menge optionaler Module.

| Entscheidung | Konsolidierter Bedarf | Belegte Gaps | Begruendung |
| --- | --- | --- | --- |
| `Kern` | Optionale `Entity.kind [0..1]`-Typisierung | `A-GAP-06`, B-Abgleich aus `use_case_B_gap_decision_matrix.md` | Allgemein, kompakt, in A und B hilfreich, rueckwaertskompatibel. |
| `Kern` | Optionale nicht-kompositive Trace-Kante `Effect -> StateAssertion [0..*]` | `A-GAP-08`, `B-GAP-09a` | Allgemeiner Traceability-Gewinn zwischen fachlicher Wirkung und beobachtbarer Zustandsaussage. |
| `Ergaenzung` | `SpatialSemanticsModule` | `A-GAP-01`, B-Bedienzonen indirekt | Raumdetails sind maschinenlesbar relevant, aber detailreich und optional. |
| `Ergaenzung` | `StateTransitionModule` | `A-GAP-02`, `B-GAP-02` | Gemeinsamer Bedarf, aber formale Automaten sind kein Pflichtkern. |
| `Ergaenzung` | `EventDetailModule` | `A-GAP-03`, `B-GAP-06` | Eventquelle, Ziel und Payload bleiben optional strukturierbar. |
| `Ergaenzung` | `RuntimeExecutionModule` | `A-GAP-04`, `B-GAP-07` | Technische Orchestrierung bleibt unter `RuntimeBinding`. |
| `Ergaenzung` | `ValidationAssertionModule` | `A-GAP-05`, `B-GAP-09b` | Formale Testlogik ist optional und testmodellspezifisch. |
| `Ergaenzung` | `InteractionObjectModule` | `A-GAP-07`, `B-GAP-01` | B-stark, A-optionaler Bedarf; gehoert an `Entity`, nicht in den Kern. |
| `Ergaenzung` | `AssistantInteractionModule` | `B-GAP-03`, teilweise `B-GAP-04` | Vivian-Dialog, Guidance und Antwortpolitik sind B-spezifisch. |
| `Ergaenzung` | `DecisionRuleModule` | `B-GAP-05` | Readiness-Regeln sind wichtig, aber objekt-/domaenenspezifisch. |
| `Ergaenzung` | `RuntimeProfileModule` | `B-GAP-08`, 10.8-Entscheidung | Plattformprofile und Schemas sind technisch und optional. |
| `kein Modellbedarf` | ScenarioVariation fuer aktuelle Baseline | `B-GAP-10` | `Scenario.kind` und `StepRelation.kind` reichen aktuell. |
| `kein Modellbedarf` | SafetyArgument fuer aktuelle Baseline | `B-GAP-11` | Safety ist moeglicher Zukunftsscope, aber keine aktuelle Modellluecke. |
| `kein Modellbedarf` | RecoveryPolicy fuer aktuelle Baseline | `B-GAP-12` | Weitere Pfade koennen ohne Metamodellumbau als Scenarios ergaenzt werden. |

## Konsequenz fuer 11.4

11.4 soll nur die beiden minimalen Kernanpassungen spezifizieren:

1. `Entity.kind: EntityKind [0..1]`
2. optionale nicht-kompositive Referenz von `Effect` auf `StateAssertion [0..*]`

Alle anderen Bedarfe sollen nicht in 11.4 landen.

## Konsequenz fuer 11.5

11.5 soll ein Ergaenzungsmodell oder mehrere anschlussfaehige Ergaenzungsmodule spezifizieren. Nach dieser Bewertung sind besonders relevant:

| Prioritaet | Module | Grund |
| --- | --- | --- |
| hoch | `InteractionObjectModule`, `AssistantInteractionModule`, `DecisionRuleModule`, `StateTransitionModule` | Diese Module tragen die zentralen Beispielsemantiken aus B und den gemeinsamen Zustandsbedarf. |
| mittel | `SpatialSemanticsModule`, `EventDetailModule`, `RuntimeExecutionModule`, `ValidationAssertionModule`, `RuntimeProfileModule` | Wichtig fuer Automatisierung, Runtime-Integration und formale Validierung, aber nicht zwingend fuer die Baseline. |
| zurueckgestellt | `ScenarioVariationModule`, `SafetyArgumentModule`, `RecoveryPolicyModule` | Fuer den aktuellen Scope kein Modellbedarf; spaeter bei Varianten-, Safety- oder Robustheitsscope neu bewerten. |

## Invariantencheck

| Invariante | Ergebnis der Bewertung |
| --- | --- |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | bleibt erhalten; Runtime-Orchestrierung wird nur als Ergaenzung unter `RuntimeBinding` behandelt. |
| `Capability` bleibt fachlich | bleibt erhalten; Dialog, DecisionRules und RuntimeProfile werden nicht in Capability hineingezogen. |
| Actor/Agent-Trennung | bleibt erhalten; Eventdetails und AssistantInteraction duerfen Actor-Rollen nicht zu Agent-Instanzen machen. |
| Kern bleibt kompakt | bleibt erhalten; nur zwei minimale, optionale Kernanpassungen werden weitergefuehrt. |
| Existing A/B models bleiben gueltig | bleibt erhalten; alle Kernanpassungen sind optional, alle Module sind zuschaltbar. |

## Abnahmekontrolle

| Kriterium aus Task 11.3 | Erfuellung |
| --- | --- |
| Bewertungstabelle vorhanden | A- und B-Luecken sind in getrennten Bewertungstabellen konsolidiert. |
| Jede Luecke hat Entscheidung | Jede Gap-Zeile hat genau eine Entscheidung: `Kern`, `Ergaenzung` oder `kein Modellbedarf`. |
| Kriterienbezug vorhanden | Jede Zeile nennt ausschlaggebende Kriterien oder den Grund fuer ausreichende Kernabbildung. |
| Kernkandidaten isoliert | Nur `Entity.kind` und `Effect -> StateAssertion` werden fuer 11.4 weitergefuehrt. |
| Ergaenzungsbedarfe isoliert | Optionale Module sind fuer 11.5 priorisiert. |
| Kein Modellbedarf explizit | `B-GAP-10`, `B-GAP-11` und `B-GAP-12` sind fuer die aktuelle Baseline bewusst nicht weiterzufuehren. |

## Kritischer Review-Abgleich

Ein kritischer Review-Agent hat die Klassifikation gegengeprueft und keine harte Fehlklassifikation gemeldet. Der Review bestaetigte insbesondere:

- Nur `A-GAP-06` und die zusammengefuehrte Trace-Kante aus `A-GAP-08`/`B-GAP-09a` gehoeren in den Kern.
- `StateTransition`, `EventDetail`, `RuntimeExecution`, `ValidationAssertion`, `InteractionObject`, `AssistantInteraction`, `DecisionRule` und `RuntimeProfile` bleiben Ergaenzungsmodelle.
- `B-GAP-10`, `B-GAP-11` und `B-GAP-12` sind fuer die aktuelle Baseline `kein Modellbedarf`, auch wenn sie bei erweitertem Varianten-, Safety- oder Recovery-Scope spaeter als Module wieder geoeffnet werden koennen.
- `B-GAP-09` muss gesplittet bleiben: Nur `Effect -> StateAssertion` ist Kern; formale ValidationOutcome-Logik bleibt Ergaenzung.
