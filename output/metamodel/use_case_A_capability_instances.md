# Anwendungsfall A: Capability-Instanzen

Stand: 2026-07-07

Task: 4.11 `Capability-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Eine `Capability` beschreibt eine fachliche Faehigkeit. Sie sagt, was im Modell fachlich geleistet werden kann, aber nicht, wie eine Plattform diese Faehigkeit technisch ausfuehrt.

Deshalb gilt fuer alle Capability-Instanzen in Anwendungsfall A:

- keine technischen Endpunkte,
- keine Tools,
- keine Topics,
- keine Controller- oder Engine-Befehle,
- keine direkte RuntimeAction-Referenz.

Eine `CapabilityUse` referenziert genau eine `Capability`. Die drei geplanten Capability-IDs aus Task 4.10 werden hier formal angelegt. Die promised Effects werden als stabile Effect-IDs vorbereitet und in Task 4.12 formal als `Effect`-Instanzen ausgearbeitet.

## Angelegte Capability-Instanzen

| Capability-ID | Metamodellklasse | `uuid` | `shortName` | Fachlicher Intent | Bereitstellende Entity | Preconditions | Planned `promisedEffect` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `Capability` | `A-CAP-ADOPT-EXECUTOR-ROLE` | `AgentRolleExecutorAnnehmen` | Der Agent kann fachlich in die Ausfuehrungsrolle wechseln, wenn er sich im gueltigen Szenenbereich befindet, nicht blockiert ist und die Zielzone erreichbar ist. | `AgentBody` | `A-GUARD-S05`; zusaetzlich gestuetzt durch `A-P2`, `A-P3`, `A-P4` | `A-EFF-ROLE-EXECUTOR`, `A-EFF-AGENT-ACTING` |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `Capability` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `ZielgerichteteSzenenhandlungAusfuehren` | Der Agent kann eine fachliche Handlung in Richtung Zielzone ausfuehren, wenn er die Ausfuehrungsrolle besitzt und die Zielzone weiterhin erreichbar ist. | `AgentBody` | `A-GUARD-S06`; zusaetzlich gestuetzt durch `A-Q1`, `A-Q7` | `A-EFF-AGENT-MOVING-TO-TARGET`, `A-EFF-TARGET-OCCUPIED` |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `Capability` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `BlockiertenZielpfadSicherStoppen` | Der Agent kann bei dauerhaft blockierter Zielzone sicher am Fortsetzen des Zielpfads gehindert werden, sodass kein falscher Erfolg gemeldet wird. | `AgentBody` | `A-GUARD-EX-S02`; zusaetzlich gestuetzt durch `A-GUARD-EX-S01`, `A-GUARD-EX-R01` | `A-EFF-AGENT-WAITING`, `A-EFF-ROLE-BLOCKED` |

## Rueckbindung an CapabilityUse

| CapabilityUse | Owner-Step | Referenzierte Capability | Konsistenzbewertung |
| --- | --- | --- | --- |
| `A-CU-001` | `A-MAIN-S05` | `A-CAP-ADOPT-EXECUTOR-ROLE` | erfuellt: die Capability beschreibt genau den fachlichen Rollenwechsel des Steps. |
| `A-CU-002` | `A-MAIN-S06` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | erfuellt: die Capability beschreibt die zielgerichtete Agentenhandlung. |
| `A-CU-003` | `A-EX-S02` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | erfuellt: die Capability beschreibt das sichere Stoppen des blockierten Zielpfads. |

## Fachliche Preconditions je Capability

| Capability-ID | Referenzierte Conditions | Fachliche Lesart |
| --- | --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-GUARD-S05`, `A-P2`, `A-P3`, `A-P4` | Rollenannahme ist nur zulaessig, wenn Agent, Szenenbereich und Zielerreichbarkeit gueltig sind. |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-GUARD-S06`, `A-Q1`, `A-Q7` | Zielhandlung ist nur zulaessig, wenn Rolle und Zielpfad konsistent sind und keine relevante Blockade offen bleibt. |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-GUARD-EX-S01`, `A-GUARD-EX-S02`, `A-GUARD-EX-R01` | Sicheres Stoppen ist nur zulaessig, wenn die Zielzone dauerhaft blockiert ist. |

