# Entscheidung 10.7: Brauchen Interaktionsobjekte eigene Affordances?

Stand: 2026-07-07

Task: 10.7 `Pruefen, ob Interaktionsobjekte eigene Affordances brauchen`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `differences_A_B.md`
- `entity_agent_scene_object_decision.md`
- `state_assertion_object_state_decision.md`
- `capability_runtime_vivian_action_decision.md`
- `spatial_relationship_decision.md`
- `use_case_A_indirect_modelability.md`
- `use_case_A_gap_decision_matrix.md`
- `use_case_B_direct_modelability.md`
- `use_case_B_indirect_modelability.md`
- `use_case_B_gap_decision_matrix.md`
- `use_case_B_events.md`
- `use_case_B_capability_instances.md`

## Entscheidung

Interaktionsobjekte brauchen fuer den aktuellen kompakten Kern keine eigene Kernklasse `Affordance`.

Interaktionsobjekte brauchen aber ein optionales `InteractionObjectModule` mit eigener Affordance-Semantik, sobald Bedienpunkte, erlaubte Manipulationen, Aktivierungsbedingungen, Bedienbereiche, Eingabeobjekte oder sichtbares Feedback maschinenlesbar generiert, validiert oder in einer Runtime eindeutig angebunden werden sollen.

Damit lautet die Entscheidung:

| Frage | Entscheidung |
| --- | --- |
| Muss der Kern um `Affordance` erweitert werden? | nein |
| Reicht `Entity` fuer die Identitaet interaktiver Objekte? | ja |
| Reicht `Capability` fuer die fachliche Faehigkeit eines Objekts? | ja |
| Reicht `Capability` allein fuer Bedienbarkeit von Starttaste, Tassenbereich oder Programmauswahl? | nein |
| Braucht Anwendungsfall B bei praeziser Bedienmodellierung Affordances? | ja |
| Braucht Anwendungsfall A in der Baseline Affordances? | nein, nur optional bei echten Interaktionsobjektvarianten |
| Empfohlene Behandlung | optionales `InteractionObjectModule`, angebunden an `Entity`, `Event`, `Condition`, `StateAssertion`, `Capability` und bei Bedarf `SpatialSemanticsModule` |

Die Kernlinie bleibt:

