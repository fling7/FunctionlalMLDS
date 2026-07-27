# Anwendungsfall A: Indirekt oder unscharf modellierbare Elemente

Stand: 2026-07-07

Task: 5.2 `Alle Elemente markieren, die nur indirekt oder unsauber modellierbar sind`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Abgrenzung

Diese Datei beschreibt Elemente, die im aktuellen kompakten Metamodell zwar abbildbar sind, aber nur ueber Strings, Konventionen, groebere Container oder textuelle Trace-Hinweise. Das ist noch keine harte Lueckenliste. Harte nicht modellierbare Elemente folgen erst in Task 5.3.

Bewertungsskala:

- `indirekt`: Abbildung ist moeglich, aber nur ueber vorhandene generische Klassen oder Trace-Konventionen.
- `unscharf`: Abbildung ist moeglich, aber die Semantik ist fuer automatische Verarbeitung nicht eindeutig genug.
- `grenzwertig`: Abbildung funktioniert fuer das Beispiel, sollte aber in Task 5.4 fuer Kernanpassung oder Ergaenzungsmodell bewertet werden.

## Ergebnis

Die meisten unscharfen Punkte in Anwendungsfall A entstehen nicht durch fehlende Use-Case- oder Runtime-Klassen, sondern durch die bewusst kompakte Behandlung von Raum, Zustand, Rollenwechsel, Ereignisquellen, Ausfuehrungsreihenfolge und fein granularer Traceability.

| Bereich | Befund |
| --- | --- |
| Raum und Bewegung | modellierbar, aber meist als Ausdruck in `Condition.expression` oder `StateAssertion.expectedState` |
| Agentenrollen und Zustandswechsel | modellierbar, aber ohne expliziten Rollen- oder Zustandsautomaten |
| Ereignisquellen und Objektinteraktionen | modellierbar, aber Quelle, Payload und Objekt-Affordance bleiben in Strings |
| Runtime-Reihenfolge und Schemas | modellierbar, aber Reihenfolge und Schemafelder sind textuell dokumentiert |
| Feingranulare Traceability | modellierbar, aber nicht alle feinen Elemente sind direkt `satisfiedBy`-Ziele |

## Problemtabelle

