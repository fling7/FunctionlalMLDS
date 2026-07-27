# Spezifikation 11.4: Minimale Kernanpassungen

Stand: 2026-07-07

Task: 11.4 `Minimale Kernanpassungen spezifizieren, falls erforderlich`

Zweck: Diese Datei spezifiziert nur die Kernanpassungen, die in `gap_criteria_evaluation.md` als `Kern` bewertet wurden. Sie nimmt keine Ergaenzungsmodule vorweg.

Bezugsdateien:

- `gap_criteria_evaluation.md`
- `core_adaptation_criteria.md`
- `cardinality_table.md`
- `dynamic_functional_mlds_specification.md`
- `invariants.md`

## Entscheidung

Es werden genau zwei minimale Kernanpassungen geplant:

| Nr. | Kernanpassung | Typ | Status |
| --- | --- | --- | --- |
| KERN-01 | `Entity.kind: EntityKind [0..1]` | optionales Attribut plus kleine Enumeration | aufnehmen |
| KERN-02 | `Effect.evidencedBy -> StateAssertion [0..*]` | optionale, nicht-kompositive Trace-Referenz | aufnehmen |

Keine weiteren Gaps werden in den Kern aufgenommen.

Insbesondere nicht Teil von 11.4 sind:

- `InteractionObject`, `Affordance`, `ControlSurface`,
- `SpatialRelation`, `SpatialRegion`, `SpatialFrame`,
- `State`, `StateTransition`, `TransitionPolicy`,
- `DialogueAct`, `GuidanceContent`, `AssistantInteraction`,
- `DecisionRule`, `ReadinessRule`, `AuthorizationPolicy`,
- `RuntimeProfile`, `RuntimeExecution`, `RuntimeActionOrder`,
- `ValidationOutcome` oder formale Assertion-Logik.

Diese Bedarfe bleiben Ergaenzungsmodelle oder fuer die aktuelle Baseline ohne Modellbedarf.

## KERN-01: Optionale Entity-Typisierung

### Geaenderte Klasse

| Klasse | Aenderung |
| --- | --- |
| `Entity` | neues optionales Attribut `kind: EntityKind [0..1]` |

`Entity.kind` ist eine grobe fachliche Einordnung einer identifizierbaren Entity. Das Attribut hilft Generatoren, Validatoren und Lesern, Entity-Instanzen maschinenlesbar zu unterscheiden, ohne fuer jedes Szenenobjekt eine neue Kernklasse einzufuehren.

### Neue Enumeration

| Enumeration | Werte | Bedeutung |
| --- | --- | --- |
| `EntityKind` | `agent`, `asset`, `zone`, `signal`, `stateObject` | kleine, stabile Oberkategorien fuer Kernmodelle |

Die Werte sind bewusst grob:

| Wert | Bedeutung | A-Beispiel | B-Beispiel |
| --- | --- | --- | --- |
| `agent` | aktive systemische Entity; muss mit `Agent` konsistent sein | `AgentBody` | `VivianAssistant` |
| `asset` | physisches oder digitales Objekt, das Zustand tragen oder Capability bereitstellen kann | `InteractionAsset` | `CoffeeMachine`, `Cup` |
| `zone` | raeumlicher oder semantischer Bereich, Grenze oder Region | `TriggerZone`, `TargetZone`, `SceneBoundary`, `ObstacleRegion` | `CoffeeMachine.cupArea`, falls als Entity instanziiert |
| `signal` | Signal-, Marker- oder Feedback-Entity | `FeedbackSignal`, `InstructionMarker`, `ExternalSignalSource` | `readyFeedback`, `completionFeedback` |
| `stateObject` | fachliches Informations-, Request- oder Statusobjekt | `SceneStateFlag`, `ObservationPoint` | `BrewingRequest` |

Die Enumeration darf nicht mit domaenenspezifischen Detailtypen wie `coffeeMachine`, `startButton`, `cupArea`, `avatar`, `ttsVoice` oder `unityController` aufgeblasen werden. Solche Typen gehoeren in Ergaenzungsmodule oder Instanzattribute.

### Kardinalitaet

| Element | Kardinalitaet | Besitzsemantik |
| --- | ---: | --- |
| `Entity.kind` | `0..1` | Attributwert der Entity; keine eigene Besitzbeziehung zu anderen Kernobjekten |

`0..1` ist zwingend: Bestehende Entity-Instanzen bleiben ohne Typisierung gueltig.

### Invarianten