`ScenarioStep -> Event/Condition/StateAssertion -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

Affordances duerfen diese Kette nicht ersetzen. Sie beschreiben die objektseitige Bedienmoeglichkeit, nicht die technische Ausfuehrung.

## Begriffsabgrenzung

| Konzept | Aufgabe | Beispiel in B | Nicht verwechseln mit |
| --- | --- | --- | --- |
| `Entity` | Identifiziert ein fachlich relevantes Ding. | `ENT-B-02 CoffeeMachine`, `ENT-B-03 Cup` | Nicht jede Entity ist automatisch bedienbar. |
| `Capability` | Beschreibt, was eine Entity fachlich leisten kann. | `CAP-B-START-BREWING`, `CAP-B-CHECK-MACHINE-READY` | Beschreibt nicht automatisch Taste, Bedienart oder Bedienzone. |
| `Affordance` | Beschreibt, wie ein Actor ein Objekt oder Objektteil fachlich bedienen kann. | Starttaste druecken, Tasse platzieren, Programm auswaehlen | Keine technische API und keine RuntimeAction. |
| `ControlSurface` | Beschreibt den konkreten bedienbaren Objektteil. | `CoffeeMachine.startButton`, `CoffeeMachine.programSelector` | Keine Capability; sie ist ein Bedienpunkt. |
| `InteractionZone` | Beschreibt den raeumlichen oder logischen Bedienbereich. | `CoffeeMachine.cupArea` | Keine vollstaendige Spatial Semantics, sondern Andockpunkt dafuer. |
| `Event` | Beschreibt ein eintretendes Ereignis. | `pressed(Visitor, CoffeeMachine.startButton)` | Nicht die dauerhafte Bedienmoeglichkeit selbst. |
| `Condition` | Beschreibt eine Bedingung oder einen Guard. | `CoffeeMachine.selectedProgram = coffee` | Nicht die Objektbedienung selbst. |
| `StateAssertion` | Beschreibt einen erwarteten beobachtbaren Zustand. | `CoffeeMachine.cupPresent = true` | Nicht die erlaubte Manipulation. |
| `RuntimeAction` | Beschreibt eine konkrete technische Ausfuehrung. | `B-RA-CM-REQUEST-BREWING-START` | Nicht in `Affordance` oder `Capability` hineinziehen. |

Eine `Capability` beantwortet also: "Was kann das Objekt fachlich leisten?"

Eine `Affordance` beantwortet: "Welche fachlich zulaessige Bedienhandlung bietet das Objekt einem Actor an, unter welchen Bedingungen und mit welchem beobachtbaren Effekt?"

## Warum `Capability` allein nicht ausreicht

`Capability` ist fuer die fachliche Faehigkeit notwendig, aber nicht ausreichend fuer praezise Interaktionsobjekte.

| Fehlender Aspekt in `Capability` | Warum relevant | Beispiel |
| --- | --- | --- |
| Bedienbarer Objektteil | Der Generator muss wissen, woran der Actor handelt. | Starttaste, Tassenbereich, Programmauswahlfeld |
| Manipulationsart | Druecken, Platzieren, Auswaehlen, Bestaetigen und Beobachten sind unterschiedliche Bedienhandlungen. | `press`, `place`, `select`, `confirm`, `observe` |
| Aktivierungsbedingung | Eine Bedienmoeglichkeit kann sichtbar, aber deaktiviert sein. | Starttaste nur nach Programmauswahl sinnvoll |
| Actor-Berechtigung | Nicht jede Rolle darf jede Bedienung ausfuehren. | `Visitor` darf bestaetigen; System startet fachlich erst danach |
| Eingabeobjekt | Manche Affordances erfordern ein anderes Objekt. | Tasse wird in den Tassenbereich gestellt |
| Bedienbereich | Bedienbarkeit kann an Ort, Reichweite, Sichtbarkeit oder Zone gebunden sein. | `CoffeeMachine.cupArea`, `near(Visitor, startButton)` |
| Feedbackkanal | Eine Interaktion erzeugt sichtbare oder hoerbare Rueckmeldung. | Startfeedback, Ready-Anzeige, Programmauswahlbestaetigung |
| Event-Abbildung | Die Bedienhandlung muss ein fachliches Event ausloesen. | `B-E07 StarttasteBetaetigt` |
| Ergebniszustand | Die Bedienhandlung soll zu einem pruefbaren Zustand fuehren. | `SA-B-CM-CUP-PRESENT` |
| Verbotene Bedienung | Eine falsche oder zu fruehe Manipulation muss blockierbar sein. | Start vor Tasse/Programm/Bestaetigung |

Beispiel: `CAP-B-START-BREWING` sagt korrekt, dass die Kaffeemaschine den Bruehvorgang fachlich starten kann. Diese Capability sagt aber nicht, dass der Visitor vorher eine Starttaste drueckt, dass diese Taste ein konkreter Objektteil ist, dass sie nach einer Programmauswahl bedienbar ist, dass die Handlung das Event `B-E07` erzeugt oder dass eine sichtbare Rueckmeldung erwartet wird.

Darum darf `Capability` nicht zur Sammelklasse fuer Bedienpunkte gemacht werden. Sonst vermischt das Modell fachliche Objektfaehigkeit, Benutzerbedienung, Zustand, Raum und technische Ausfuehrung.

## Bewertung fuer Anwendungsfall B

Anwendungsfall B ist der starke Treiber fuer Affordance-Semantik. Die Kaffeemaschine ist nicht nur ein Zustandstraeger, sondern ein bedienbares Interaktionsobjekt.

| B-Sachverhalt | Aktuelle Baseline-Abbildung | Reicht fuer Baseline? | Wann Affordance noetig wird |
| --- | --- | --- | --- |
| Tasse platzieren | `B-E03 placed(Visitor, Cup, CoffeeMachine.cupArea)`; danach `B-E04` und `SA-B-CM-CUP-PRESENT` | ja | Wenn `cupArea`, Pose, Erlaubnis, Toleranz oder Sensorbereich strukturiert sein muessen. |
| Programm auswaehlen | `B-E05 selectedProgram(Visitor, CoffeeMachine, coffee)`; danach `B-E06` | ja | Wenn Auswahloptionen, Control Surface, Anzeigezustand oder gueltige Werte modelliert werden muessen. |
| Starttaste betaetigen | `B-E07 pressed(Visitor, CoffeeMachine.startButton)`; danach `B-E08` | ja | Wenn die Taste als bedienbarer Objektteil mit Aktivierung, Reichweite und Feedback generiert oder validiert wird. |
| Start bestaetigen | `B-E10 confirmationRequested(...)`, `B-E11 confirmed(...)`; Vivian-Capability und RuntimeAction zeigen eine Bestaetigungsmoeglichkeit | ja | Wenn Antwortoptionen, Timeout, Widerruf, UI-Affordance oder Autorisierung formal werden. |
| Fortschritt beobachten | `B-E14 progressChanged(...)`, `B-E16 shown(CoffeeMachine.completionFeedback)` | ja | Wenn sichtbares Feedback als wahrnehmbare Objektfunktion oder Display-Affordance modelliert wird. |

Fuer die aktuelle Baseline reicht es, diese Sachverhalte in `Event.expression`, `Condition.expression` und `StateAssertion.expectedState` qualitativ zu beschreiben.

Fuer eine doktorarbeitstaugliche, generierbare Interaktionsobjektmodellierung sollte B jedoch ein optionales Affordance-Modul erhalten, weil sonst die Bedienbarkeit der Kaffeemaschine nur als Textausdruck in Events und RuntimeSchemas existiert.

## Beispiel B: Starttaste

Kompakte Kernabbildung:

| Ebene | Instanz |
| --- | --- |
| Actor | `ACT-B-01 Visitor` |
| Entity | `ENT-B-02 CoffeeMachine` |
| Event | `B-E07 StarttasteBetaetigt`, `pressed(Visitor, CoffeeMachine.startButton)` |
| ScenarioStep | `B-MAIN-S09`, `actorIntent` |
| Folgeschritt | `B-MAIN-S10`, Vivian bestaetigt die Bruehanforderung |
| Capability | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST`, spaeter `CAP-B-CHECK-MACHINE-READY` und `CAP-B-START-BREWING` |
| StateAssertions | `SA-B-BREWING-REQUESTED`, spaeter Startpermission und Brewing-Zustand |

