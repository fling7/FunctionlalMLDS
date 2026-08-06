# DFMLDS V2 - Nichtregressionsmatrix

Stand: 2026-07-14

## Leseregel

Diese Matrix beschreibt fuer jede bestehende Vertragsfaehigkeit den fachlichen
V2-Pfad und die verlustfreie v0.5-Rueckprojektion. Ein Eintrag in dieser Matrix
ist ein Modell- und Zuordnungsbeleg, aber fuer sich allein kein ausgefuehrter
Test. Der maschinelle Gesamtstatus wird ausschliesslich aus
`acceptance_report.json` uebernommen.

Gemeinsamer Rueckprojektionsmechanismus fuer alle Zeilen:

```text
v0.5 JSON
  -> V2 semantic projection + V05ProjectionLedger
  -> fail-closed export
  -> struktur- und reihenfolgeidentische v0.5-JSON-Bedeutung
```

Der Ledger bewahrt insbesondere Feldpraesenz, `null`, leere Container,
Reihenfolgen, IDs, Enum-Lexeme, rohe `stepNumber`-/`level`-Werte, Locator-Slots
und Agent-/Entity-Aliasse. Dadurch werden nicht eindeutig ableitbare
Runtime-Details nicht aus dem V2-Fachmodell erraten.

## Die zehn urspruenglichen Vertragsfaehigkeiten

