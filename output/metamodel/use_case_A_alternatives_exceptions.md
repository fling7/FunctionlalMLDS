# Anwendungsfall A: Alternativen und Exceptions

Stand: 2026-07-07

Task: 2.10 `Relevante Fehler- und Alternativfaelle fuer A sammeln`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Modellierungsregel

Ein Alternativfall ist ein zulaessiger Ablaufpfad, der vom Hauptpfad abweicht, aber den Zielzustand weiterhin erreichen kann. Im Metamodell wird er spaeter als `StepRelation.kind = alternative` mit einer Guard-`Condition` modelliert.

Ein Exception-Fall ist ein Ablaufpfad, bei dem eine Pflichtbedingung verletzt wird oder eine Pflicht-Nachbedingung nicht mehr erreichbar ist. Im Metamodell wird er spaeter als `StepRelation.kind = exception` modelliert. Der Exception-Fall muss trotzdem eine fachlich erwartete Reaktion und einen beobachtbaren Abschlusszustand besitzen.

Wichtig: Weder Alternativen noch Exceptions beschreiben technische Implementierung. Es geht um ausloesende `Event`-Instanzen, pruefbare `Condition`-Ausdruecke, fachliche `ScenarioStep`-Reaktionen und erwartete `StateAssertion`-Zustaende.

## Alternativfaelle

| ID | Alternativfall | Ausloeser | Bedingung | Erwartete Reaktion | Vorlaeufige Metamodell-Abbildung | Erwarteter Abschluss |
| --- | --- | --- | --- | --- | --- | --- |
| `A-ALT1` | Externes Signal startet den Ablauf statt Betreten der Ausloesezone. | `A-E2` | `A-P5` wahr und `Event.kind = signal` | Der Agent nimmt die passende Rolle an und startet den gleichen Zielpfad wie im Hauptszenario. | `StepRelation.kind = alternative`, Guard `A-C5`; `ScenarioStep.triggeredBy -> A-E2` | `A-Q1`, `A-Q4`, `A-Q5` bleiben erreichbar. |
| `A-ALT2` | Die Zielzone ist nur temporaer blockiert. | `A-E4` | `ObstacleRegion.state = temporarilyBlocked` und `A-C6` wahr | Der Ablauf verzweigt in einen fachlichen Warte- oder Freigabeschritt und kehrt nach `ObstacleRegion.state = cleared` in den Zielpfad zurueck. | `StepRelation.kind = alternative`; Zwischenzustand `A-S9`; Guard `A-C6` | `A-O9` und danach `A-O2`, `A-O3` |
| `A-ALT3` | Ein optionales Interaktionsobjekt wird nicht benoetigt. | Kein eigenes Muss-Event; Variante aus Szenariokonfiguration | `A-P8` nicht relevant, weil kein Objekt fuer den Hauptpfad erforderlich ist | Der Agent ueberspringt objektbezogene Handlung und erreicht die Zielzone direkt. | `StepRelation.kind = alternative`; keine `CapabilityUse` fuer Objektinteraktion | `A-Q1` bis `A-Q5`, ohne `A-Q8` als Pflicht |
| `A-ALT4` | Ein Instruktionsmarker wird sichtbar und fuehrt den Agenten. | `A-E5` | `InstructionMarker.state = visible` | Der Agent bestaetigt oder nutzt die Instruktion, bevor er den Zielpfad fortsetzt. | `StepRelation.kind = alternative`; `StateAssertion.subjectRef = InstructionMarker`, `expectedState = acknowledged` | `A-O11` und danach `A-Q1` |
| `A-ALT5` | Die Zielverifikation erfolgt durch ein Systemsignal statt durch einen menschlichen Beobachter. | `A-E7` mit `Event.kind = signal` | `exists(ObservationPoint) = true` und `ObservationPoint.state` wird verifizierbar | Das System setzt den Beobachtungspunkt auf `verified`; der Abschluss bleibt beobachtbar. | `StepRelation.kind = alternative`; `Condition.kind = post`; `StateAssertion` ueber `ObservationPoint` | `A-O6`, `A-Q4` |
| `A-ALT6` | Das Zeitfenster ist knapp, aber noch gueltig. | Zeitbezogene Veraenderung im Szenario | `A-P11` wahr und `reactionTime <= allowedReactionWindow` | Der Agent fuehrt nur die fuer das Ziel notwendigen fachlichen Schritte aus und laesst optionale Marker- oder Objektvarianten aus. | `StepRelation.kind = alternative`; Guard `A-C9`; optionale Schritte werden nicht durchlaufen | `A-Q1`, `A-Q2`, `A-Q4`, `A-Q5` |

