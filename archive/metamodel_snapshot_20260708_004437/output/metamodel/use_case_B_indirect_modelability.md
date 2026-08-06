# Anwendungsfall B: Indirekt oder unscharf modellierbare Elemente

Stand: 2026-07-07

Task: 9.2 `Unscharf modellierbare B-Elemente markieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Abgrenzung

Diese Datei beschreibt Elemente, die im aktuellen kompakten Metamodell zwar abbildbar sind, aber nur ueber Strings, Konventionen, groebere Container oder textuelle Trace-Hinweise. Das ist noch keine harte Lueckenliste. Harte nicht modellierbare Elemente folgen erst in Task 9.3.

Bewertungsskala:

- `indirekt`: Abbildung ist moeglich, aber nur ueber vorhandene generische Klassen oder Trace-Konventionen.
- `unscharf`: Abbildung ist moeglich, aber die Semantik ist fuer automatische Verarbeitung nicht eindeutig genug.
- `grenzwertig`: Abbildung funktioniert fuer das Beispiel, sollte aber in Task 9.4 fuer Kernanpassung oder Ergaenzungsmodell bewertet werden.

## Ergebnis

Die meisten unscharfen Punkte in Anwendungsfall B entstehen nicht durch fehlende Use-Case- oder Runtime-Klassen. Sie entstehen durch die bewusst kompakte Behandlung von Vivian als Agent, Kaffeemaschine als generische Entity, Objektzustand als String-basierte StateAssertion, Event-/Condition-Ausdruecken, Runtime-Kontexten und textueller Traceability.

| Bereich | Befund |
| --- | --- |
| Vivian-spezifische Assistenzlogik | modellierbar, aber Dialogzustand, Inhalt, Intention, Erklaerstrategie und Modalitaet bleiben grob |
| Interaktionsobjekt Kaffeemaschine | modellierbar, aber Affordances, Bedienpunkte und interne Zustandsautomaten sind nicht strukturiert |
| Kontextobjekte und Requests | modellierbar, aber Cup und BrewingRequest sind nur minimal als Entity-/StateAssertion-Subjekte eingefuehrt |
| Events und Conditions | modellierbar, aber Quelle, Ziel, Payload und Auswertungslogik stehen in Expressions |
| Runtime und Schemas | modellierbar, aber Plattformprofil, Reihenfolge, Fehlerverhalten und Schema-Struktur sind textuell |
| Validierung und Traceability | modellierbar, aber einige Nachweise bleiben dokumentarisch statt als eigene Metamodellkanten |

## Vivian-spezifische Problemtabelle

| Element oder Konzept | Aktuelle Abbildung | Problem | Bewertung | Konsequenz fuer 9.3/9.4 |
| --- | --- | --- | --- | --- |
| Vivian als `Agent` statt `Actor` | `ENT-B-01 VivianAssistant` als `Agent` und `Entity`; keine Actor-Rolle in der Baseline | Die Entscheidung ist korrekt fuer die aktuelle Systemgrenze, aber systemgrenzensensitiv. Bei engerer Betrachtung der Kaffeemaschinensteuerung koennte Vivian als externer Assistenzdienst auftreten. | unscharf | In 9.4 klaeren, ob eine explizite SystemBoundary- oder RoleView-Ergaenzung sinnvoll ist. |
| Vivian-Dialogzustand `guiding`, `awaitingConfirmation`, `errorExplained` | `StateAssertion.expectedState` ueber `VivianAssistant.mode` und `feedbackState` | Dialog- und Assistenzzustaende sind Strings ohne erlaubte Transitionen, Prioritaeten oder Dialogkontext. | grenzwertig | Kandidat fuer optionales Dialogue-/Assistant-State-Ergaenzungsmodell. |
| Vivian-Hinweise wie `placeCup`, `selectProgram`, `placeCupAgain` | `StateAssertion.expectedState`, `Capability.intent`, RuntimeAction-Schemas | Hinweisinhalt, Zielgruppe, Medium, Sprache, Visualisierung und Bezug auf Szenenobjekte sind nicht strukturiert. | unscharf | In 9.4 pruefen, ob GuidanceContent oder InteractionMessage als Ergaenzungsmodell noetig ist. |
| Fehlererklaerung `waterLevelLow` | `Capability`, `Effect`, `RuntimeAction.inputSchema.reasonCode` | Fehlergrund ist als String transportierbar, aber Ursache, Schweregrad, Korrekturhinweis und Wiederaufnahmeoption sind nicht getrennt. | unscharf | Eventuell ErrorExplanation-/Recovery-Ergaenzung statt Kernklasse. |
| Vivian fordert explizite Startbestaetigung | `CAP-B-VIVIAN-REQUEST-CONFIRMATION`; `B-RB-VIVIAN-CONFIRMATION-PROMPT`; RuntimeAction-Affordance | Die Rueckfrage ist modellierbar, aber die Benutzerantwort, Timeout, Ablehnung, Wiederholung oder Abbruchpolitik sind nicht formal. | grenzwertig | In 9.3 pruefen, ob fehlende Antwort-/Timeout-Semantik eine harte Luecke fuer B ist. |
| Vivian loest assistierten Start nicht selbst als Actor aus | `systemResponse` mit `CapabilityUse(CAP-B-START-BREWING)` und CoffeeMachine-Capability | Die Verantwortung zwischen Vivian, System und Kaffeemaschine ist fachlich nachvollziehbar, aber nicht als Responsibility- oder Authority-Beziehung modelliert. | unscharf | In 9.4 klaeren, ob Capability-Provider plus Guard ausreicht oder Authority ergaenzt werden sollte. |
| Optionale Trainings- oder Detailerklaerungen | in 7.8 als Extend-Kandidaten dokumentiert, nicht formal instanziiert | ExtensionPoints und optionale Vivian-Zusatzusecases sind nur Kandidaten. Der aktuelle Kern zeigt nicht, wann Zusatzdialog fachlich aktiviert wird. | indirekt | In 9.3 nur dann als Luecke werten, wenn Trainingsmodus im Zielumfang bleiben soll. |
| Vivian-Fortschrittskommentar | als moeglicher Extend-Kandidat; nicht im Hauptpfad | Maschinenfortschritt ist sichtbar, aber Vivian-Kommentar waere optionaler Dialog. Die Grenze zwischen Basisfeedback und Zusatzassistenz ist textuell. | indirekt | In 9.4 als Extend-/Dialogue-Ergaenzung bewerten, nicht zwingend Kern. |
| Vivian-Modalitaet | Runtime-Kontexte `VivianAssistantRuntime` und `VRInteractionRuntime` | Ob Vivian per Avatar, Text, Sprache, Geste oder kombinierten Kanalen kommuniziert, ist nicht im fachlichen Modell strukturiert. | unscharf | Kandidat fuer UI-/Multimodal-Interaction-Ergaenzung. |
| Vivian-Personalisierung oder Adaptivitaet | nicht formal modelliert; hoechstens in Runtime/Content-Schemas andeutbar | Nutzerprofil, Hilfestufe, Lernstand oder Praeferenz fehlen als modellierte Parameter. | indirekt | Nur in 9.3 relevant, wenn adaptive Assistenz zum Scope gehoert. |

## Interaktionsobjekt-spezifische Problemtabelle

| Element oder Konzept | Aktuelle Abbildung | Problem | Bewertung | Konsequenz fuer 9.3/9.4 |
| --- | --- | --- | --- | --- |
| Kaffeemaschine als generische `Entity` mit `Entity.kind = asset` | `ENT-B-02 CoffeeMachine`; StateAssertions und Capabilities | Das Objekt ist identifizierbar, aber nicht als spezifisches Interaktionsobjekt mit Bedienpunkten, Affordances und Manipulationszonen strukturiert. | grenzwertig | In 9.4 pruefen, ob `InteractionObject` oder Affordance-Ergaenzung noetig ist. |
| Starttaste | Benutzerereignis `pressed(Visitor, CoffeeMachine.startButton)` und Step `B-MAIN-S09` | Der Button ist kein eigenes Element. Position, Sichtbarkeit, Bedienart und Aktivierungsbedingung stehen nur im Ausdruck. | unscharf | Kandidat fuer Interaktionsobjekt-/Affordance-Ergaenzung. |
| Tassenbereich | `CoffeeMachine.cupArea` in Event-/Runtime-Ausdruecken; `Cup` als Kontext-Entity | Der Bereich ist keine eigene Entity mit Geometrie, Erkennungszone oder Toleranz. | unscharf | In 9.4 mit Spatial-/Affordance-Ergaenzung zusammen bewerten. |
| Programmauswahl | `CoffeeMachine.selectedProgram = coffee`; Event `selectedProgram(...)` | Auswahloptionen, Auswahloberflaeche, erlaubte Werte und UI-Zustaende sind nicht strukturiert. | unscharf | Fuer einfache Demo ausreichend; fuer Produkt-/Toolchain-Modell evtl. OptionSet-Ergaenzung. |
| Bereitschaftsmerkmale Wasser, Tasse, Programm | `Condition.expression` und `StateAssertion.expectedState` | Die Merkmale sind pruefbar, aber ihre logische Kombination, Prioritaet und Fehlerdiagnose sind nicht als eigene Rule-Struktur formalisiert. | grenzwertig | In 9.4 pruefen, ob ReadinessRule oder Constraint-Ergaenzung sinnvoll ist. |
| Maschinen-Lifecycle `idle`, `ready`, `notReady`, `brewing`, `finished` | `StateAssertion.expectedState` und Conditions | Lebenszykluswerte sind Strings ohne expliziten Zustandsautomaten, erlaubte Transitionen oder gegenseitige Ausschlussregeln. | grenzwertig | Kandidat fuer StateMachine-/ObjectLifecycle-Ergaenzung. |
| Orthogonale Maschinenmerkmale | `waterLevel`, `cupPresent`, `selectedProgram`, `startPermission`, Feedback-Flags | Die Orthogonalitaet ist dokumentiert, aber nicht formal durch getrennte State-Dimensionen modelliert. | unscharf | In 9.4 pruefen, ob StateDimension-Struktur gebraucht wird. |
| Maschinenfeedback `readyFeedback`, `progressIndicator`, `completionFeedback` | `StateAssertion` und `Event.kind = environment` | Feedback ist sichtbar modellierbar, aber Medium, Empfaenger, Dauer und Inhalt sind nicht formal getrennt. | unscharf | Kandidat fuer Feedback-/Presentation-Ergaenzung. |
| Bruehfortschritt | `SA-B-CM-PROGRESS-VISIBLE`, Event `shown(CoffeeMachine.progressIndicator)` | Fortschritt ist nur als sichtbar markiert, nicht als Wert, Verlauf, Dauer oder Prozentbereich. | indirekt | Nur bei genauer Prozesssimulation in 9.4 vertiefen. |
| Bruehvorgang als Prozess | `CoffeeMachine.lifecycleState = brewing` und RuntimeActions | Der Prozess ist als Zustand beobachtbar, aber Prozessdauer, Startzeit, Endbedingung und Unterbrechung sind nicht formal. | unscharf | Moeglicher Process-/Temporal-Ergaenzungskandidat. |
| Tasse als Kontextobjekt | `ENT-B-03 Cup` minimal; `SA-B-CUP-PLACED` | Die Tasse ist referenzierbar, aber Position, Fassungsvermoegen, Ausrichtung oder Eignung fuer Kaffee sind nicht strukturiert. | indirekt | Nur erweitern, wenn physische Objektinteraktion relevant wird. |
| BrewingRequest als Kontextobjekt | `ENT-B-04 BrewingRequest` minimal; StateAssertions | Request-Zustand ist modellierbar, aber Request-Lifecycle, Autorisierung, Besitzer und Abbruchpfad sind nicht explizit. | grenzwertig | In 9.3 pruefen, ob Abbruch/Timeout im Scope harte Luecken erzeugt. |
| Sicherer Zustand `CoffeeMachine.safeState = true` | `StateAssertion` und Exception-Postcondition | Sicherheitsbezug ist pruefbar, aber SafetyGoal, Hazard, Severity und Risk-Argument fehlen. | indirekt | Falls Safety-Argumentation gefordert ist, eher Safety-Ergaenzung als Kern. |

## Szenario- und Ablaufunschaerfen

| Element oder Konzept | Aktuelle Abbildung | Problem | Bewertung | Konsequenz fuer 9.3/9.4 |
| --- | --- | --- | --- | --- |
| Alternative Rueckfuehrung vor `B-MAIN-S06` | `StepRelation` von `B-ALT-S04` zu `B-MAIN-S06` | Rueckfuehrung funktioniert, aber Entry-/ReturnPoint-Semantik ist nicht als eigene Beziehung modelliert. | grenzwertig | In 9.4 pruefen, ob CrossScenarioTransition strukturiert werden sollte. |
| Exception ohne Rueckkehr | `Scenario.kind = exception`; keine Rueckfuehrung | Abbruchsemantik, Recovery-Policy und Endzustandsklassifikation sind textuell beschrieben. | indirekt | Fuer B ausreichend; bei Safety/Training evtl. Exception-Ergaenzung. |
| Branch-Anker `B-BRANCH-*` | dokumentierte Analyseinformation, keine formale Instanz | Branch-Anker sind nuetzlich fuer Planung, aber nicht Teil des Metamodells und deshalb nicht maschinenpruefbar. | unscharf | In 9.4 entscheiden, ob BranchPoint/VariationPoint noetig ist. |
| Include-Kandidat Bereitschaftspruefung | in 7.8 dokumentiert, kein formales Include | Wiederverwendbarkeit ist erkannt, aber ohne eigenen UseCase `UC-B-02` nicht formal instanziiert. | indirekt | In 9.3 nur als Luecke werten, falls Reuse-Schicht gefordert wird. |
| Extend-Kandidaten fuer Vivian-Zusatzverhalten | in 7.8 dokumentiert, keine ExtensionPoints | ExtensionPoints sind nur Kandidaten; ohne formale Punkte gibt es kein korrektes Extend. | indirekt | In 9.4 als optionales UseCase-Extension-Thema bewerten. |
| Kontrollierter Abbruch durch Visitor | Handlungskatalog nennt B-ACT-006, aber nicht formal als B-Scenario instanziiert | Abbruch ist fachlich plausibel, aber nicht im aktuellen B-Baseline-Szenario ausgearbeitet. | grenzwertig | In 9.3 pruefen, ob Abbruch fuer den geforderten Scope zwingend ist. |
| Fehlendes Programm als Alternative | Branch-Anker/Kandidaten vorhanden, aber nur fehlende Tasse formal ausgearbeitet | Programmmangel ist analog modellierbar, aber nicht instanziiert. | indirekt | Kein Metamodellproblem; eher Umfangsentscheidung. |

## Event-, Condition- und Trace-Unschaerfen

| Element oder Konzept | Aktuelle Abbildung | Problem | Bewertung | Konsequenz fuer 9.3/9.4 |
| --- | --- | --- | --- | --- |
| Eventquelle und Eventziel | `Event.expression` wie `pressed(Visitor, CoffeeMachine.startButton)` | Quelle, Ziel, Objekt, Payload und Kanal sind nicht eigene Attribute oder Beziehungen. | unscharf | Event-Ergaenzung pruefen, falls maschinelle Auswertung wichtig wird. |
| Event-Kind `user`, `signal`, `environment` | Tabellenattribut `Event.kind` | Grobe Typisierung reicht fuer Trace, aber nicht fuer detaillierte Quellen-, Kanal- und Prioritaetslogik. | indirekt | Fuer B ausreichend; bei Runtime-Event-Orchestrierung vertiefen. |
| Guard-Ausdruecke | `Condition.expression` | Conditions sind pruefbar beschrieben, aber nicht als formale Logik mit Operatorbaum, Prioritaet oder Konfliktauflosung. | unscharf | Kandidat fuer Constraint-/Expression-Ergaenzung. |
| Readiness-Ergebnis | `ReadinessCheck.result = passed|failed` in Conditions/Effects/RuntimeSchemas | `ReadinessCheck` ist kein eigenes identifizierbares Modellelement, sondern Ausdrucksbegriff. | grenzwertig | In 9.3 pruefen, ob `ReadinessCheck` als Entity/ValidationObject fehlt. |
| Effect-StateAssertion-Rueckbindung | Trace-Tabellen in Capability- und RuntimeAction-Artefakten | Es gibt keine eigene Metamodellkante `Effect -> StateAssertion`; Rueckbindung ist dokumentarisch. | indirekt | In 9.4 pruefen, ob `realizedBy`/`observedAs`-Kante sinnvoll ist. |
| Requirement-Trace auf feine Elemente | ValidationCases und Tabellen; keine formalen B-Satisfy-Instanzen | Traceability ist nachvollziehbar, aber formale Satisfy-Instanzen fehlen noch fuer B. | indirekt | In 9.3 klaeren, ob fehlende B-Satisfy-Instanzen als Scope-Luecke gelten. |
| Entity.kind-Werte `asset`, `system` | Tabellenkonvention | Hilfreich, aber im kompakten Diagramm nur begrenzt als zentraler Typmechanismus sichtbar. | grenzwertig | In 9.4 pruefen, ob `Entity.kind` expliziter Kernbestandteil werden soll. |

## Runtime- und Validation-Unschaerfen

| Element oder Konzept | Aktuelle Abbildung | Problem | Bewertung | Konsequenz fuer 9.3/9.4 |
| --- | --- | --- | --- | --- |
| Runtime-Kontexte `VivianAssistantRuntime`, `VRInteractionRuntime`, `CoffeeMachineAdapterRuntime` | Tabellenwerte in RuntimeBindings | Plattform, Version, Adapterwahl, Deployment und Verfuegbarkeit sind nicht strukturiert. | unscharf | RuntimeProfile-Ergaenzung in 9.4 pruefen. |
| RuntimeAction-Reihenfolge | Textabschnitt `Ausfuehrungsreihenfolge innerhalb der Bindings` | Reihenfolge ist fuer Ausfuehrung relevant, aber keine eigene Metamodellkante. | grenzwertig | In 9.4 pruefen, ob `RuntimeAction.order` oder ActionDependency noetig ist. |
| RuntimeAction-Schemas `Schema.*` | `inputSchema` und `outputSchema` als benannte Attributwerte | Schemas sind dokumentiert, aber nicht als eigene strukturierte Schema-Elemente modelliert. | unscharf | Fuer Codegenerierung Schema-Ergaenzung sinnvoll. |
| RuntimeAction-Fehlerverhalten | teilweise `reasonCode`, `accepted`, `message` in Schemas | Fehlerarten, Retry, Timeout und Fallback sind nicht formalisiert. | unscharf | In 9.3 pruefen, ob Runtime-Ausfall im Scope harte Luecke ist. |
| ValidationCase-Stimulus | Text in ValidationCase-Tabelle | Stimulus ist pruefbar beschrieben, aber keine formale Sequenz von Events, Conditions und RuntimeActions. | indirekt | TestModel-Ergaenzung nur bei Automatisierung noetig. |
| ValidationCase-ExpectedOutcome | StateAssertion-Liste plus Strukturregeltext | Zusammengesetzte Erwartungen, Negationen und zeitliche Reihenfolgen sind nicht formal maschinenlesbar. | unscharf | Assertion-/Temporal-Ergaenzung in 9.4 bewerten. |
| Kein RuntimeBinding-Fallback | ValidationCase kann fehlende Binding pruefen, aber kein Modell fuer Fallback-Strategie | Fehlende oder fehlschlagende technische Bindung ist als Pruefproblem erkennbar, aber nicht als fachlicher Recovery-Pfad modelliert. | indirekt | Nur bei Toolchain-Resilienz als harte Luecke bewerten. |

## Gruppierung nach Problemtyp

| Problemtyp | Betroffene Elemente | Warum nicht direkt sauber genug? |
| --- | --- | --- |
| Vivian-Dialog und Assistenzinhalt | Vivian-Modus, GuidanceTopic, Fehlererklaerung, Startbestaetigung, optionaler Trainingsdialog | Fachliche Reaktion ist modellierbar, aber Dialoginhalt, Modalitaet und Strategie sind nicht strukturiert. |
| Interaktionsobjekt und Affordances | Starttaste, Tassenbereich, Programmauswahl, Feedbackanzeigen | Kaffeemaschine ist Entity, aber Bedienpunkte und Affordances sind nur in Expressions. |
| Objektzustandsautomat | Maschinen-Lifecycle, Request-Lifecycle, sicherer Zustand | Zustaende sind StateAssertions; Transitionen, Ausschlussregeln und Recovery sind nicht eigenstaendig. |
| Event- und Condition-Struktur | User-/Signal-/Environment-Events, Guards, ReadinessCheck | Quelle, Ziel, Payload und Logik bleiben Ausdrucksstrings. |
| Runtime-Orchestrierung | Runtime-Kontexte, Action-Reihenfolge, Schemas, Fehlerverhalten | Technische Aktionen existieren, aber Orchestrierung und Plattformprofile sind textuell. |
| Feingranulare Traceability | Effect-StateAssertion-Bezug, B-Satisfy, Validation-Outcome | Trace ist nachvollziehbar, aber nicht jede Feinstruktur ist eigene Metamodellkante. |

## Bewertung fuer Anwendungsfall B

| Frage | Antwort |
| --- | --- |
| Kann B mit dem aktuellen Modell beschrieben werden? | ja |
| Gibt es eine Kardinalitaets- oder Invariantenverletzung? | nein |
| Sind alle fachlich zentralen Elemente mindestens modellierbar? | ja |
| Gibt es unscharfe Stellen fuer automatische Auswertung oder Codegenerierung? | ja |
| Sind Vivian-spezifische und Interaktionsobjekt-spezifische Unklarheiten getrennt? | ja |
| Muss deshalb der Kern sofort erweitert werden? | noch nicht entschieden; Entscheidung folgt in 9.4 |

## Abnahmekontrolle

| Kriterium aus Task 9.2 | Erfuellung |
| --- | --- |
| Problemtabelle vorhanden | Mehrere Problemtabellen benennen konkrete B-Elemente und Probleme. |
| Vivian-spezifische Unklarheiten getrennt | Eigene Tabelle `Vivian-spezifische Problemtabelle` vorhanden. |
| Interaktionsobjekt-spezifische Unklarheiten getrennt | Eigene Tabelle `Interaktionsobjekt-spezifische Problemtabelle` vorhanden. |
| Problem konkret benannt | Jede Zeile nennt aktuelle Abbildung, Problem und Bewertung. |
| Keine harte Lueckenentscheidung vorweggenommen | Task 9.3 bleibt fuer nicht modellierbare Elemente reserviert. |
| Keine Modellanpassung vorweggenommen | Task 9.4 bleibt fuer Kern- oder Ergaenzungsmodell-Entscheidungen reserviert. |

## Konsequenz fuer Task 9.3

Task 9.3 kann nun pruefen, ob unter den oben genannten unscharfen Punkten harte Luecken existieren. Eine harte Luecke liegt nur dann vor, wenn ein Element mit keiner vorhandenen Klasse, keinem Attribut und keiner dokumentierten Trace-Konvention sinnvoll abbildbar ist.