| ID | Vertragsfaehigkeit | V2-Modellpfad | v0.5-Rueckprojektion | Nachweisanker |
|---|---|---|---|---|
| NR-01 | Requirements und Use Cases mit `Satisfy`, `Include`, `Extend` und `ExtensionPoint` | `DynamicFunctionalModel -> RequirementsModel`; `RequirementsModel.requirement[*]` und `useCase[*]`; unveraenderte EAST-ADL-Beziehungen `Satisfy`, `Include`, `Extend`; bedingte Erweiterung separat als `ConditionalExtend -> Extend` | `requirementsModel.requirements`, `requirementsModel.useCases`, `includes`, `extends`, `extensionPoints`, `satisfyRelationships`; IDs, Container- und Relationsreihenfolge bleiben im Projektionspayload/Ledger | `v05_compatibility_mapping.md`; EAST-Abgleich `east_adl_conformance_matrix.md` |
| NR-02 | Main-, Alternativ- und Exception-Szenarien mit Schritten, Triggern, Guards, Zustaenden, lokalen Verzweigungen und Parallelgruppen | `UseCaseScenarioSpecification -> Relationship` verbindet `UseCase` und `Scenario`; `Scenario.step[*]`, `stepRelation[*]`, `parallelGroup[*]`; `ScenarioStep.triggeredBy`, `guard`, `resultingAssertion`; `variantOf` trennt Ablaufvariante von lokaler Verzweigung. StepRelation ist alleinige Ablaufsemantik | Verschachtelte `useCases[].scenarios[]`-Sicht, `kind`, `steps`, `stepRelations`, `parallelGroups`, `triggeredBy`, `guard`, `resultingState`; StateAssertions bilden die kompatible Teilmenge. Listenfolge, `stepNumber` und nicht normative Legacy-Probability-Werte bleiben exakt im Ledger | Mappingzeilen fuer `UseCaseScenarioSpecification`, `Scenario`, `ScenarioStep`, `StepRelation`, `ParallelGroup` |
| NR-03 | Trennung von Actor-Rolle, konkreter Entity und Agent | `Actor` bleibt Rolle; `Entity` ist konkreter Ausfuehrer; `Agent -> Entity`; `ActorParticipation -> Relationship`; `Entity.playsActor[*]`; `ScenarioStep.actorRole[*]` und `ScenarioStep.performedBy[*]` sind getrennte Rollen | `actors[]`, `entities[]`, `agents[]`, `actor_ids` und `playsActor` bleiben getrennt. Das Legacy-Feld `steps[].performedBy` enthaelt Actor-IDs und wird deshalb auf `ScenarioStep.actorRole` projiziert; AG-, ENT-AGENT- und Source-Agent-IDs bleiben getrennte Aliasse im Ledger | Mappingzeilen fuer `ActorParticipation`, `Entity`, `Agent`; `V05ProjectionLedger.agentAliases` |
| NR-04 | Fachlich-technische Kette Schritt -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction | `ScenarioStep.capabilityUse[*] -> CapabilityUse.type:Capability`; optionaler Core-Provider bzw. verpflichtender executable-Provider ordnet die konkrete Entity zu; `target[*]` benennt Interaktionsobjekte; `RuntimeBinding.capability`; `runtimeAction[1..*] {ordered}` | `steps[].capabilityUseIds`, `capabilityUses[].capability_id`, `runtimeBindings[].capability_id`, `runtimeActions[]`; Provider/Targets werden aus Legacy-Daten nicht geraten. Die Legacy-Top-Level-Liste bleibt mit Ledger-Reihenfolge erhalten | Mappingzeilen fuer `ScenarioStep`, `CapabilityUse`, `Capability`, `RuntimeBinding`, `RuntimeAction`; `INV-064`/`INV-065` |
| NR-05 | Mindestens ein beobachtbarer Effect je Capability und pruefbare Spezifikation durch Assertions | `Capability.effect[1..*] -> Effect`; `Effect.specifiedBy[1..*] -> Assertion`; State-, Event-, Output-, Grounding- und RelationAssertion sind zulaessig; Schrittresultat ueber `ScenarioStep.resultingAssertion[*]` | Legacy-`evidencedBy`, `stateAssertions[]` und `steps[].resultingState` werden auf StateAssertion als kompatible Assertion-Teilmenge projiziert; Feldname, leere/fehlende Werte und Reihenfolge bleiben im v0.5-Payload/Ledger | Mappingzeilen fuer `Capability.effect`, `Effect.specifiedBy`, `Assertion`/`StateAssertion`; `INV-023`, `INV-066` |
| NR-06 | Mehrere RuntimeBindings je Capability und mindestens eine geordnete RuntimeAction je Binding | `Capability <- RuntimeBinding.capability`; mehrere Bindings sind zulaessig; `RuntimeBinding.runtimeAction[1..*] {ordered}` | `runtimeBindings[]` bleibt geordnet; mehrere Eintraege mit derselben `capability_id` und jede `runtimeActions[]`-Reihenfolge werden unveraendert exportiert | Mappingzeilen fuer `RuntimeBinding`; V2-Multiplizitaet und Runtime-Invarianten |
| NR-07 | ValidationCases mit Stimuli, erwarteten Ergebnissen, Requirement-Trace und pruefbaren RuntimeBindings | `VerificationValidation.vvCase[*] -> ValidationCase -> VVCase`; Procedure/Stimulus; `AssertionOutcome`; `vvSubject[*]`; `RuntimeValidationTarget(platform,runtimeBinding,environmentRef)` ueber `vvTarget`; Verify und separater UseCase-Binding | `stimulus_ids`, `expectedOutcome`, `runtime_binding_ids`, Requirement-/UseCase-Referenzen bleiben erhalten. RuntimeTargets werden deterministisch aus expliziten Binding-IDs/Platform erzeugt; `level` bleibt Legacy-Lexem im Ledger | Mappingzeilen fuer ValidationCase und Runtime-V&V; EAST-V&V-Matrix; `INV-069`/`INV-070` |
| NR-08 | ScenarioSteps besitzen keine direkte RuntimeAction-Referenz | Erlaubter Pfad ist ausschliesslich `ScenarioStep -> CapabilityUse -> Capability <- RuntimeBinding -> RuntimeAction`; im Modell existiert keine `ScenarioStep.runtimeAction`-Assoziation | v0.5 besitzt nur `capabilityUseIds` am Schritt; Export fuegt kein `runtimeActionId` am Schritt hinzu | Kanonische Modellquelle und negative Invariantenfixture; v0.5-Feldoberflaeche |
| NR-09 | Agent-Grounding, Raumwissen, Antwort- und Handoff-Faehigkeit bleiben modellierbar | `Agent -> Entity`; kanonische Rollen `Entity.providedCapability[*]`, `Agent.responsibleZone[*]`, `groundedAsset[*]`, `groundedObjectGroup[*]` und `handoffTarget[*]`; Attribute `expertise[*]` und `knowledgeTag[*]` sind geordnet. `AgentKnowledgeBinding` ist nur die optionale Erweiterung fuer Wissen, Quelle, Berechtigungen und Provenienz | Alle 21 Agent-Felder, einschliesslich paralleler Source-/Entity-ID-Felder, werden gemaess der folgenden Feldtabelle semantisch oder ueber den Alias-Ledger erhalten | Vollstaendige Agent-Zeilen in `v05_compatibility_mapping.md`; Agent-Alias-Nachweis im Roundtrip-Report |
| NR-10 | Jede bestehende v0.5-Instanz ist verlustfrei in V2 repraesentierbar | `DynamicFunctionalModel` plus semantische V2-Projektion; nicht fachlich ableitbare Serialisierungsdetails liegen ausserhalb des Fachmodells im `V05ProjectionLedger` | Verbindliches Gesetz `exportV05(importV05(x)) == x`; 173/173 deklarierte Struktur- und Blattpfade haben ein maschinell aufgeloestes Ziel; sieben reale Fixtures sind strukturell und in ihrer Objekt-/Arrayreihenfolge gleich rueckprojiziert; V2-only-Inhalte bleiben fail-closed | `v05_roundtrip_report.json`, `v05_field_coverage.json`, `v05_compatibility_mapping.json` |

