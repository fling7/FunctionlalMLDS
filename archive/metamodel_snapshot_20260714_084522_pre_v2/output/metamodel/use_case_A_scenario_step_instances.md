# Anwendungsfall A: ScenarioStep-Instanzen

Stand: 2026-07-07

Task: 4.6 `ScenarioStep-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

`ScenarioStep` ist ein geordneter fachlicher Schritt innerhalb genau eines `Scenario`. Die Komposition `Scenario -> ScenarioStep [1..*]` bedeutet: Jeder hier angelegte Schritt gehoert genau zu seinem Owner-Scenario.

In diesem Task werden nur die Step-Instanzen mit `uuid`, `shortName`, `stepNumber`, `kind`, `text` und optionalem `performedBy` angelegt. Events, Guard Conditions, StateAssertions, CapabilityUses und Runtime-Beziehungen bleiben fuer Task 4.7 bis 4.14 offen.

`performedBy` wird nur gesetzt, wenn `ScenarioStep.kind = actorIntent` ist. In Anwendungsfall A ist kein Schritt als `actorIntent` klassifiziert. Deshalb bleibt `performedBy` fuer alle Step-Instanzen leer. Das ist konsistent mit der Actor/Agent-Trennung: Agentenhandlungen werden hier als `systemResponse` modelliert und spaeter ueber `CapabilityUse` und `Capability`, nicht ueber Actor-Handlung.

## ScenarioStep-Instanzen fuer `A-MAIN-SC01`

| Owner-Scenario | Step-ID | Metamodellklasse | `uuid` | `shortName` | `stepNumber` | `ScenarioStep.kind` | `performedBy` | `text` |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `A-MAIN-SC01` | `A-MAIN-S01` | `ScenarioStep` | `A-MAIN-S01` | `GueltigesAusloeseereignisFeststellen` | 1 | `environmentObservation` | leer | Ein gueltiges Ausloeseereignis wird fachlich festgestellt. |
| `A-MAIN-SC01` | `A-MAIN-S02` | `ScenarioStep` | `A-MAIN-S02` | `AgentImSzenenbereichFeststellen` | 2 | `environmentObservation` | leer | Der Agent wird im gueltigen Szenenbereich festgestellt. |
| `A-MAIN-SC01` | `A-MAIN-S03` | `ScenarioStep` | `A-MAIN-S03` | `AgentHandlungsbereitFeststellen` | 3 | `environmentObservation` | leer | Der Agent wird als handlungsbereit festgestellt. |
| `A-MAIN-SC01` | `A-MAIN-S04` | `ScenarioStep` | `A-MAIN-S04` | `ZielzoneErreichbarFeststellen` | 4 | `environmentObservation` | leer | Die Zielzone wird als fachlich erreichbar festgestellt. |
| `A-MAIN-SC01` | `A-MAIN-S05` | `ScenarioStep` | `A-MAIN-S05` | `AusfuehrungsrolleAnnehmen` | 5 | `systemResponse` | leer | Der Agent nimmt die Ausfuehrungsrolle an. |
| `A-MAIN-SC01` | `A-MAIN-S06` | `ScenarioStep` | `A-MAIN-S06` | `ZielgerichteteSzenenhandlungAusfuehren` | 6 | `systemResponse` | leer | Der Agent fuehrt die zielgerichtete Szenenhandlung aus. |
| `A-MAIN-SC01` | `A-MAIN-S07` | `ScenarioStep` | `A-MAIN-S07` | `ZielzoneErreichen` | 7 | `environmentObservation` | leer | Der Agent erreicht die Zielzone. |
| `A-MAIN-SC01` | `A-MAIN-S08` | `ScenarioStep` | `A-MAIN-S08` | `ZielzustandVerifizieren` | 8 | `environmentObservation` | leer | Der Zielzustand wird beobachtbar verifiziert. |
| `A-MAIN-SC01` | `A-MAIN-S09` | `ScenarioStep` | `A-MAIN-S09` | `ErgebnisrueckmeldungBestaetigen` | 9 | `environmentObservation` | leer | Die Ergebnisrueckmeldung wird bestaetigt. |

## ScenarioStep-Instanzen fuer `A-ALT-SC01`

| Owner-Scenario | Step-ID | Metamodellklasse | `uuid` | `shortName` | `stepNumber` | `ScenarioStep.kind` | `performedBy` | `text` |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `A-ALT-SC01` | `A-ALT-S01` | `ScenarioStep` | `A-ALT-S01` | `TemporaereBlockadeFeststellen` | 1 | `environmentObservation` | leer | Die temporaere Blockade der Zielzone wird festgestellt. |
| `A-ALT-SC01` | `A-ALT-S02` | `ScenarioStep` | `A-ALT-S02` | `BlockadeAufhebungFeststellen` | 2 | `environmentObservation` | leer | Die Blockade wird fachlich als aufgehoben festgestellt. |

## ScenarioStep-Instanzen fuer `A-EX-SC01`

| Owner-Scenario | Step-ID | Metamodellklasse | `uuid` | `shortName` | `stepNumber` | `ScenarioStep.kind` | `performedBy` | `text` |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `A-EX-SC01` | `A-EX-S01` | `ScenarioStep` | `A-EX-S01` | `DauerhafteBlockadeFeststellen` | 1 | `environmentObservation` | leer | Die dauerhafte Blockade der Zielzone wird festgestellt. |
| `A-EX-SC01` | `A-EX-S02` | `ScenarioStep` | `A-EX-S02` | `AgentFortsetzenHindern` | 2 | `systemResponse` | leer | Der Agent wird am Fortsetzen des Zielpfads gehindert. |
| `A-EX-SC01` | `A-EX-S03` | `ScenarioStep` | `A-EX-S03` | `FehlerabschlussRueckmelden` | 3 | `environmentObservation` | leer | Der nicht erreichbare Zielzustand wird als Fehlerabschluss rueckgemeldet. |

## Sortier- und Besitzcheck

| Scenario | Erwartete Step-Folge | Anzahl Steps | Bewertung |
| --- | --- | ---: | --- |
| `A-MAIN-SC01` | `A-MAIN-S01 -> A-MAIN-S02 -> A-MAIN-S03 -> A-MAIN-S04 -> A-MAIN-S05 -> A-MAIN-S06 -> A-MAIN-S07 -> A-MAIN-S08 -> A-MAIN-S09` | 9 | eindeutig sortiert von `stepNumber = 1` bis `9` |
| `A-ALT-SC01` | `A-ALT-S01 -> A-ALT-S02` | 2 | eindeutig sortiert von `stepNumber = 1` bis `2` |
| `A-EX-SC01` | `A-EX-S01 -> A-EX-S02 -> A-EX-S03` | 3 | eindeutig sortiert von `stepNumber = 1` bis `3` |

## `performedBy`-Entscheidung

| Step-Kategorie | Betroffene Steps | `performedBy` | Begruendung |
| --- | --- | --- | --- |
| `actorIntent` | keine | nicht anwendbar | Kein Schritt beschreibt eine explizite Absichtshandlung einer externen Actor-Rolle. |
| `systemResponse` | `A-MAIN-S05`, `A-MAIN-S06`, `A-EX-S02` | leer | Agentenreaktionen werden nicht als Actor-Handlung modelliert, sondern spaeter ueber `CapabilityUse` und `Capability`. |
| `environmentObservation` | alle uebrigen Steps | leer | Beobachtungs- und Feststellungsschritte werden nicht von einem Actor ausgefuehrt. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.6 | Folgetask |
| --- | --- | --- |
| `Event`-Instanzen und `triggeredBy` | nicht formal angelegt | 4.7 |
| `Condition`-Instanzen und `guard` | nicht formal angelegt | 4.8 |
| `StateAssertion`-Instanzen und `resultingState` | nicht formal angelegt | 4.9 |
| `CapabilityUse`-Instanzen | nicht angelegt | 4.10 |
| `RuntimeAction`-Referenzen | bewusst keine direkte Referenz | 4.13 und 4.14 ueber `RuntimeBinding` |
| `ValidationCase` | nicht angelegt | 4.15 |

## Abnahmekontrolle

| Kriterium aus Task 4.6 | Erfuellung |
| --- | --- |
| Schrittliste mit Nummern vorhanden | 14 `ScenarioStep`-Instanzen besitzen `stepNumber`. |
| Schrittliste mit Text vorhanden | Jede Step-Instanz besitzt ein fachliches `text`-Attribut. |
| Schrittliste mit Art vorhanden | Jeder Step hat genau einen Wert aus `actorIntent`, `systemResponse`, `environmentObservation`. |
| Optionales `performedBy` korrekt behandelt | Alle Steps haben `performedBy = leer`, weil kein Step `actorIntent` ist. |
| Schrittfolge eindeutig sortiert | Jede Scenario-Tabelle beginnt bei `1` und steigt ohne Luecke an. |
| Jeder Step gehoert genau zu einem Scenario | Jede Zeile besitzt genau ein `Owner-Scenario`. |
| Keine technische Kurzschaltung | Kein Step referenziert RuntimeAction, API, Topic, Tool oder Controlleraktion direkt. |

## Konsequenz fuer Task 4.7

Task 4.7 kann nun die Event-Instanzen fuer A anlegen und sie den hier formalisierten Step-IDs zuordnen oder als ungenutzt markieren.