| ID | Invariante |
| --- | --- |
| INV-KERN-01 | `Entity.kind` ist optional. Fehlende Typisierung macht eine Entity nicht ungueltig. |
| INV-KERN-02 | Wenn `Entity.kind = agent`, dann muss die Instanz entweder `Agent` sein oder explizit als Agent-Spezialisierung modelliert werden. |
| INV-KERN-03 | `Entity.kind` ersetzt keine Spezialisierung. Insbesondere bleibt `Agent --|> Entity` die einzige Kern-Spezialisierung fuer aktive systemische Subjekte. |
| INV-KERN-04 | `Entity.kind` darf nicht benutzt werden, um `Actor` und `Entity` zu vermischen. Externe Use-Case-Rollen bleiben `Actor`. |
| INV-KERN-05 | Domaenen- oder runtime-spezifische Feintypen duerfen nicht in die Kern-Enumeration aufgenommen werden. |

### Begruendung

`Entity.kind` erfuellt die Kernkriterien:

| Kriterium | Bewertung |
| --- | --- |
| Allgemeingueltigkeit | A und B nutzen unterschiedliche Entity-Arten; beide profitieren von einer groben Typisierung. |
| Kompaktheit | Ein optionales Attribut plus kleine Enumeration reicht aus. |
| EAST-ADL-Nahe | Die Typisierung bleibt fachlich und tracebar; sie fuehrt keine technische Runtime-Semantik ein. |
| Wiederverwendbarkeit | Die Oberkategorien sind ueber Use Cases und Toolchains hinweg nutzbar. |
| Rueckwaertskompatibilitaet | Bestehende Instanzen bleiben gueltig, weil das Attribut optional ist. |

## KERN-02: Optionale Trace-Kante von Effect zu StateAssertion

### Geaenderte Klasse und Beziehung

| Quelle | Ziel | Rollenname | Beziehungstyp | Kardinalitaet am Ziel |
| --- | --- | --- | --- | ---: |
| `Effect` | `StateAssertion` | `evidencedBy` | association/reference | `0..*` |

`Effect.evidencedBy` referenziert konkrete Zustandsaussagen, die den versprochenen fachlichen Effekt beobachtbar machen.

Die Beziehung ist bewusst nicht-kompositiv:

- `Effect` besitzt `StateAssertion` nicht.
- `StateAssertion` bleibt ein eigenstaendiges fachliches Aussageobjekt und kann weiter von ScenarioSteps, ValidationCases oder Dokumentationsartefakten referenziert werden.
- Eine `StateAssertion` darf mehrere Effects stuetzen, wenn sie fachlich passt.

### Kardinalitaet

| Element / Beziehung | Kardinalitaet | Besitzsemantik |
| --- | ---: | --- |
| `Capability -> Effect` | `1..*` | unveraendert; Effects gehoeren zur Capability |
| `Effect.evidencedBy -> StateAssertion` | `0..*` | neue optionale Referenz; keine Komposition |
| inverse Sicht `StateAssertion.evidenceFor` | `0..*` | optional ableitbar; nicht zwingend als sichtbare Diagrammkante noetig |

`0..*` ist zwingend: Nicht jeder Effect muss sofort formal mit StateAssertions hinterlegt sein. Ein fachlich formulierter Effect bleibt auch ohne Evidence-Link gueltig.

### Invarianten

| ID | Invariante |
| --- | --- |
| INV-KERN-06 | `Effect.evidencedBy` ist optional und darf nicht als Pflichtnachweis fuer jede Capability missverstanden werden. |
| INV-KERN-07 | `Effect.evidencedBy` ist keine Komposition. Eine `StateAssertion` darf nicht durch einen Effect besessen oder exklusiv gebunden werden. |
| INV-KERN-08 | Eine referenzierte `StateAssertion` muss ein gueltiges `subjectRef [1]` besitzen. |
| INV-KERN-09 | Die referenzierte `StateAssertion` muss den fachlichen Inhalt des Effects stuetzen oder konkretisieren; sie darf ihm nicht widersprechen. |
| INV-KERN-10 | `Effect.evidencedBy` darf keine technische Kurzschaltung erzeugen. Der Pfad zu technischen Aktionen bleibt `Capability -> RuntimeBinding -> RuntimeAction`. |
| INV-KERN-11 | Die Kante darf nicht als formale Testorakel- oder ValidationOutcome-Sprache interpretiert werden. Komplexe Assertion-Logik bleibt Ergaenzungsmodell. |

### Beispiele

| Use Case | Effect | Evidencing StateAssertion |
| --- | --- | --- |
| A | `A-EFF-ROLE-EXECUTOR` | `A-SA-S05-01`, `AgentBody.roleState = executor` |
| A | `A-EFF-AGENT-MOVING-TO-TARGET` | `A-SA-S06-01`, `AgentBody.expectedState = movingTo(TargetZone)` |
| B | `B-EFF-CUP-GUIDANCE-ISSUED` | `SA-B-VIVIAN-GUIDANCE-CUP` |
| B | `B-EFF-BREWING-START-ISSUED` | StateAssertion fuer `CoffeeMachine.lifecycleState = brewing` |