## Planned promised Effects

| Capability-ID | Planned Effect-ID | Erwartete beobachtbare Wirkung | Bezug zu StateAssertions |
| --- | --- | --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-EFF-ROLE-EXECUTOR` | Der Agent besitzt den Rollenzustand `executor`. | `A-SA-S05-01` |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-EFF-AGENT-ACTING` | Der Agent ist fachlich in einem aktiven Reaktionszustand. | `A-SA-S05-02` |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-EFF-AGENT-MOVING-TO-TARGET` | Der Agent fuehrt die Zielhandlung in Richtung Zielzone aus. | `A-SA-S06-01` |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-EFF-TARGET-OCCUPIED` | Die Zielzone wird durch die Agentenhandlung erreicht oder belegt. | `A-SA-S06-02` |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-EFF-AGENT-WAITING` | Der Agent setzt die Zielhandlung nicht fort und bleibt in einem sicheren Wartezustand. | `A-EX-SA03` |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-EFF-ROLE-BLOCKED` | Der Rollenzustand des Agenten ist fuer den Zielpfad blockiert. | `A-EX-SA04` |

## Warum Beobachtungssteps keine eigenen Capabilities bekommen

Die Beobachtungssteps in A stellen Ereignisse, Bedingungen oder Ergebniszustaende fest. Sie sind bereits durch `Event`, `Condition` und `StateAssertion` abgedeckt. Eine zusaetzliche Beobachtungs-Capability waere nur dann noetig, wenn das Modell eine aktive fachliche Prueffaehigkeit als eigene Systemleistung beschreiben soll.

Fuer den aktuellen kompakten A-Durchlauf bleiben solche aktiven Pruef- oder Feedbackfaehigkeiten bewusst aus dem Modell heraus, damit die Capability-Schicht nur echte fachliche Systemreaktionen enthaelt.

## Keine technischen Daten in Capabilities

| Capability-ID | Fachlich sauber? | Begruendung |
| --- | --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | ja | Beschreibt Rollenwechsel und beobachtbare Agentenzustaende, keine technische Ausfuehrung. |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | ja | Beschreibt zielgerichtete Szenenhandlung und Zielzonenwirkung, keine technische Ausfuehrung. |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | ja | Beschreibt sicheren fachlichen Blockadeabschluss, keine technische Ausfuehrung. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.11 | Folgetask |
| --- | --- | --- |
| Formale `Effect`-Instanzen | Effect-IDs vorbereitet, Details folgen | 4.12 |
| `RuntimeBinding` | nicht angelegt | 4.13 |
| `RuntimeAction` | nicht angelegt | 4.14 |
| `ValidationCase` | nicht angelegt | 4.15 |

## Abnahmekontrolle

| Kriterium aus Task 4.11 | Erfuellung |
| --- | --- |
| Capability-Instanzen vorhanden | Drei Capabilities sind angelegt. |
| Jede Capability hat fachlichen Intent | Jede Capability besitzt eine Intent-Beschreibung. |
| Jede Capability hat Preconditions | Jede Capability referenziert fachliche Conditions. |
| Jede Capability hat promised Effects | Jede Capability besitzt mindestens zwei geplante promised Effect-IDs. |
| Jede CapabilityUse referenziert eine existierende Capability | `A-CU-001` bis `A-CU-003` sind rueckgebunden. |
| Keine Capability enthaelt technische Ausfuehrungsdaten | Keine Capability-Zeile enthaelt technische Plattform-, Endpunkt-, Topic-, Tool- oder Controllerdaten. |

## Konsequenz fuer Task 4.12

Task 4.12 kann nun die geplanten Effect-IDs `A-EFF-*` formal als `Effect`-Instanzen anlegen und dabei fuer jede Capability mindestens einen beobachtbaren Effect bestaetigen.
