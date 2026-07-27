# Anwendungsfall A: Entscheidungsmatrix zu harten Luecken

Stand: 2026-07-07

Task: 5.4 `Fuer jede Luecke Entscheidung vorbereiten: Kernanpassung oder Ergaenzungsmodell`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Bezugsdateien:

- `use_case_A_non_modelable_gaps.md`
- `use_case_A_indirect_modelability.md`
- `dynamic_functional_mlds_specification.md`
- `invariants.md`

## Ziel der Entscheidung

Diese Matrix bereitet fuer jede in Task 5.3 identifizierte Luecke eine Modellentscheidung vor. Sie aendert das Metamodell noch nicht. Sie legt aber fest, ob eine Luecke eher in den kompakten Kern gehoert, als optionales Ergaenzungsmodell angebunden werden sollte oder fuer Anwendungsfall A keinen unmittelbaren Modellbedarf erzeugt.

Die Entscheidung ist bewusst A-spezifisch. Eine endgueltige gemeinsame Entscheidung fuer A und B folgt erst nach der Ausarbeitung von Vivian/Kaffeemaschine und der gemeinsamen Analyse in den spaeteren Tasks.

## Entscheidungskriterien

| Entscheidung | Kriterium | Bevorzugt, wenn |
| --- | --- | --- |
| `Kernanpassung` | Allgemeingueltig, kompakt, traceability-relevant, rueckwaertskompatibel | die Aenderung fuer fast alle Dynamic-Functional-MLDS-Modelle nuetzlich ist, nur wenige Attribute oder optionale Kanten braucht und keine EAST-ADL-nahe Semantik verfaelscht |
| `Ergaenzungsmodell` | Domaenen- oder Ausfuehrungsspezifik, optional, groesserer Strukturbedarf | die Luecke nur fuer bestimmte Runtimes, Spatial Reasoning, Interaktionsobjekte, formale Tests oder ausfuehrbare Orchestrierung gebraucht wird |
| `Kein unmittelbarer Modellbedarf fuer A` | Out of Scope oder fuer A ausreichend textuell abbildbar | die Luecke nur Implementierungsdetails betrifft oder das A-Beispiel mit vorhandenen Klassen und dokumentierten Konventionen belastbar bleibt |

## Entscheidungsmatrix