| Element oder Konzept | Aktuelle Abbildung | Problem | Bewertung | Konsequenz fuer 5.3/5.4 |
| --- | --- | --- | --- | --- |
| Raeumliche Relation `inside(AgentBody, SceneBoundary)` | `Condition.expression`, `StateAssertion.expectedState` | Es gibt keine eigene Klasse fuer Raumrelation, Koordinate, Volumen, Bezugssystem oder Gueltigkeitsbereich. Die Bedeutung bleibt ein Ausdrucksstring. | unscharf | In 5.4 pruefen, ob ein optionales Spatial-Extension-Modell noetig ist. |
| Zielposition `at(AgentBody, TargetZone)` | `StateAssertion.expectedState` | Die Zielerreichung ist beobachtbar, aber nicht geometrisch oder topologisch strukturiert. Abstand, Toleranz und Zielvolumen sind nicht formalisiert. | unscharf | Kandidat fuer Spatial-Extension, nicht zwingend Kern. |
| Bewegung `movingTo(TargetZone)` | `StateAssertion.expectedState`; RuntimeAction-Trace | Bewegung ist als Zustand formulierbar, aber Trajektorie, Pfad, Dauer, Hindernisumfahrung und Bewegungsmodus fehlen. | indirekt | Fuer A ausreichend; fuer echte Laufzeitnavigation in 5.4 als Ergaenzung bewerten. |
| Hindernis-/Blockadebezug `ObstacleRegion` | `Entity`, `Condition`, `StateAssertion` | Blockade ist fachlich modellierbar, aber nicht als begehbare Flaeche, Kollisionszone, Reichweitengraph oder Pfadkostenmodell. | unscharf | Eher Spatial-/Navigationsergaenzung als Kernklasse. |
| Erreichbarkeit `TargetZone.state = reachable` | `Condition.expression` | Erreichbarkeit ist ein boolescher Ausdruck, aber die Begruendung fuer Erreichbarkeit ist nicht strukturiert. | unscharf | In 5.4 pruefen, ob Reachability als abgeleitete Condition reicht. |
| Agentenrolle `AgentBody.roleState` | `StateAssertion.expectedState`, `Condition.expression` | Rollenstatus ist konsistent normalisiert, aber Rollen selbst sind keine eigenen Elemente mit erlaubten Uebergaengen. | indirekt | Fuer A ausreichend; bei komplexen Rollenprofilen eventuell Agent-Extension. |
| Agentenaktivitaet `idle`, `waiting`, `acting`, `moving` | `StateAssertion.expectedState` | Aktivitaetszustaende sind Strings ohne expliziten Zustandsautomaten und ohne erlaubte Transitionen. | unscharf | Kandidat fuer optionales Agent-State-Modell. |
| Zustandswechsel `X -> Y` | Vorzustand als `Condition`, Zielzustand als `StateAssertion` | Der Uebergang selbst ist keine eigene Instanz; Ursache, Vorzustand, Zielzustand und Wirkung sind verteilt. | indirekt | In 5.3 pruefen, ob echte Transitionen fuer A hart fehlen oder ob die Verteilung reicht. |
| Alternative Rueckfuehrung `A-ALT-R03 -> A-MAIN-S05` | `StepRelation` mit Source/Target ueber Scenario-Grenzen | Einstieg und Rueckkehr funktionieren als StepRelation, aber das Metamodell kennt keine explizite `entryPoint`-/`returnPoint`-Semantik fuer alternative Scenarios. | grenzwertig | In 5.4 entscheiden, ob Cross-Scenario-Relations strukturiert werden sollten. |
| Exception-Einstieg `A-EX-R01` | `StepRelation.kind = exception` | Der Fehlerpfad ist modellierbar, aber Fehlerklasse, Severity, Recovery Policy und Abbruchsemantik sind nicht eigene Elemente. | indirekt | Fuer A ausreichend; fuer Safety-/Training-Szenarien evtl. Exception-Ergaenzung. |
| Ereignisquelle `SceneParticipant` in `entered(SceneParticipant, TriggerZone)` | `Event.expression` | `Event` hat keine eigene Source-/Target-/Payload-Beziehung; Quelle und Objekt stehen nur im Ausdruck. | unscharf | Kandidat fuer Event-Extension, falls automatische Auswertung wichtig wird. |
| `ExternalSignalSource` als vorbereiteter Ausloeser | `Entity`, `Event.expression` | Externe Signale sind fachlich erfassbar, aber Signaltyp, Kanal, Payload und Verbrauchsstatus sind nicht strukturiert. | indirekt | In 5.4 pruefen, ob Signalmodell noetig ist. |
| `InteractionAsset` als generisches Szenenobjekt | `Entity`, vorbereitete Events/Conditions | Interaktionsobjekt ist nur generische Entity; Affordances, Bedienpunkte, Manipulationsarten und Objekt-API fehlen. | grenzwertig | Wird fuer Anwendungsfall B wahrscheinlich wichtiger; dort separat bewerten. |
| `InstructionMarker` | `Entity`, optionales `Event` | Marker ist als Zustand/Signal modellierbar, aber Darstellung, Sichtbarkeit fuer bestimmte Rollen und Lebensdauer sind nicht formal. | unscharf | Optionales UI-/Guidance-Ergaenzungsmodell moeglich. |
| `SceneStateFlag` | `Entity` mit Zustandsstrings | Verdichtet mehrere Szenenbedingungen in einem Marker. Das ist praktisch, aber semantisch grob und kann Ursachen vermischen. | unscharf | In 5.4 pruefen, ob als abgeleiteter Zustand dokumentiert reicht. |
| `ObservationPoint` | `Entity`, `StateAssertion`, `ValidationCase` | Beobachtungspunkt ist pruefbar, aber Messmethode, Beobachterrolle, Sensor oder Validierungsinstrument sind nicht strukturiert. | indirekt | Fuer Validation ausreichend; bei Messmethoden evtl. Validation-Extension. |
| `FeedbackSignal` | `Entity`, `StateAssertion` | Rueckmeldung ist beobachtbar, aber Medium, Empfaenger, Sichtbarkeit und Inhalt sind nicht formal getrennt. | unscharf | Fuer A ausreichend; fuer B/Vivian-Dialog wahrscheinlich erneut bewerten. |
| Capability-Preconditions | `Capability.precondition` als Condition-Referenzen und Textlisten | Preconditions sind referenzierbar, aber keine formale Logik mit Auswertung, Prioritaet oder Konfliktauflosung. | indirekt | Fuer Traceability ausreichend; fuer automatische Pruefung evtl. Constraint-Sprache. |
| `Effect` zu `StateAssertion` | fachlicher Trace in Tabellen; seit v0.5 optional `Effect.evidencedBy -> StateAssertion [0..*]` | Zum Zeitpunkt von Task 5.2 war die Rueckbindung dokumentarisch. Im aktuellen Kern ist sie als optionale, nicht-kompositive Referenz modellierbar. | seit v0.5 direkt modellierbar | Keine weitere Kernkante noetig; formale ValidationOutcome-Logik bleibt ggf. Ergaenzungsmodell. |
| `Capability` zu bereitstellender Entity | `Entity -> Capability : provides` und Tabellenfeld | Die Bereitstellung ist direkt, aber Verantwortlichkeit, Version, Auswahlregel oder Prioritaet einer Capability fehlen. | unscharf | Fuer A ausreichend; bei mehreren Agenten/Plattformen pruefen. |
| RuntimeAction-Ausfuehrungsreihenfolge | Textabschnitt `Ausfuehrungsreihenfolge innerhalb der Bindings` | Das Metamodell besitzt keine Kante fuer Reihenfolge, Abhaengigkeit oder Transaktion zwischen RuntimeActions. | grenzwertig | In 5.4 entscheiden, ob RuntimeAction-Order in Kern oder Runtime-Ergaenzung gehoert. |
| RuntimeAction-Schemas `Schema.*` | `inputSchema` und `outputSchema` als Attributwerte | Schemas sind benannt und beschrieben, aber nicht als eigene strukturierte Schema-Elemente modelliert. | unscharf | Fuer Dokumentation ausreichend; fuer Codegenerierung evtl. Schema-Modell noetig. |
| RuntimeAction-Endpoint-Namen | `RuntimeAction.endpoint` | Generische Endpoints sind technisch abbildbar, aber Plattform, Protokoll, Version und Fehlerverhalten sind nicht strukturiert. | indirekt | Eher Runtime-Extension als Kern. |
| RuntimeBinding-Kontext `GenericVRSceneRuntime` | Tabellenwert `Laufzeitkontext` | Laufzeitkontext ist benannt, aber Plattformprofil, Adapter, Version und Auswahlkriterien fehlen. | unscharf | In 5.4 als RuntimeBinding-Ergaenzung bewerten. |
| ValidationCase-Stimulus | Text in ValidationCase-Tabelle | Stimulus ist pruefbar beschrieben, aber nicht als formale Sequenz von Events/Actions/Bindings modelliert. | indirekt | Fuer Dissertationstext ausreichend; fuer Testautomatisierung evtl. Test-Model-Extension. |
| ValidationCase-ExpectedOutcome | StateAssertion-Liste plus Strukturregeltext | Outcomes sind vorhanden, aber zusammengesetzte logische Erwartungen sind nicht formal maschinenlesbar. | unscharf | In 5.4 pruefen, ob Assertion-Sprache noetig ist. |
| Satisfy-Nachweisstellen auf Event/Condition/StateAssertion | Nachweisstellen in Tabellen, nicht primaer `satisfiedBy` | Feingranulare Elemente werden wegen kompakter TraceableSpecification-Struktur nicht direkt als `satisfiedBy` genutzt. | indirekt | In 5.4 pruefen, ob Event/Condition/StateAssertion traceable werden sollten. |
| Ungenutzte vorbereitete Events `A-E2`, `A-E3`, `A-E5`, `A-E6` | Event-Instanzen mit Status `ungenutzt vorbereitet` | Vorhalten ist dokumentarisch nuetzlich, aber Lebenszyklus `planned/active/unused` ist keine Metamodellsemantik. | unscharf | In 5.4 nur aufnehmen, wenn Variantenmanagement wichtig wird. |
| Entity-Typisierung `agent`, `asset`, `zone`, `signal`, `stateObject` | seit v0.5 optionales Kernattribut `Entity.kind [0..1]` | Zum Zeitpunkt von Task 5.2 war die Typisierung noch Tabellenkonvention. Im aktuellen Kern ist sie als grobe optionale Typisierung modellierbar. | seit v0.5 direkt modellierbar | Keine weitere Kernklasse noetig; feinere Objekt- oder Rollenontologien bleiben Ergaenzungsmodelle. |

