# Anwendungsfall A: Endzustand und Nachbedingungen

Stand: 2026-07-07

Task: 2.9 `Endzustand und Nachbedingungen sammeln`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Modellierungsregel

Der Endzustand beschreibt beobachtbare Zielwerte nach erfolgreichem Abschluss des Hauptszenarios. Er ist primaer als `StateAssertion.subjectRef + StateAssertion.expectedState` formulierbar.

Eine Nachbedingung beschreibt eine pruefbare Aussage, die nach dem Hauptszenario gelten muss. Sie kann als `StateAssertion` formuliert werden; zusammengesetzte Aussagen werden zusaetzlich als `Condition.kind = post` notiert, muessen aber auf einzelne StateAssertions zerlegbar bleiben.

Nicht aufgenommen werden technische Abschlussdetails wie API-Antworten, Engine-Callbacks, Topic-Acknowledgements oder konkrete Runtime-Logs. Solche Details gehoeren spaeter nur in `RuntimeBinding` und `RuntimeAction`.

## Endzustand des erfolgreichen Hauptszenarios

| ID | Endzustand | Betroffenes Subjekt | Vorlaeufige Metamodell-Abbildung | Pruefbare Aussage |
| --- | --- | --- | --- | --- |
| `A-O1` | Der Agent befindet sich weiterhin im gueltigen Szenenbereich. | `AgentBody`, `SceneBoundary` | `StateAssertion` plus `Condition.kind = post` | `inside(AgentBody, SceneBoundary) = true` |
| `A-O2` | Der Agent hat die Zielzone erreicht. | `AgentBody`, `TargetZone` | `StateAssertion.subjectRef = AgentBody` | `at(AgentBody, TargetZone) = true` |
| `A-O3` | Die Zielzone ist als erreicht markiert. | `TargetZone` | `StateAssertion.subjectRef = TargetZone` | `TargetZone.state = reached` |
| `A-O4` | Die Agentenrolle ist passend abgeschlossen oder bleibt ausfuehrend. | `AgentBody.roleState` | `StateAssertion.subjectRef = AgentBody` | `roleState in {executor, completed}` |
| `A-O5` | Der Agent ist nicht blockiert. | `AgentBody`, `AgentBody.roleState` | `StateAssertion.subjectRef = AgentBody` | `AgentBody.state != blocked and AgentBody.roleState != blocked` |
| `A-O6` | Der relevante Beobachtungspunkt wurde verifiziert. | `ObservationPoint` | `StateAssertion.subjectRef = ObservationPoint` | `ObservationPoint.state = verified` |
| `A-O7` | Die Ergebnisrueckmeldung wurde angezeigt und bestaetigt. | `FeedbackSignal` | `StateAssertion.subjectRef = FeedbackSignal` | `FeedbackSignal.state = confirmed` |
| `A-O8` | Das ausloesende externe Signal ist verbraucht, falls es verwendet wurde. | `ExternalSignalSource` | `StateAssertion.subjectRef = ExternalSignalSource` | `ExternalSignalSource.state = signalConsumed` |
| `A-O9` | Eine im Hauptpfad relevante Blockade ist nicht mehr offen. | `ObstacleRegion` | `StateAssertion.subjectRef = ObstacleRegion` | `ObstacleRegion.state in {clear, cleared}` |
| `A-O10` | Ein optional verwendetes Interaktionsobjekt ist in einem fachlich konsistenten Abschlusszustand. | `InteractionAsset` | `StateAssertion.subjectRef = InteractionAsset` | `InteractionAsset.state in {used, active, available}` |
| `A-O11` | Eine ausgegebene Instruktion ist nicht mehr unbearbeitet. | `InstructionMarker` | `StateAssertion.subjectRef = InstructionMarker` | `InstructionMarker.state in {acknowledged, expired, hidden}` |
| `A-O12` | Die Szene fordert keine weitere unmittelbare Agentenreaktion. | `SceneStateFlag` | `StateAssertion.subjectRef = SceneStateFlag` | `SceneStateFlag.state in {normal, resolved}` |

## Nachbedingungen

