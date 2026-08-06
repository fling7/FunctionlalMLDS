# DFMLDS V2 - Optionales Mapping auf EAST-ADL Annex C

Stand: 2026-07-14  
Referenz: EAST-ADL V2.1.12, Annex C / BehaviorDescription, PDF-Seiten
212-236

## Status und Grenze

Annex C bezeichnet seine BehaviorDescription-Erweiterung selbst als
**vorlaeufig**, zwar sprachlich ausgerichtet, aber noch nicht validiert und noch
nicht zur Aufnahme in die Basisspezifikation bereit (S. 212). Das folgende
Mapping ist daher ein optionales, explizit aktiviertes Projektionsprofil. Es
veraendert weder den DFMLDS-Core noch die EAST-ADL-Basisklassen und ist keine
Voraussetzung fuer eine gueltige V2-Instanz.

Die Abbildung ist partiell: Ein DFMLDS-Element wird nur projiziert, wenn die in
der Tabelle genannten Vorbedingungen vorliegen. Nicht ausreichend bestimmte
Quellinformation wird nicht durch erfundene Annex-C-Elemente vervollstaendigt.

## Normative Projektionsregeln

| ID | DFMLDS-V2-Quelle | Erzeugte Annex-C-Struktur | Vorbedingungen und Regel | EAST-ADL-Beleg |
|---|---|---|---|---|
| AC-01 | `Scenario` als Projektionsumfang | projektionslokale `ScenarioAnnexMapping`-Beziehungen und ein Wurzel-`LogicalPath` | Fuer jedes tatsaechlich abgebildete Quellglied wird eine optionale `ScenarioAnnexMapping -> Relationship` erzeugt; `annexElement [1..*]` zeigt nur auf die erzeugten Annex-C-Elemente. Der aktuelle V2-Slice importiert keinen `ComputationConstraint`-Container und behauptet daher auch keinen solchen Container. Wenn ein externes Vollprofil ihn zusaetzlich erzeugt, muss dessen Constraint "mindestens eine Transformation oder Flowdefinition" erfuellt sein. | DFMLDS-Modellquelle; `ComputationConstraint` und Constraint [1], S. 225-226 |
| AC-02 | `ScenarioStep` | `ScenarioAnnexMapping.scenarioStep [0..1]` plus `LogicalTransformation` und `TransformationOccurrence` als `annexElement` | Die Transformation beschreibt die Schrittberechnung. Die Occurrence muss mit `invokedLogicalTransformation [1]` genau diese erzeugte Transformation referenzieren. Der zugehoerige Blattpfad besitzt `transformationOccurrence [0..1] {composite}`. Eine Schrittausfuehrung wird nicht mit einem EAST-ADL-FunctionPrototype gleichgesetzt. | `LogicalTransformation`, S. 227-228; `TransformationOccurrence.invokedLogicalTransformation [1]`, S. 228-229; `LogicalPath.transformationOccurrence`, S. 227 |
| AC-03 | `StepRelation(kind=sequence)` | geordnete `LogicalPath.segment[*]`-Eintraege | `segment` enthaelt **ausschliesslich erzeugte `LogicalPath`-Elemente**, nie `ScenarioStep`, `StepRelation` oder IDs dieser DFMLDS-Klassen. Die Reihenfolge folgt dem kanonischen Kontrollfluss, nicht einer zufaelligen Containerreihenfolge. | `LogicalPath.segment : LogicalPath [*] {ordered}`, S. 226-227 |
| AC-04 | konsistente Fork-/Join-Region und zugehoerige `ParallelGroup` | `LogicalPath.strand[*]` | Fuer jeden parallelen Zweig wird zuerst ein eigener `LogicalPath` erzeugt. `strand` referenziert nur diese erzeugten Pfade. Das Mapping ist unzulaessig, wenn Gruppenmitglieder nicht vollstaendig zwischen demselben Fork und Join erreichbar sind. | `LogicalPath.strand : LogicalPath [*]`, parallele/serielle Kombination, S. 226-227 |
| AC-05 | `ScenarioEvent` mit Ausfuehrungsereignis-Semantik | separates `TransitionEvent`; dessen `occurredExecutionEvent[*]` referenziert das `ScenarioEvent` | `TransitionEvent` wird **nicht** als Unter- oder Oberklasse von `Timing::Event` modelliert. Es ist ein eigenes Annex-C-Element. Die Bruecke ist allein die Assoziation `occurredExecutionEvent : Timing::Event [*]`. | `TransitionEvent -> EAElement + BehaviorConstraintParameter`, `occurredExecutionEvent : Event [*]`, S. 236; `Timing::Event` S. 113-116 |
| AC-06 | wertbezogenes `ScenarioEvent` oder wertbezogene `ScenarioCondition` | `LogicalEvent` bzw. `Quantification`; optional `TransitionEvent.occurredLogicalEvent[*]` | Nur bei vorhandenen, typisierten Operanden. Eine `Quantification` braucht mindestens ein `Attribute`; `operand [1..*] {ordered}` darf nicht leer sein. Ein Textausdruck allein rechtfertigt keine erfundene Operandenzuordnung. | `LogicalEvent -> Quantification`, S. 223; `Quantification -> EAElement + EAExpression`, `operand [1..*]`, Constraint [1], S. 223-224; `occurredLogicalEvent[*]`, S. 236 |
| AC-07 | zeitbezogene `ScenarioCondition` | `LogicalTimeCondition`; optional Verwendung als `LogicalTransformation.timeInvariant`, `TransformationOccurrence.timeCondition`, `Transition.timeGuard` oder `State.timeInvariant` | Nur wenn Zeitbasis und Grenzen bzw. Ereignisreferenzen aus der Quelle ableitbar sind. Start-/Endreferenzen zeigen auf erzeugte `TransitionEvent`-Elemente, nicht direkt auf `Timing::Event`. | `LogicalTimeCondition`, `startPointReference/endPointReference : TransitionEvent [0..1]`, S. 232; Verwendungen S. 228-229, 233, 235 |
| AC-08 | lokale Guard-Bedingung einer `StepRelation` | `Transition.quantificationGuard[*]` oder `Transition.timeGuard[*]` | Nur nach erfolgreicher AC-06- bzw. AC-07-Projektion. Eine Bedingung wird genau entsprechend ihrer Bedeutung als Wert- oder Zeitguard abgebildet; ein raeumlicher Guard bleibt ohne passendes Profil DFMLDS-eigen. | `Transition.quantificationGuard[*]`, `timeGuard[*]`, S. 235 |
| AC-09 | `StateAssertion` | optional `State.quantificationInvariant[*]`, `State.timeInvariant[*]` oder ausserhalb Annex C ein `StateAssertionOutcome` / `VVIntendedOutcome` | Die Zielrolle wird nach Aussageart gewaehlt. Eine wiederverwendbare StateAssertion bleibt als DFMLDS-Quelle erhalten und wird nicht pauschal in einen Annex-C-State umklassifiziert. | `State.quantificationInvariant[*]`, `timeInvariant[*]`, S. 232-233; V&V S. 106-111 |
| AC-10 | `CapabilityBehaviorBinding` mit hinreichend formaler Verhaltensbeschreibung | `BehaviorConstraintType` mit passenden Quantification-, Computation- und/oder Temporal-Constraints | Nur bei mindestens einem fachlichen Target und mindestens einer inhaltlichen Constraint-Struktur. `BehaviorConstraintType` ist ein `Context`; seine Unterstrukturen sind komposit. | `BehaviorConstraintType -> Context`, Bestandteile und Constraint [1], S. 219-220 |
| AC-11 | Zielseite von AC-10 | `BehaviorConstraintTargetBinding` | Das Binding generalisiert `Relationship`, referenziert genau einen `behaviorConstraintType [1]` und mindestens ein tatsaechlich vorhandenes Ziel, z. B. `targetedVehicleFeature[*]`, `constrainedModeBehavior[*]`, `targetedFunctionType[*]`, `constrainedFunctionBehavior[*]` oder `constrainedFunctionTriggering[*]`. DFMLDS darf kein Dummy-Target erzeugen, nur um die Annex-C-Constraint zu erfuellen. | `BehaviorConstraintTargetBinding -> Relationship`; Zielrollen und `behaviorConstraintType [1]`, S. 218-219; Target-Constraint des Typs, S. 220 |
| AC-12 | optionale Prototype-Instanzierung | keine automatische V2-Abbildung | `BehaviorConstraintPrototype` gehoert nicht zum aktuell importierten V2-Slice. Ein externes Annex-C-Vollprofil darf es nur bei vorhandenem `BehaviorConstraintType [1]`, gueltigem Part-Kontext und vollstaendigen Instantiierungsvariablen erzeugen. Die V2-Projektion erfindet diese Angaben nicht. | `BehaviorConstraintPrototype -> TraceableSpecification`, `type [1]`, Part-/Variablen-Constraint, S. 218 |
| AC-13 | `Capability` mit automotive Feature-Bezug | separate optionale `CapabilityFeatureMapping -> Relationship` mit `capability [1]` und `feature: Feature [1]` | Nur im aktivierten Featureprofil und nur bei vorhandenem Ziel-Feature. Ein `VehicleFeature` ist als Spezialisierung von `Feature` zulaessig, wird aber durch keine zweite Rolle verlangt. Das Feature-Mapping bleibt von `BehaviorConstraintTargetBinding` getrennt. Im domaenenuebergreifenden Core wird kein VehicleFeature erzeugt oder verlangt. | Feature S. 28-29; VehicleFeature -> Feature, S. 38-39; Annex-C-Status S. 212 |