## Gruppierung nach Problemtyp

| Problemtyp | Betroffene Elemente | Warum nicht direkt sauber genug? |
| --- | --- | --- |
| Fehlende Raumstruktur | `inside`, `at`, `movingTo`, `TargetZone`, `SceneBoundary`, `ObstacleRegion` | Raum wird ueber Strings und Entity-Zustaende beschrieben, nicht ueber strukturierte Relation, Position oder Geometrie. |
| Fehlende Lebenszyklus- oder Zustandsautomatensemantik | `AgentBody.roleState`, Aktivitaetszustaende, Zustandswechsel `X -> Y` | States sind modellierbar, Transitionen und erlaubte Sequenzen aber nicht eigenstaendig. |
| Fehlende Event-Struktur | `SceneParticipant`, `ExternalSignalSource`, `A-E*` | Eventquelle, Ziel, Payload und Verbrauchsstatus stehen in Expressions. |
| Fehlende Interaktionsobjektstruktur | `InteractionAsset`, `InstructionMarker` | Objektzustand ist modellierbar, Affordances und Bedienpunkte sind noch nicht formal. |
| Fehlende Runtime-Orchestrierung | RuntimeAction-Reihenfolge, RuntimeBinding-Kontext, Endpoints | Technische Aktionen existieren, aber Abhaengigkeiten, Plattformprofile und Fehlerverhalten sind textuell. |
| Fehlende formale Test-/Assertion-Sprache | ValidationCase-Stimulus und ExpectedOutcome | Tests sind nachvollziehbar, aber nicht voll formal auswertbar. |
| Feingranularer Trace nur dokumentarisch | Nachweisstellen auf Event/Condition/StateAssertion, Effect-StateAssertion-Trace | Trace ist nachvollziehbar, aber nicht jede fachliche Feinstruktur ist eigene Metamodellkante. |