## Exception-Faelle

| ID | Exception-Fall | Ausloeser | Bedingung | Erwartete Reaktion | Vorlaeufige Metamodell-Abbildung | Erwarteter Abschluss |
| --- | --- | --- | --- | --- | --- | --- |
| `A-EX1` | Der Agent verlaesst den gueltigen Szenenbereich. | `A-E6` | `inside(AgentBody, SceneBoundary) = false` oder `SceneBoundary.state = violated` | Der Zielpfad wird verlassen; der Agent wird als ausserhalb oder verletzt markiert und eine Fehler-Rueckmeldung wird erzeugt. | `StepRelation.kind = exception`; Guard verletzt `A-C2`; `StateAssertion.subjectRef = SceneBoundary`, `expectedState = violated` | `A-Q2` nicht erfuellt; `FeedbackSignal.state = failed` |
| `A-EX2` | Der Agent wird blockiert und kann nicht sinnvoll weiter handeln. | `A-S1` oder Zustandsaenderung von `AgentBody` | `AgentBody.state = blocked` oder `AgentBody.roleState = blocked` | Der Ablauf stoppt oder wechselt in einen Korrekturschritt; Zielerreichung wird nicht als erfolgreich bestaetigt. | `StepRelation.kind = exception`; verletzt `A-P2`, `A-P12`, `A-Q3` | `AgentBody.roleState = blocked`; `FeedbackSignal.state = failed` |
| `A-EX3` | Die Zielzone ist dauerhaft nicht erreichbar. | `A-E4` | `ObstacleRegion.state = blocked` und keine Freigabebedingung `A-C6` | Der Zielpfad wird abgebrochen; das Szenario meldet, dass der Zielzustand nicht erreichbar ist. | `StepRelation.kind = exception`; Guard verletzt `A-C3`; `StateAssertion` ueber `ObstacleRegion` | `A-Q1`, `A-Q7` nicht erfuellt; `SceneStateFlag.state = requiresReaction` |
| `A-EX4` | Ein zwingend benoetigtes Interaktionsobjekt ist gesperrt oder nicht verfuegbar. | `A-E3` | `InteractionAsset.state in {locked, unavailable}` und Objekt ist Pflichtbestandteil des Pfads | Der objektbezogene Schritt wird nicht ausgefuehrt; der Ablauf wechselt in Fehlerbehandlung oder fordert eine Korrektur an. | `StepRelation.kind = exception`; verletzt `A-P8`, `A-Q8` | `InteractionAsset.state in {locked, unavailable}`; `FeedbackSignal.state = failed` |
| `A-EX5` | Das eintretende Ereignis passt nicht zu den erlaubten Ereignisarten. | Unerwartetes Event | `Event.kind not in {spatial, signal, user, environment}` | Das Ereignis wird fachlich ignoriert oder als ungueltiger Ausloeser gemeldet; kein Hauptpfadstart. | `StepRelation.kind = exception`; verletzt `A-P6`; kein gueltiges `ScenarioStep.triggeredBy` fuer Hauptpfad | `SceneStateFlag.state` bleibt `normal` oder wird `requiresReaction` |
| `A-EX6` | Der Zielzustand kann nicht beobachtbar verifiziert werden. | `A-E7` bleibt aus oder Verifikation scheitert | `ObservationPoint.state != verified` nach Zielerreichung | Der Ablauf erreicht moeglicherweise die Zielzone, darf aber nicht als erfolgreich abgeschlossen gelten. | `StepRelation.kind = exception`; verletzt `A-Q4`; `Condition.kind = post` falsch | `TargetZone.state = reached` moeglich, aber `FeedbackSignal.state != confirmed` |
| `A-EX7` | Die Ergebnisrueckmeldung bleibt aus oder scheitert. | `A-E8` bleibt aus oder `FeedbackSignal.state = failed` | `FeedbackSignal.state != confirmed` | Der fachliche Abschluss wird nicht bestaetigt; Validierung muss fehlschlagen oder wiederholt werden. | `StepRelation.kind = exception`; verletzt `A-Q5`; `StateAssertion.subjectRef = FeedbackSignal` | `FeedbackSignal.state in {notShown, failed}` |
| `A-EX8` | Das erlaubte Zeitfenster ist ueberschritten. | Zeitereignis | `reactionTime > allowedReactionWindow` | Der Ablauf wechselt in einen Timeout-Exception-Pfad; Zielerreichung wird nicht als normaler Erfolg gewertet. | `StepRelation.kind = exception`; verletzt `A-C9` beziehungsweise `A-P11`, falls Timing verpflichtend ist | `SceneStateFlag.state = requiresReaction`; optional `FeedbackSignal.state = failed` |