Optionale Affordance-Abbildung:

| Modulinstanz | Inhalt |
| --- | --- |
| `InteractionObject` | `IO-B-COFFEE-MACHINE`, referenziert `ENT-B-02 CoffeeMachine` |
| `ControlSurface` | `CS-B-START-BUTTON`, Teil von `IO-B-COFFEE-MACHINE` |
| `Affordance` | `AFF-B-PRESS-START-BUTTON` |
| `manipulationKind` | `press` |
| `offeredTo` | `ACT-B-01 Visitor` |
| `activationCondition` | Programm gewaehlt, Tasse erkannt, keine aktive Sperre |
| `producesEvent` | `B-E07` |
| `resultingState` | `SA-B-BREWING-REQUESTED` |
| `enablesCapability` | `CAP-B-CHECK-MACHINE-READY`; indirekt spaeter `CAP-B-START-BREWING` |
| `feedback` | Bruehanforderung erkannt oder Start blockiert |

Wichtig: Die Affordance startet den Bruehvorgang nicht direkt. Sie erzeugt eine fachlich beobachtbare Benutzerhandlung. Der eigentliche Start bleibt ueber `CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction` modelliert.

## Beispiel B: Tassenbereich

Kompakte Kernabbildung:

| Ebene | Instanz |
| --- | --- |
| Actor | `ACT-B-01 Visitor` |
| Entity | `ENT-B-03 Cup`, `ENT-B-02 CoffeeMachine` |
| Event | `B-E03 TassePlatziert`, `placed(Visitor, Cup, CoffeeMachine.cupArea)` |
| Folgestatus | `B-E04 TasseErkannt`, `SA-B-CM-CUP-PRESENT` |
| Vivian-Capability | `CAP-B-VIVIAN-GUIDE-CUP` |
| Alternativpfad | `B-ALT-S01` bis `B-ALT-S04`, falls Tasse fehlt oder nicht erkannt wird |

Optionale Affordance-Abbildung:

| Modulinstanz | Inhalt |
| --- | --- |
| `InteractionZone` | `IZ-B-CUP-AREA`, referenziert `CoffeeMachine.cupArea` |
| `Affordance` | `AFF-B-PLACE-CUP` |
| `manipulationKind` | `place` |
| `inputObjectConstraint` | `ENT-B-03 Cup` muss platzierbar und geeignet sein |
| `activationCondition` | Vivian im Fuehrungsmodus oder Tassenplatzierung fachlich erwartet |
| `producesEvent` | `B-E03` |
| `resultingState` | `SA-B-CM-CUP-PRESENT`, falls Erkennung positiv |
| `failureState` | Tasse fehlt oder nicht erkannt, Einstieg in Alternativpfad |
| `spatialAnchor` | optional `SpatialRegion` fuer Lage, Toleranz und Erreichbarkeit |

Hier zeigt sich die Grenze besonders klar: `CAP-B-VIVIAN-GUIDE-CUP` beschreibt Vivians Anleitung. Die Affordance `AFF-B-PLACE-CUP` beschreibt die objektseitige Moeglichkeit, eine Tasse in einen bestimmten Bereich zu stellen. Beides darf nicht zusammenfallen.