## Vollstaendige Agent-/Entity-Feldoberflaeche

Die folgenden Tabellen machen die in NR-03 und NR-09 zusammengefasste
Kompatibilitaetsgrenze explizit. `shortName` und alle fachlichen Zielrollen
liegen im kanonischen Modell; reine Source-Aliasse und die separate Legacy-ID
bleiben im `V05ProjectionLedger`.

### Entity-Felder

| v0.5-Feld | V2-Ziel |
|---|---|
| `id` | `Entity.shortName` |
| `name` | `Entity.name` |
| `kind` | `Entity.kind` |
| `source_id` | `Entity.sourceId` |
| `entityRole` | `Entity.entityRole` |
| `source_object_ids` | `Entity.sourceObjectId[*] {ordered}` |
| `purpose` | `Entity.purpose` |
| `source_group` | `Entity.sourceGroup` |
| `object_type` | `Entity.objectType` |
| `object_group_entity_id` | `Entity.objectGroup` |

### Agent-Felder

| v0.5-Feld | V2-Ziel |
|---|---|
| `id` | `V05ProjectionLedger.agentAliases.agentId` |
| `source_agent_id` | `Agent.sourceAgentId` |
| `entity_id` | `Agent.shortName`; Originalpraesenz und Alias bleiben im Ledger |
| `playsActor` | geerbtes `Entity.playsActor[*]` |
| `providedCapabilityIds` | geerbtes `Entity.providedCapability[*]` |
| `display_name` | `Agent.displayName` |
| `persona` | `Agent.persona` |
| `expertise` | `Agent.expertise[*] {ordered}` |
| `knowledge_tags` | `Agent.knowledgeTag[*] {ordered}` |
| `voice` | `Agent.voice` |
| `voice_gender` | `Agent.voiceGender` |
| `voice_style` | `Agent.voiceStyle` |
| `tts_model` | `Agent.ttsModel` |
| `responsible_zone_ids` | `V05ProjectionLedger.agentAliases.responsibleZone.source[*]` |
| `responsibleZoneEntityIds` | `Agent.responsibleZone[*]` |
| `grounded_object_ids` | `V05ProjectionLedger.agentAliases.groundedAsset.source[*]` |
| `groundedAssetEntityIds` | `Agent.groundedAsset[*]` |
| `grounded_object_groups` | `V05ProjectionLedger.agentAliases.groundedObjectGroup.source[*]` |
| `groundedObjectGroupEntityIds` | `Agent.groundedObjectGroup[*]` |
| `handoff_targets` | `V05ProjectionLedger.agentAliases.handoffTarget.source[*]` |
| `handoffTargetAgentIds` | `Agent.handoffTarget[*]` |

`AgentKnowledgeBinding` ersetzt keine dieser Legacy-Kernrollen. Es kann in
einem explizit aktivierten Knowledge-Profil zusaetzlich `knowledgeItem`,
`source`, Berechtigungen und Provenienz ausdruecken.

## Explizite Runtime-Vertraege