## Klassifikationsregel fuer spaetere ScenarioSteps

| Falltyp | Typische `StepRelation.kind` | Typische Guard | Erwarteter Zielbezug |
| --- | --- | --- | --- |
| Alternative | `alternative` | Guard ist wahr und beschreibt eine erlaubte Variante. | Ziel bleibt erreichbar; Pflicht-Postconditions bleiben erfuellbar. |
| Exception | `exception` | Guard zeigt verletzte Pflichtbedingung oder nicht erreichbare Pflicht-Postcondition. | Ziel ist nicht normal erreicht oder muss ueber Fehlerbehandlung beendet werden. |
| Rueckkehr in Hauptpfad | `sequence` nach Alternative oder `join`, falls mehrere Pfade zusammengefuehrt werden | Korrektur- oder Freigabebedingung ist wahr. | Hauptziel kann anschliessend wieder erreicht werden. |
| Wiederholung | `loop` | Wiederholungsbedingung ist fachlich begrenzt und pruefbar. | Nur zulaessig, wenn kein unendlicher Ablauf entsteht und ein beobachtbarer Endzustand definiert ist. |

## Abnahmekontrolle

| Kriterium aus Task 2.10 | Erfuellung |
| --- | --- |
| Liste von Alternativen vorhanden | `A-ALT1` bis `A-ALT6` beschreiben zulaessige Abweichungen vom Hauptpfad. |
| Liste von Exceptions vorhanden | `A-EX1` bis `A-EX8` beschreiben relevante Fehler- und Ausnahmefaelle. |
| Jeder Fall hat einen Ausloeser | Jede Tabellenzeile enthaelt ein Event, eine Variante aus der Szenariokonfiguration oder einen klaren zeit-/zustandsbezogenen Ausloeser. |
| Jeder Fall hat eine Bedingung | Jede Tabellenzeile enthaelt einen pruefbaren Guard oder eine verletzte Pflichtbedingung. |
| Jeder Fall hat eine erwartete Reaktion | Jede Tabellenzeile beschreibt eine fachliche Reaktion und einen erwarteten Abschluss. |
| Metamodellnahe Zuordnung vorhanden | Jeder Fall wird auf `StepRelation.kind`, `Event`, `Condition` oder `StateAssertion` zurueckgefuehrt. |
| Keine technische Kurzschaltung | Keine Reaktion setzt API, Topic, Engine-Befehl, Controlleraufruf oder Runtime-Log voraus. |

## Konsequenz fuer Abschnitt 3

Abschnitt 3 kann nun ein konkretes Hauptszenario ausarbeiten. Dafuer sollte der Hauptpfad zuerst ohne Alternativen modelliert werden. Danach koennen mindestens drei Falltypen als Verzweigungen ergaenzt werden:

- `A-ALT1` als erlaubter alternativer Start durch externes Signal,
- `A-ALT2` als temporaere Blockade mit Rueckkehr in den Hauptpfad,
- `A-EX1`, `A-EX3` oder `A-EX6` als klarer Exception-Pfad mit beobachtbarem Fehlerabschluss.