## Beispiel B: Programmauswahl

Kompakte Kernabbildung:

| Ebene | Instanz |
| --- | --- |
| Event | `B-E05 ProgrammGewaehlt`, `selectedProgram(Visitor, CoffeeMachine, coffee)` |
| Environment Event | `B-E06 ProgrammauswahlBestaetigt` |
| StateAssertion | `CoffeeMachine.selectedProgram = coffee` |
| Vivian-Capability | `CAP-B-VIVIAN-GUIDE-PROGRAM` |

Optionale Affordance-Abbildung:

| Modulinstanz | Inhalt |
| --- | --- |
| `ControlSurface` | `CS-B-PROGRAM-SELECTOR` |
| `Affordance` | `AFF-B-SELECT-COFFEE-PROGRAM` |
| `manipulationKind` | `select` |
| `allowedValue` | `coffee`, optional weitere Programme |
| `activationCondition` | Tasse erkannt und Vivian fuehrt zur Programmauswahl |
| `producesEvent` | `B-E05` |
| `resultingState` | Programmauswahl bestaetigt, `B-E06` |
| `feedback` | Auswahl sichtbar oder bestaetigt |

Auch hier gilt: Die Affordance ist nicht die fachliche Maschinenfaehigkeit. Sie ist die strukturierte Bedienmoeglichkeit, durch die der Visitor einen zulaessigen Wert setzt.

## Bewertung fuer Anwendungsfall A

Anwendungsfall A benoetigt Affordances in der Baseline nicht als eigene Struktur. Der Schwerpunkt liegt auf dynamischem Agentenverhalten, Rollenwechsel, Zielerreichung, Hindernisbehandlung und Beobachtbarkeit.

| A-Sachverhalt | Aktuelle Baseline-Abbildung | Reicht fuer Baseline? | Wann Affordance noetig wird |
| --- | --- | --- | --- |
| TriggerZone betreten | `Event.expression = entered(SceneParticipant, TriggerZone)` | ja | Wenn die Zone als interaktive Eintrittsmoeglichkeit mit Sensorik und Feedback generiert wird. |
| Optionales `InteractionAsset` | `Entity` plus Conditions wie `InteractionAsset.state != locked` | ja | Wenn das Objekt konkrete Bedienpunkte, Manipulationsarten oder Freischaltregeln besitzt. |
| `InstructionMarker` | `Entity` und `StateAssertion` | ja | Wenn der Marker bestaetigt, angeklickt oder als Interaktionsflaeche genutzt wird. |
| `FeedbackSignal` | `StateAssertion` und ValidationCase | ja | Wenn das Feedback selbst bedienbar oder quittierbar wird. |

Fuer A reicht also `Entity` plus `Condition`, `Event`, `StateAssertion` und `Capability`, solange Interaktionsobjekte nur Kontext sind. Wenn A spaeter echte bedienbare Objekte enthaelt, kann dasselbe optionale Modul wiederverwendet werden.

## Vorgeschlagener Andockpunkt fuer ein optionales Modul

Ein optionales `InteractionObjectModule` sollte die vorhandenen Kernklassen referenzieren und nicht in den Kern hineinwachsen.

| Modulkonzept | Kardinalitaet/Andockpunkt | Zweck |
| --- | --- | --- |
| `InteractionObject` | referenziert genau eine `Entity [1]` | Markiert eine Entity als bedienbares Objekt, ohne `Entity` zu ueberladen. |
| `ControlSurface` | gehoert zu `InteractionObject [1]`, `InteractionObject -> ControlSurface [0..*]` | Beschreibt Taste, Regler, Display, Selector oder Objektteil. |
| `InteractionZone` | gehoert zu `InteractionObject [0..*]`, optional `SpatialRegion [0..1]` | Beschreibt Bereich, Flaeche oder Zone einer Bedienung. |
| `Affordance` | gehoert zu `InteractionObject [1]`, `InteractionObject -> Affordance [1..*]` | Beschreibt eine fachlich zulaessige Bedienmoeglichkeit. |
| `Affordance.controlSurface` | `0..1` | Eine Affordance kann an einen konkreten Bedienpunkt gebunden sein. |
| `Affordance.interactionZone` | `0..1` | Eine Affordance kann an einen Bereich gebunden sein. |
| `Affordance.offeredTo` | `0..* Actor` | Beschreibt, fuer welche Rollen die Bedienmoeglichkeit gilt. |
| `Affordance.activationCondition` | `0..* Condition` | Beschreibt, wann die Bedienmoeglichkeit aktiv ist. |
| `Affordance.producesEvent` | `1..* Event` | Jede Affordance muss mindestens ein fachliches Bedienereignis erzeugen. |
| `Affordance.resultingState` | `0..* StateAssertion` | Optional erwartete Objekt- oder Szenenzustaende nach der Bedienung. |
| `Affordance.enablesCapability` | `0..* Capability` | Eine Bedienmoeglichkeit kann eine spaetere fachliche Faehigkeitsnutzung vorbereiten. |
| `Affordance.feedback` | `0..* StateAssertion` oder optionales Feedback-Konzept | Beschreibt wahrnehmbare Rueckmeldung. |
| `InputObjectConstraint` | `0..*` an `Affordance` | Beschreibt Objekte, die bei der Bedienung beteiligt sein muessen. |