| ID | Nachbedingung | Art | Betroffene Elemente | Als `StateAssertion` formulierbar durch | Pruefbare Aussage |
| --- | --- | --- | --- | --- | --- |
| `A-Q1` | Der Hauptzielzustand ist erreicht. | fachlich | `AgentBody`, `TargetZone` | `A-O2`, `A-O3` | `at(AgentBody, TargetZone) = true and TargetZone.state = reached` |
| `A-Q2` | Der erfolgreiche Ablauf bleibt innerhalb der Szenengrenze. | raeumlich | `AgentBody`, `SceneBoundary` | `A-O1` | `inside(AgentBody, SceneBoundary) = true` |
| `A-Q3` | Der Agent ist nach Abschluss nicht in einem Fehlerzustand. | fachlich | `AgentBody`, `AgentBody.roleState` | `A-O4`, `A-O5` | `AgentBody.state != blocked and AgentBody.roleState in {executor, completed}` |
| `A-Q4` | Der Zielzustand wurde beobachtbar verifiziert. | validierungsbezogen | `ObservationPoint` | `A-O6` | `ObservationPoint.state = verified` |
| `A-Q5` | Der Abschluss ist fuer Beobachter oder System rueckgemeldet. | validierungsbezogen | `FeedbackSignal` | `A-O7` | `FeedbackSignal.state = confirmed` |
| `A-Q6` | Kein fuer den Erfolg relevanter Ausloeser bleibt unverarbeitet. | ausloeserbezogen | `TriggerZone`, `ExternalSignalSource` | `A-O8` oder zusaetzliche `StateAssertion` ueber `TriggerZone` | `ExternalSignalSource.state = signalConsumed or TriggerZone.state in {entered, left}` |
| `A-Q7` | Keine erfolgreiche Hauptpfad-Blockade bleibt offen. | fachlich/raeumlich | `ObstacleRegion` | `A-O9` | `ObstacleRegion.state in {clear, cleared}` |
| `A-Q8` | Optional genutzte Interaktionsobjekte stehen in keinem widerspruechlichen Zustand. | fachlich | `InteractionAsset` | `A-O10` | `InteractionAsset.state not in {locked, unavailable}` |
| `A-Q9` | Optional verwendete Instruktionsmarker wurden verarbeitet oder sind nicht mehr sichtbar. | fachlich | `InstructionMarker` | `A-O11` | `InstructionMarker.state in {acknowledged, expired, hidden}` |
| `A-Q10` | Die Szene fordert nach erfolgreichem Abschluss keine weitere unmittelbare Reaktion. | fachlich | `SceneStateFlag` | `A-O12` | `SceneStateFlag.state in {normal, resolved}` |
| `A-Q11` | Die Nachbedingungen verletzen keine Pflicht-Vorbedingung, die waehrend des Erfolgsablaufs erhalten bleiben muss. | konsistenzbezogen | `AgentBody`, `SceneBoundary`, `AgentBody.roleState` | `A-O1`, `A-O5` | `inside(AgentBody, SceneBoundary) = true and AgentBody.roleState != blocked` |

## Pflicht- und optionale Nachbedingungen

| Kategorie | Nachbedingungen | Begruendung |
| --- | --- | --- |
| Pflicht fuer erfolgreichen Hauptpfad | `A-Q1`, `A-Q2`, `A-Q3`, `A-Q4`, `A-Q5`, `A-Q11` | Diese Aussagen sind direkt aus `Scenario.goal` und `A-G5` bis `A-G7` ableitbar. |
| Pflicht, falls jeweiliger Ausloeser oder Gegenstand verwendet wurde | `A-Q6`, `A-Q7`, `A-Q8`, `A-Q9`, `A-Q10` | Diese Aussagen haengen davon ab, ob Signalquelle, Hindernis, Interaktionsobjekt, Instruktionsmarker oder Szenenflag im konkreten Szenario vorkommen. |

## Rueckbindung an Zielaussagen und Vorbedingungen

| Bezug | Abgesicherte Nachbedingungen |
| --- | --- |
| `A-G5` Agent erreicht Zielzone | `A-Q1`, `A-O2`, `A-O3` |
| `A-G6` Beobachtungspunkt wurde verifiziert | `A-Q4`, `A-O6` |
| `A-G7` Rueckmeldung wurde bestaetigt | `A-Q5`, `A-O7` |
| `A-P3` Agent bleibt im erlaubten Szenenbereich | `A-Q2`, `A-Q11`, `A-O1` |
| `A-P4` Zielzone war erreichbar | `A-Q7`, `A-O9` |
| `A-P7` Szenario begann nicht abgeschlossen | `A-Q1`, `A-Q5` zeigen den erfolgreichen Zustandswechsel. |
| `A-P10` Zielzustand ist beobachtbar | `A-Q4`, `A-Q5` |
| `A-P12` keine Exception zu Beginn | `A-Q2`, `A-Q3`, `A-Q11` stellen sicher, dass der Erfolgspfad nicht in einer Exception endet. |

## Abnahmekontrolle

| Kriterium aus Task 2.9 | Erfuellung |
| --- | --- |
| Liste von Postconditions vorhanden | `A-Q1` bis `A-Q11` bilden die Nachbedingungsliste. |
| Jede Nachbedingung ist als `StateAssertion` formulierbar | Jede Nachbedingung verweist auf eine oder mehrere Endzustandsaussagen `A-O1` bis `A-O12`. |
| Endzustand erfasst | `A-O1` bis `A-O12` beschreiben beobachtbare Abschlusszustaende. |
| Pruefbarkeit gegeben | Jede Zeile enthaelt eine konkrete pruefbare Aussage. |
| Pflicht und Option getrennt | Pflichtnachbedingungen und gegenstandsabhaengige Nachbedingungen sind getrennt. |
| Konsistenz zu Vorbedingungen geprueft | Rueckbindung zeigt, welche Start- und Pflichtbedingungen im erfolgreichen Abschluss erhalten bleiben oder erfolgreich veraendert werden. |
| Keine technische Kurzschaltung | API-Antworten, Engine-Callbacks, Topic-Acknowledgements und Runtime-Logs sind ausgeschlossen. |

## Konsequenz fuer Task 2.10

Task 2.10 kann aus den nicht erfuellten Postconditions Alternativen und Exceptions ableiten. Besonders relevante Fehler- oder Alternativfaelle sind:

- `A-Q2` verletzt: Agent verlaesst gueltigen Szenenbereich,
- `A-Q3` verletzt: Agent endet blockiert,
- `A-Q4` verletzt: Zielzustand kann nicht verifiziert werden,
- `A-Q5` verletzt: Ergebnisrueckmeldung bleibt aus,
- `A-Q7` verletzt: Blockade bleibt offen,
- `A-Q8` verletzt: Interaktionsobjekt ist gesperrt oder nicht verfuegbar.