### Begruendung

`Effect.evidencedBy` erfuellt die Kernkriterien:

| Kriterium | Bewertung |
| --- | --- |
| Allgemeingueltigkeit | A und B dokumentieren Effects, die durch konkrete StateAssertions beobachtbar werden. |
| Kompaktheit | Eine optionale Referenz reicht aus; keine neue StateMachine- oder Validation-Klasse noetig. |
| EAST-ADL-Nahe | Die Kante staerkt Traceability zwischen fachlicher Wirkung und Nachweis. |
| Wiederverwendbarkeit | Jede Capability mit beobachtbaren Effects kann davon profitieren. |
| Rueckwaertskompatibilitaet | Bestehende Effects bleiben gueltig, weil die Kante optional ist. |

## Diagramm- und Spezifikationsauswirkung

| Artefakt | Noetige Anpassung |
| --- | --- |
| Klassendiagramm | `Entity` erhaelt Attribut `kind: EntityKind [0..1]`; `EntityKind` wird als kleine Enumeration gezeigt; neue Assoziation `Effect -- evidencedBy --> StateAssertion [0..*]`. |
| Kardinalitaetstabelle | Zwei neue Eintraege: `Entity.kind [0..1]` und `Effect.evidencedBy -> StateAssertion [0..*]`. |
| Spezifikation | Abschnitt `Zentrale Kardinalitaeten` und `Diagramm-Beziehungsabdeckung` um die neue optionale Trace-Kante ergaenzen; Entity-Attribut beschreiben. |
| Invarianten | `INV-KERN-01` bis `INV-KERN-11` oder aequivalente Regeln aufnehmen. |
| Instanzartefakte | Keine Pflichtmigration; bestehende Entities koennen optional typisiert und bestehende Effect-StateAssertion-Traces formalisiert werden. |

## Nicht-Ziele dieser Kernanpassung

| Nicht-Ziel | Grund |
| --- | --- |
| Vollstaendige Objektontologie | `Entity.kind` ist nur grobe Typisierung, keine neue Klassenhierarchie. |
| Geometrische Raumsemantik | `zone` ersetzt kein `SpatialSemanticsModule`. |
| Affordance- oder Interaktionsobjektmodell | `asset` ersetzt kein `InteractionObjectModule`. |
| Formale StateMachine | `Effect.evidencedBy` ersetzt kein `StateTransitionModule`. |
| Formale ValidationOutcome-Sprache | `Effect.evidencedBy` ist Trace, keine Assertion-Logik. |
| Runtime-Orchestrierung | Keine neue direkte Runtime-Kante; technische Ausfuehrung bleibt unter `RuntimeBinding`. |

## Rueckwaertskompatibilitaet

| Bestandsmodell | Auswirkung |
| --- | --- |
| Entity ohne `kind` | bleibt gueltig |
| Agent als Spezialisierung von Entity | bleibt gueltig; optional `kind=agent` muss konsistent sein |
| Effect ohne `evidencedBy` | bleibt gueltig |
| StateAssertion ohne referenzierenden Effect | bleibt gueltig |
| Bestehende ScenarioSteps | bleiben gueltig |
| Bestehende RuntimeBindings und RuntimeActions | bleiben unveraendert |

## Abnahmekontrolle

| Kriterium aus Task 11.4 | Erfuellung |
| --- | --- |
| Liste geplanter Kernaenderungen vorhanden | `KERN-01` und `KERN-02` sind explizit benannt. |
| Neue oder veraenderte Klasse genannt | `Entity` wird erweitert; `EntityKind` wird als Enumeration ergaenzt; `Effect` erhaelt eine optionale Referenz. |
| Beziehung genannt | `Effect.evidencedBy -> StateAssertion` ist spezifiziert. |
| Kardinalitaet genannt | `Entity.kind [0..1]`; `Effect.evidencedBy [0..*]`; inverse Sicht `StateAssertion.evidenceFor [0..*]`. |
| Invarianten genannt | `INV-KERN-01` bis `INV-KERN-11` sind formuliert. |
| Keine unbewerteten Gaps in den Kern gezogen | Alle anderen Bedarfe bleiben Ergaenzungsmodell oder kein Modellbedarf. |

## Konsequenz fuer Task 11.5

11.5 soll nun die Ergaenzungsmodelle spezifizieren, ohne die beiden Kernanpassungen zu wiederholen. Alle Module muessen an bestehende Kernklassen andocken und duerfen die hier spezifizierten Kerninvarianten nicht verletzen.