Bewusste Nicht-Kante:

`Affordance -> RuntimeAction`

Diese direkte Kante sollte verboten bleiben. Eine Affordance erzeugt fachliche Events und Zustaende. Technische Ausfuehrung bleibt ueber `Capability`, `RuntimeBinding` und `RuntimeAction` getrennt.

## Minimales Modul ohne Aufblaehen

Falls das Modul spaeter tatsaechlich ins Diagramm aufgenommen wird, reicht fuer eine kompakte Version:

| Minimaler Baustein | Warum ausreichend |
| --- | --- |
| `InteractionObject` | Verbindet bedienbares Objekt mit `Entity`. |
| `Affordance` | Beschreibt Bedienmoeglichkeit mit Manipulationsart und fachlicher Wirkung. |
| `InteractionTarget` | Fasst `ControlSurface` und `InteractionZone` zusammen, damit das Diagramm klein bleibt. |
| `InputObjectConstraint` | Nur noetig, wenn ein zweites Objekt wie `Cup` beteiligt ist. |

Kompakte Struktur:

`Entity <- InteractionObject -> Affordance -> Event`

Optional:

`Affordance -> Condition`, `Affordance -> StateAssertion`, `Affordance -> Capability`, `Affordance -> InteractionTarget`

Damit bleibt das Hauptmetamodell klein. Die Details zu Bedienpunkten, Zonen und Eingabeobjekten koennen im Modul liegen.

## Invariantencheck

| Regel | Ergebnis |
| --- | --- |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | eingehalten |
| Keine direkte `Affordance -> RuntimeAction`-Kante | als Modulregel empfohlen |
| `Capability` bleibt technische-datenfrei | eingehalten; Affordance enthaelt keine Endpoint-, Topic- oder Tool-Daten |
| `Entity` wird nicht mit Bedienpunktdetails ueberladen | eingehalten; Affordance bleibt optionales Modul |
| Actor/Agent-Trennung bleibt erhalten | eingehalten; `Visitor` bedient, Vivian assistiert, CoffeeMachine stellt Faehigkeiten bereit |
| Spatial Semantics wird nicht in Affordance versteckt | eingehalten; `InteractionZone` kann optional an `SpatialRegion` andocken |
| Runtime-nahe UI-Erzeugung bleibt RuntimeAction | eingehalten; z. B. `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` bleibt technische Praesentation |

## Abnahmekontrolle

| Kriterium aus Task 10.7 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | Affordances nicht im Kern, aber optionales Modul fuer praezise Interaktionsobjekte. |
| `Capability` allein bewertet | `Capability` reicht fuer fachliche Faehigkeiten, nicht fuer konkrete Bedienbarkeit. |
| Begruendung fuer Nicht-Ausreichen vorhanden | Abschnitt `Warum Capability allein nicht ausreicht` listet die fehlenden Semantiken. |
| B-Beispiele verwendet | Starttaste, Tassenbereich, Programmauswahl, Startbestaetigung und Fortschritt. |
| A-Beispiele bewertet | TriggerZone, InteractionAsset, InstructionMarker und FeedbackSignal. |
| Kompakte Modelloption formuliert | Minimales Modul mit `InteractionObject`, `Affordance`, `InteractionTarget`, optional `InputObjectConstraint`. |
| Keine Kernaufblaehung abgeleitet | Kern bleibt unveraendert; Modul ist optional und andockbar. |

## Konsequenz fuer Task 10.8

Task 10.8 soll als naechstes pruefen, ob Agenten eigene Ziele, Rollenwechsel oder Laufzeitprofile brauchen. Die Entscheidung aus 10.7 haelt dafuer fest: Objektseitige Bedienmoeglichkeiten gehoeren nicht in `Agent` oder `Capability`. Ein Agent kann Affordances nutzen oder durch Vivian zu ihnen fuehren, aber die Affordance selbst ist eine Eigenschaft des Interaktionsobjekts.