| Gap-ID | Vorbereitete Entscheidung | Entscheidendes Kriterium | Risiko der Entscheidung | Auswirkung auf bestehendes Modell | Empfehlung fuer naechste Schritte |
| --- | --- | --- | --- | --- | --- |
| A-GAP-01 | `Ergaenzungsmodell`: Spatial Semantics | Raumrelationen, Koordinaten, Toleranzen und Referenzrahmen sind VR-/Simulations-spezifisch und wuerden den Kern deutlich vergroessern. | Ohne Ergaenzung bleiben `inside`, `at`, `near`, `reachable` und `movingTo` nur als Strings auswertbar. Mit Kernintegration wuerde das kompakte Modell Richtung Geometrie-/Navigationmodell kippen. | Keine bestehende Klasse wird ungueltig. Optionales Spatial-Modul kann an `Entity`, `Condition` und `StateAssertion` andocken. | Fuer A nicht sofort umsetzen; in Task 10.6 erneut pruefen. Falls noetig: `SpatialRelation`, `SpatialFrame`, `SpatialRegion` und `SpatialAssertion` als optionales Modul entwerfen. |
| A-GAP-02 | `Ergaenzungsmodell`: State/Transition Semantics, spaeter B-Abgleich | Explizite Zustandsautomaten sind fachlich nuetzlich, aber nicht jeder UseCase braucht erlaubte Transitionen, Source-/Target-State und Trigger als eigene Objekte. | Ohne Ergaenzung bleiben Zustandswechsel verteilt auf `Condition`, `Event`, `ScenarioStep` und `StateAssertion`. Als Kernklasse koennte `StateTransition` einfache Szenarien unnoetig aufblaehen. | Bestehende StateAssertions bleiben gueltig. Ein optionales Modul kann `Entity` oder `Agent` mit States und Transitions verbinden. | Nach B pruefen, ob Kaffeemaschine und Vivian denselben Bedarf erzeugen. Bis dahin kein Kernumbau. |
| A-GAP-03 | `Ergaenzungsmodell`: Event Payload and Participation | Quelle, Ziel, Payload, Kanal und Verbrauchsstatus sind fuer Ereignisverarbeitung relevant, aber nicht fuer jeden fachlichen Szenarioschritt notwendig. | Ohne Ergaenzung bleiben Eventdetails in `Event.expression`. Bei Kernintegration droht Vermischung von `Actor` als Rolle mit Ereignisquelle als Instanz. | `Event` bleibt kompakt. Optionales Modul kann `Event` mit `source`, `target`, `payload`, `channel` und `consumedBy` erweitern. | Fuer A nur dokumentieren. Bei automatischer Event-Korrelation oder Runtime-Signalabgleich als Event-Ergaenzungsmodell spezifizieren. |
| A-GAP-04 | `Ergaenzungsmodell`: Runtime Orchestration | Reihenfolge, Abhaengigkeiten, Transaktionen und Rollback gehoeren zur technischen Orchestrierung und nicht zur fachlichen Szenario- oder Capability-Semantik. | Ohne Ergaenzung bleibt die konkrete Ausfuehrungsreihenfolge dokumentarisch. Als Kernanpassung wuerde `RuntimeBinding` in Richtung Workflow-Engine kippen. | Bestehende RuntimeBindings bleiben gueltig. Ein optionales Runtime-Orchestration-Modul kann `RuntimeAction`-Sequenzen, Dependencies, Retry und Rollback beschreiben. | Fuer A keine Kernanpassung. Bei ausfuehrbarer Codegenerierung spaeter als Runtime-Ergaenzungsmodell spezifizieren. |
| A-GAP-05 | `Ergaenzungsmodell`: Validation/Assertion Semantics | Formale Testorakel mit Logik, Zeitoperatoren, Negation und Toleranzen sind fuer Testautomatisierung wichtig, aber nicht fuer jede fachliche Modellierung. | Ohne Ergaenzung bleiben Expected Outcomes teilweise halbformal. Als Kernbestandteil wuerde eine Assertionsprache den Kern ueberfrachten und eine eigene Logiksemantik erzwingen. | `ValidationCase.expectedOutcome [1..*]` bleibt gueltig. Optionales Modul kann Expected Outcomes formal verfeinern. | Fuer Dissertationstext als optionales Validation-Ergaenzungsmodell markieren. Nicht in den Kern aufnehmen, solange manuelle oder halbformale Validierung reicht. |
| A-GAP-06 | `Kernanpassung minimal`: optionale `Entity.kind`-Typisierung | Entity-Typisierung ist allgemein, kompakt, fuer A und B erwartbar und hilft, Agent, Zone, Asset, Signal und Zustandstraeger maschinenlesbar zu unterscheiden. | Ohne Kernanpassung bleiben Entity-Arten Tabellenkonvention. Zu detaillierte Enumeration koennte domaenenspezifische Typen festschreiben. | Rueckwaertskompatibel, wenn `Entity.kind` optional bleibt. Bestehende Entity-Instanzen koennen schrittweise typisiert werden. | Spaeter als minimale Kernanpassung vorbereiten: `Entity.kind: EntityKind [0..1]` mit stabilen Oberkategorien `agent`, `asset`, `zone`, `signal`, `stateObject`. |
| A-GAP-07 | `Ergaenzungsmodell`: Interaction Object/Affordance | Bedienpunkte, erlaubte Manipulationen, Inputs, Objektreaktionen und objektseitige Constraints betreffen interaktive Assets; nicht jede Entity ist ein Interaktionsobjekt. | Ohne Ergaenzung bleibt ein Interaktionsobjekt nur generische `Entity` plus `Capability`. Als Kernbestandteil wuerde jedes Szenenobjekt mit Bediensemantik belastet. | Bestehende Entities und Capabilities bleiben gueltig. Ein optionales Modul kann an `Entity` und `Capability` andocken. | Fuer B sehr wahrscheinlich relevant. In Task 6.4 und 10.7 gezielt pruefen; fuer A noch nicht in den Kern aufnehmen. |
| A-GAP-08 | `Kernanpassung minimal`: optionale Trace-Kante `Effect -> StateAssertion` | Die Rueckbindung versprochener Effects auf konkrete erwartete Zustandsaussagen ist zentral fuer Traceability und Validierung, aber als optionale Referenz kompakt haltbar. | Ohne Kante bleibt der Nachweis dokumentarisch. Mit zu starker Kante koennte eine wiederverwendbare `Capability` zu eng an einzelne Scenario-StateAssertions gekoppelt werden. | Rueckwaertskompatibel, wenn die Kante optional und nicht besitzend ist. Bestehende Effects bleiben gueltig; vorhandene dokumentierte Traces koennen formalisiert werden. | Fuer spaetere Kernanpassung vormerken: optionale nicht-kompositive Referenz `Effect.evidencedBy StateAssertion [0..*]` oder aequivalenter Name. |

## Kompakte A-Empfehlung

| Kategorie | Gaps | Begruendung |
| --- | --- | --- |
| Minimaler Kernkandidat | A-GAP-06, A-GAP-08 | Kleine, rueckwaertskompatible Praezisierungen mit allgemeinem Nutzen fuer Traceability und Modellpruefung. |
| Optionales Ergaenzungsmodell | A-GAP-01, A-GAP-02, A-GAP-03, A-GAP-04, A-GAP-05, A-GAP-07 | Fachlich wichtig, aber entweder domaenen-, runtime-, test- oder interaktionsspezifisch und daher nicht zwingend Kernbestandteil. |
| Kein sofortiger Umbau fuer A | alle Gaps | Der aktuelle A-Use-Case bleibt mit bestehendem Modell gueltig; die Matrix bereitet nur spaetere gezielte Anpassungen vor. |