| ID | Vertrag | V2-Modellpfad | v0.5-Rueckprojektion | Nachweisanker |
|---|---|---|---|---|
| NR-11 | Answer-Capability | `ScenarioStep(S11) -> CapabilityUse -> Capability(Answer Room Grounded Question) -> Effect -> GroundingAssertion/OutputAssertion` ist neu ausdrueckbar; bestehende StateAssertions bleiben gueltig. Bereitstellung ueber Entity/Agent, Runtime ueber RuntimeBinding | Bestehende IDs mit S11-/ANSWER-Suffix, `providedCapabilityIds`, Capability-Text/Effects/Legacy-evidencedBy und Binding werden unveraendert exportiert | Reale v0.5-Fixtures; Mapping- und Roundtrip-Report |
| NR-12 | Agent-Handoff | `ScenarioEvent(HANDOFF_NEEDED)` und `ScenarioCondition(HANDOFF_TARGET_AVAILABLE)` steuern `ScenarioStep(S12) -> CapabilityUse -> Capability(Handoff)`; `Agent.handoffTarget[*]`; Effect/StateAssertion belegen Zielgueltigkeit | S12-/HANDOFF-IDs, `handoff_targets`, `handoffTargetAgentIds`, Event, Guard, Capability, RuntimeBinding und erwartete StateAssertion bleiben erhalten | Reale v0.5-Fixtures; Alias-Ledger; Runtime-Trace-Nachweis |
| NR-13 | Backend-Locator `POST /chat` fuer Answer und Handoff | Je Capability ein `RuntimeBinding`; darin geordnete `RuntimeAction`; genau ein `RuntimeActionLocator(kind=endpoint, value="POST /chat")` pro Aktion im V2-Runtimeprofil | Der Legacy-Slot `endpoint: "POST /chat"` wird im `V05ProjectionLedger.runtimeActionLocatorSlots.endpoint` wortgetreu erhalten; `tool`/`topic`, `null` und Feldpraesenz bleiben getrennt | v0.5-Fixtures; Mappingzeilen fuer Locator-Slots; Backend-Smoke im Acceptance-Report |
| NR-14 | Runtime-Trace von Schritt bis Aktion | Aufloesung ueber stabile `shortName`-/ID-Aliasse entlang `ScenarioStep -> CapabilityUse -> Capability <- RuntimeBinding -> RuntimeAction`; keine direkte Abkuerzung im Modell | Runtime-Trace-Felder `scenario_step_id`, `capability_use_ids`, `capability_id`, `runtime_binding_id`, `runtime_action_id` werden gegen die unveraenderte v0.5-Sicht aufgeloest | `runtime_trace_nonregression.json`; Trace-Maps; NR-08 |
| NR-15 | Validation-Ausdrucksfaehigkeit einschliesslich strukturiertem Soll-/Ist-Ergebnis | `AssertionOutcome -> VVIntendedOutcome` referenziert Assertions; `RuntimeActualOutcome -> VVActualOutcome` besitzt `AssertionResult[1..*]` mit Verdict, observedValue, evidenceRef und timestamp; vvSubject und RuntimeValidationTarget/VVTarget.element bleiben getrennt | Legacy-Felder `level`, `stimulus_ids`, `runtime_binding_ids`, `expectedOutcome`, Requirement- und UseCase-Referenzen werden erhalten; v0.5 erfindet keine ActualOutcome-Logs oder Resultate | EAST-V&V-Matrix; Mappingzeilen; positive/negative V2-Invariantenfixtures |

## Ausgefuehrter Abnahmestand

Die folgenden Artefakte liegen vor und wurden im Gesamtbericht auf demselben
Modellstand ausgewertet:

- `output/metamodel_v2/evidence/acceptance_report.json`
- `output/metamodel_v2/evidence/v05_roundtrip_report.json`
- `output/metamodel_v2/evidence/v05_field_coverage.json`
- `output/metamodel_v2/evidence/runtime_trace_nonregression.json`
- `output/metamodel_v2/evidence/implementation_hash_verification.json`
- die positiven und negativen V2-Invariantenfixtures

`acceptance_report.json` meldet `status: pass`. Konkret belegen die
maschinenlesbaren Teilberichte:

- sieben von sieben reale v0.5-Instanzen strukturell und in Objekt-/Arrayfolge
  gleich rueckprojiziert;
- 173 von 173 Feldpfade abgedeckt und zielaufgeloest, ohne fehlende oder
  unaufgeloeste Ziele;
- drei Runtime-Logs mit mindestens 260 Ereignissen; alle im finalen Report
  gezaehlten Referenzen sind aufgeloest;
- 1.715 eingefrorene Implementierungsdateien mit 2.449.211.010 geprueften
  Bytes, ohne fehlende Datei, Groessen- oder Hashabweichung;
- 118 Klassen, 157 Assoziationen, 74 Invarianten und acht Sichten in allen
  drei Diagrammformaten konsistent;
- 27 Generatorartefakte in zwei Laeufen hashidentisch;
- 18 von 18 Modellpruefkategorien, 13 von 13 Instanzpruefkategorien sowie 17 von 17 Full-Surface-Anforderungen
  ohne Fehler oder Warnung bestanden.

Die Markdown-Matrix referenziert diese Laufzeitnachweise; der verbindliche
Gesamtstatus bleibt der maschinenlesbare Acceptance-Report.