## Bewertung fuer Anwendungsfall A

| Frage | Antwort |
| --- | --- |
| Kann A mit dem aktuellen Modell beschrieben werden? | ja |
| Gibt es eine Kardinalitaets- oder Invariantenverletzung? | nein |
| Sind alle fachlich zentralen Elemente mindestens modellierbar? | ja |
| Gibt es unscharfe Stellen fuer automatische Auswertung oder Codegenerierung? | ja |
| Muss deshalb der Kern sofort erweitert werden? | noch nicht entschieden; Entscheidung folgt in 5.4 |

## Abnahmekontrolle

| Kriterium aus Task 5.2 | Erfuellung |
| --- | --- |
| Tabelle `Element -> Problem` vorhanden | Die Problemtabelle enthaelt konkrete Elemente und Problemformulierungen. |
| Problem konkret benannt | Jede Zeile benennt das konkrete Unschaerfeproblem. |
| Beispiele wie fehlende Raumstruktur erfasst | Raumstruktur, Lebenszyklussemantik und Interaktionsobjektstruktur sind explizit enthalten. |
| Keine harte Lueckenentscheidung vorweggenommen | Task 5.3 bleibt fuer nicht modellierbare Elemente reserviert. |
| Keine Modellanpassung vorweggenommen | Task 5.4 bleibt fuer Kern- oder Ergaenzungsmodell-Entscheidungen reserviert. |

## Konsequenz fuer Task 5.3

Task 5.3 kann nun pruefen, ob unter den oben genannten unscharfen Punkten harte Luecken existieren. Eine harte Luecke liegt nur dann vor, wenn ein Element mit keiner vorhandenen Klasse, keinem Attribut und keiner dokumentierten Trace-Konvention sinnvoll abbildbar ist.