## Besonders wichtige Typgrenze: `TransitionEvent` und `Timing::Event`

Die beiden Klassen bezeichnen verschiedene Ebenen:

```text
DFMLDS::V2::ScenarioEvent
        --generalizes/use of--> EAST-ADL::Timing::Event

EAST-ADL::AnnexC::TransitionEvent
        --generalizes--> EAElement
        --generalizes--> BehaviorConstraintParameter
        --occurredExecutionEvent [*]--> EAST-ADL::Timing::Event
```

Zulaessig ist also:

```text
generatedTransitionEvent.occurredExecutionEvent += sourceScenarioEvent
```

Unzulaessig sind dagegen Generalisierungen `TransitionEvent -> Timing::Event`,
`Timing::Event -> TransitionEvent` oder `ScenarioEvent -> TransitionEvent`.
Auch ein gleichlautender Ausdruck macht diese Typen nicht identisch.

## Konstruktion von `LogicalPath.segment` und `strand`

Die Projection erzeugt zunaechst Pfade und verknuepft erst danach Pfade mit
Pfaden:

1. Fuer jeden projizierbaren Schritt wird ein `LogicalTransformation`-Element
   und dessen `TransformationOccurrence` erzeugt.
2. Um die Occurrence wird ein Blatt-`LogicalPath` mit
   `transformationOccurrence [0..1] {composite}` erzeugt.