## Risikoanalyse nach Modellqualitaet

| Qualitaetskriterium | Risiko | Gegenmassnahme |
| --- | --- | --- |
| Kompaktheit | Zu viele Klassen im Kern machen das Diagramm wieder unlesbar und schwer pruefbar. | Nur A-GAP-06 und A-GAP-08 als minimale Kernkandidaten vormerken; alle groesseren Semantiken als Module behandeln. |
| EAST-ADL-Nahe | Eventquellen, Agents oder RuntimeActions koennten mit Actors oder UseCases vermischt werden. | Actor/Agent-Trennung und keine direkte `ScenarioStep -> RuntimeAction`-Kante strikt beibehalten. |
| Rueckwaertskompatibilitaet | Neue Pflichtfelder koennten bestehende Beispielinstanzen ungueltig machen. | Alle Kernkandidaten optional oder als Praezisierung bestehender Kardinalitaet definieren. |
| Automatisierbarkeit | Ohne formale Erweiterungen bleiben manche Pruefungen textuell. | Erweiterungsmodule gezielt dort einhaengen, wo automatische Auswertung wirklich gebraucht wird. |
| B-Weiterverwendung | Eine nur fuer A getroffene Entscheidung koennte Vivian/Kaffeemaschine behindern. | Alle Entscheidungen in Task 10/11 nach B erneut bewerten. |

## Auswirkungen auf bestehende Invarianten

| Invariante | Auswirkung |
| --- | --- |
| Genau ein Main-Scenario pro UseCase | Keine Entscheidung veraendert diese Regel. |
| Include verpflichtend, Extend optional | Keine Entscheidung veraendert die EAST-ADL-nahe Use-Case-Semantik. |
| Satisfy-XOR-Regel | Keine Entscheidung veraendert die XOR-Regel. |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | A-GAP-04 bleibt als Ergaenzungsmodell unterhalb von `RuntimeBinding` und erzeugt keine direkte Schritt-zu-RuntimeAction-Kante. |
| Capability ohne technische Daten | A-GAP-04 und A-GAP-08 lassen technische Details in RuntimeBinding/RuntimeAction; Capability bleibt fachlich. |
| Actor/Agent-Trennung | A-GAP-03 und A-GAP-06 muessen diese Trennung respektieren: Eventquellen und Entity-Arten duerfen Actors nicht zu Instanzen machen. |

## Kritischer Review-Abgleich

Ein parallel eingeholter Review bestaetigte die Grundlinie, den Kern strikt kompakt zu halten. Daraus folgt gegenueber einer weicheren Auslegung: `A-GAP-04` wird nicht als Kernkandidat gefuehrt, sondern als Runtime-Orchestration-Ergaenzung. Damit bleiben fuer den Kern nur zwei minimale Kandidaten: `A-GAP-06` fuer `Entity.kind` und `A-GAP-08` fuer eine optionale Trace-Kante von `Effect` zu `StateAssertion`.

## Abnahmekontrolle

| Kriterium aus Task 5.4 | Erfuellung |
| --- | --- |
| Entscheidungsmatrix vorhanden | Die Tabelle `Entscheidungsmatrix` bewertet A-GAP-01 bis A-GAP-08. |
| Jede Luecke hat Entscheidung | Jede Gap-Zeile enthaelt `Kernanpassung`, `Ergaenzungsmodell` oder eine Kombination mit klarer Aufteilung. |
| Jede Entscheidung nennt Kriterium | Spalte `Entscheidendes Kriterium` nennt das ausschlaggebende Kriterium. |
| Jede Entscheidung nennt Risiko | Spalte `Risiko der Entscheidung` benennt das Hauptrisiko. |
| Jede Entscheidung nennt Auswirkung auf bestehendes Modell | Spalte `Auswirkung auf bestehendes Modell` beschreibt Rueckwaertskompatibilitaet und Andockpunkte. |
| Keine sofortige Metamodell-Aenderung | Die Datei bereitet Aenderungen vor, setzt sie aber nicht in Diagramm, Spezifikation oder Generator um. |

## Konsequenz fuer Task 6

Der naechste Block kann Anwendungsfall B abgrenzen. Besonders wichtig wird dort, ob A-GAP-02 `State/Transition Semantics`, A-GAP-06 `Entity.kind` und A-GAP-07 `Interaction Object/Affordance` durch Vivian und die Kaffeemaschine bestaetigt, abgeschwaecht oder veraendert werden.