3. Eine Sequenz erzeugt einen uebergeordneten Pfad, dessen geordnete
   `segment`-Liste diese Blatt- oder Teilpfade referenziert.
4. Eine Parallelregion erzeugt je Zweig einen Teilpfad; der uebergeordnete Pfad
   referenziert diese Teilpfade ueber `strand`.
5. Ein Element darf im selben Elternpfad nicht zugleich als `segment` und
   `strand` dienen. Verschachtelung wird durch zusaetzliche Teilpfade
   ausgedrueckt.

Damit bleiben die EAST-ADL-Typen der Rollen erhalten: Sowohl `segment` als auch
`strand` enthalten `LogicalPath`, niemals DFMLDS-Schritte oder Gruppen.

## BehaviorConstraint-Target-Regel

Eine Verhaltensconstraint ohne fachliches Ziel wird nicht exportiert. Fuer jede
erzeugte `BehaviorConstraintType`-Instanz gilt:

- mindestens ein Requirement, VehicleFeature, Mode, FunctionType,
  FunctionBehavior, FunctionTrigger oder Error-Behavior-Ziel muss fachlich
  belegt sein (Constraint [1], S. 220);
- die konkrete Verbindung wird als `BehaviorConstraintTargetBinding`
  modelliert, nicht als untypisierte DFMLDS-Kante;
- `behaviorConstraintType [1]` verweist auf genau den erzeugten Constraint-Typ;
- die Target-Rolle wird nach dem wirklichen Ziel gewaehlt, z. B.
  `targetedVehicleFeature` fuer ein VehicleFeature,
  `constrainedModeBehavior` fuer einen Mode,
  `targetedFunctionType` fuer einen FunctionType und
  `constrainedFunctionBehavior` fuer ein FunctionBehavior;
- ein `CapabilityBehaviorBinding` allein ist nur die DFMLDS-Bruecke. Es ersetzt
  weder die Annex-C-Constraint-Struktur noch ein gueltiges Ziel.

## Projektionsweite Vorbedingungen

Vor jeder Annex-C-Projektion muessen alle folgenden Bedingungen gelten:

1. Das Annex-C-Profil ist explizit aktiviert; Standard ist deaktiviert.
2. Die Quelle erfuellt die DFMLDS-V2-Invarianten fuer Kontrollfluss,
   Typisierung und Referenzaufloesung.
3. Jedes erzeugte Annex-C-Element erhaelt eine stabile Herkunftsreferenz auf
   sein DFMLDS-Element; die Quelle selbst wird nicht veraendert.
4. Alle EAST-ADL-Pflichtrollen der erzeugten Elemente sind belegt. Kann dies
   nicht aus der Quelle erfolgen, wird die jeweilige Teilprojektion ausgelassen
   und diagnostiziert.
5. Run-to-completion wird fuer `LogicalTransformation` und angebundene
   `FunctionBehavior`-Semantik respektiert (S. 228 bzw. S. 70). Offene,
   dauerhaft laufende Dialog- oder VR-Prozesse werden nicht ohne explizite
   Segmentierung als eine einzelne Transformation projiziert.
6. Die Projektion darf weder v0.5-Runtime-Felder aendern noch EAST-ADL-Klassen
   um neue Pflichtmerkmale erweitern.

## Nicht abgebildete oder nur profilierte Semantik

- `ScenarioCondition(kind=spatial)` bleibt ohne eigenes Raumprofil
  DFMLDS-spezifisch.
- Stochastische `Probability` wird nicht automatisch zu einer Quantification;
  dafuer fehlen in Annex C eine DFMLDS-spezifische Wahrscheinlichkeitssemantik
  und gegebenenfalls Operanden.
- `ParallelGroup` ist keine Annex-C-Metaklasse und wird nie direkt als
  `LogicalPath` typisiert.
- `RuntimeBinding` und `RuntimeAction` sind keine `FunctionConnector`- oder
  Annex-C-Transformationen. Eine Abbildung braucht eine explizite
  Verhaltensbeschreibung, nicht nur einen technischen Locator.
- `ValidationCase` bleibt V&V. Nur sein fachlicher erwarteter Zustand kann ueber
  eine StateAssertion mit Annex-C-Quantifications/States korrespondieren.

## Modellbeleg

Die kanonische V2-Modellquelle
`tools/dynamic_functional_mlds_v2_model.py` enthaelt:

- `DFMLDS::V2::AnnexCBridge::ScenarioAnnexMapping -> Relationship` mit den
  optionalen Quellrollen `scenarioStep`, `stepRelation`, `scenarioEvent` und
  `stateAssertion` sowie `annexElement [1..*]`;
- die exakten Annex-C-Assoziationen `LogicalPath.segment`,
  `LogicalPath.strand`, `LogicalPath.transformationOccurrence`,
  `TransformationOccurrence.invokedLogicalTransformation` und
  `TransitionEvent.occurredExecutionEvent`;
- `BehaviorConstraintTargetBinding -> Relationship` mit
  `behaviorConstraintType [1]`, `targetedVehicleFeature[*]`,
  `constrainedModeBehavior[*]`, `targetedFunctionType[*]`,
  `constrainedFunctionBehavior[*]` und `constrainedFunctionTriggering[*]`;
- die Invarianten `INV-049` bis `INV-051` fuer die Event-Typgrenze und den
  optionalen/preliminary Status sowie `INV-055` fuer das notwendige fachliche
  Target eines `BehaviorConstraintType`.

Dieses Dokument beschreibt die zulaessige Semantik; es behauptet fuer sich
allein weder die Ausfuehrung einer Projektion noch einen Abnahmestatus.
