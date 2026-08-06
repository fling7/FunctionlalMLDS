# Anwendungsfall A: RuntimeAction-Instanzen

Stand: 2026-07-07

Task: 4.14 `RuntimeAction-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Eine `RuntimeAction` ist die konkrete technische Einzelaktion innerhalb genau einer `RuntimeBinding`. Sie ist der Ort fuer technische Endpoints, Topics, Tools sowie optionale Input- und Output-Schemas.

Fuer Anwendungsfall A gilt:

- Jede `RuntimeAction` gehoert genau zu einer `RuntimeBinding`.
- Jede `RuntimeBinding` besitzt mindestens eine `RuntimeAction`.
- `ScenarioStep`, `CapabilityUse`, `Capability` und `Effect` referenzieren keine RuntimeAction direkt.
- Die technischen Namen in diesem Dokument sind generische Schnittstellennamen fuer `GenericVRSceneRuntime`; sie sind keine Implementierung und kein Code.
- Die fachlichen Effects werden nicht von RuntimeActions besessen. Sie werden nur als Trace genutzt, um zu zeigen, welche beobachtbare Wirkung durch die technische Ausfuehrung unterstuetzt wird.

Der erlaubte Trace bleibt:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Angelegte RuntimeAction-Instanzen

| RuntimeAction-ID | Owner-RuntimeBinding | Aktionstyp | Technischer Endpoint | `inputSchema` | `outputSchema` | Technischer Zweck | Unterstuetzter Effect-Trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `A-RA-ROLE-SET` | `A-RB-ROLE-EXECUTOR-VR` | `endpoint` | `GenericVRSceneRuntime.AgentRole.setRole` | `Schema.AgentRoleCommand` | `Schema.ActionReceipt` | Setzt fuer den Agenten den technischen Rollenzustand auf `executor`. | `A-EFF-ROLE-EXECUTOR` |
| `A-RA-ROLE-SYNC` | `A-RB-ROLE-EXECUTOR-VR` | `endpoint` | `GenericVRSceneRuntime.AgentState.syncRoleState` | `Schema.AgentStateSyncRequest` | `Schema.AgentStateSnapshot` | Synchronisiert den sichtbaren Agentenzustand nach dem Rollenwechsel. | `A-EFF-ROLE-EXECUTOR`; `A-EFF-AGENT-ACTING` |
| `A-RA-TARGET-ACTION-REQUEST` | `A-RB-TARGET-ACTION-VR` | `endpoint` | `GenericVRSceneRuntime.AgentMotion.requestTargetAction` | `Schema.TargetActionCommand` | `Schema.MotionPlanReceipt` | Fordert die zielgerichtete Agentenhandlung in Richtung Zielzone an. | `A-EFF-AGENT-MOVING-TO-TARGET` |
| `A-RA-TARGET-OCCUPANCY-SYNC` | `A-RB-TARGET-ACTION-VR` | `endpoint` | `GenericVRSceneRuntime.ZoneState.syncOccupancy` | `Schema.ZoneOccupancySyncRequest` | `Schema.ZoneStateSnapshot` | Synchronisiert die Belegung der Zielzone nach der Agentenhandlung. | `A-EFF-TARGET-OCCUPIED` |
| `A-RA-BLOCK-PROGRESS-HOLD` | `A-RB-BLOCKED-PROGRESS-VR` | `endpoint` | `GenericVRSceneRuntime.AgentMotion.holdProgress` | `Schema.BlockedProgressCommand` | `Schema.ActionReceipt` | Haelt den Agenten technisch im sicheren Wartezustand, wenn der Zielpfad blockiert ist. | `A-EFF-AGENT-WAITING` |
| `A-RA-BLOCK-STATE-SYNC` | `A-RB-BLOCKED-PROGRESS-VR` | `endpoint` | `GenericVRSceneRuntime.AgentState.syncBlockedRoleState` | `Schema.AgentBlockedStateSyncRequest` | `Schema.AgentStateSnapshot` | Synchronisiert den blockierten Rollenzustand des Agenten. | `A-EFF-ROLE-BLOCKED` |

## Komposition unter RuntimeBindings

| RuntimeBinding-ID | Enthaltene RuntimeActions | Anzahl | Kardinalitaetsbewertung |
| --- | --- | ---: | --- |
| `A-RB-ROLE-EXECUTOR-VR` | `A-RA-ROLE-SET`; `A-RA-ROLE-SYNC` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `A-RB-TARGET-ACTION-VR` | `A-RA-TARGET-ACTION-REQUEST`; `A-RA-TARGET-OCCUPANCY-SYNC` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-RA-BLOCK-PROGRESS-HOLD`; `A-RA-BLOCK-STATE-SYNC` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |

## Ausfuehrungsreihenfolge innerhalb der Bindings

Die Reihenfolge ist keine eigene Metamodellkante. Sie wird hier als technische Ausfuehrungshinweis dokumentiert, damit spaetere ValidationCases eindeutige Stimuli und erwartete Outcomes formulieren koennen.

| RuntimeBinding-ID | Empfohlene Reihenfolge | Begruendung |
| --- | --- | --- |
| `A-RB-ROLE-EXECUTOR-VR` | `A-RA-ROLE-SET` vor `A-RA-ROLE-SYNC` | Der Zustand kann erst synchronisiert werden, nachdem der Rollenwechsel technisch angenommen wurde. |
| `A-RB-TARGET-ACTION-VR` | `A-RA-TARGET-ACTION-REQUEST` vor `A-RA-TARGET-OCCUPANCY-SYNC` | Die Zielzonenbelegung ist Folge der angeforderten Agentenhandlung. |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-RA-BLOCK-PROGRESS-HOLD` vor `A-RA-BLOCK-STATE-SYNC` | Der sichere Wartezustand muss gesetzt sein, bevor der blockierte Rollenstatus synchronisiert wird. |

## Technische Schemas

Die folgenden Schemas sind als kompakte technische Schnittstellenbeschreibung zu lesen. Sie sind keine eigenen Metamodellklassen in diesem Artefakt, sondern Werte der optionalen `inputSchema`- und `outputSchema`-Attribute der RuntimeActions.

| Schema-ID | Richtung | Pflichtfelder |
| --- | --- | --- |
| `Schema.AgentRoleCommand` | input | `sceneId: Identifier`; `agentId: Identifier`; `targetRole: String`; `correlationId: Identifier` |
| `Schema.AgentStateSyncRequest` | input | `sceneId: Identifier`; `agentId: Identifier`; `expectedRole: String`; `correlationId: Identifier` |
| `Schema.TargetActionCommand` | input | `sceneId: Identifier`; `agentId: Identifier`; `targetZoneId: Identifier`; `obstacleRegionId: Identifier`; `correlationId: Identifier` |
| `Schema.ZoneOccupancySyncRequest` | input | `sceneId: Identifier`; `targetZoneId: Identifier`; `agentId: Identifier`; `correlationId: Identifier` |
| `Schema.BlockedProgressCommand` | input | `sceneId: Identifier`; `agentId: Identifier`; `targetZoneId: Identifier`; `obstacleRegionId: Identifier`; `reasonCode: String`; `correlationId: Identifier` |
| `Schema.AgentBlockedStateSyncRequest` | input | `sceneId: Identifier`; `agentId: Identifier`; `targetZoneId: Identifier`; `obstacleRegionId: Identifier`; `correlationId: Identifier` |
| `Schema.ActionReceipt` | output | `actionId: Identifier`; `accepted: boolean`; `message: String`; `correlationId: Identifier` |
| `Schema.AgentStateSnapshot` | output | `sceneId: Identifier`; `agentId: Identifier`; `roleState: String`; `activityState: String`; `timestamp: String`; `correlationId: Identifier` |
| `Schema.MotionPlanReceipt` | output | `actionId: Identifier`; `accepted: boolean`; `targetZoneId: Identifier`; `reason: String`; `correlationId: Identifier` |
| `Schema.ZoneStateSnapshot` | output | `sceneId: Identifier`; `targetZoneId: Identifier`; `occupancyState: String`; `occupantId: Identifier [0..1]`; `timestamp: String`; `correlationId: Identifier` |

## Trace auf fachliche Effects und StateAssertions

Diese Tabelle ist eine Rueckverfolgbarkeitshilfe. Sie bedeutet nicht, dass RuntimeActions Effects besitzen. Fachlich gehoeren Effects weiterhin zur Capability; technisch werden sie durch RuntimeBindings und RuntimeActions realisierbar gemacht.

| RuntimeAction-ID | Effect-Trace | StateAssertion-Trace | Pruefidee fuer spaetere ValidationCases |
| --- | --- | --- | --- |
| `A-RA-ROLE-SET` | `A-EFF-ROLE-EXECUTOR` | `A-SA-S05-01` | Nach erfolgreichem Receipt muss `roleState=executor` beobachtbar werden. |
| `A-RA-ROLE-SYNC` | `A-EFF-ROLE-EXECUTOR`; `A-EFF-AGENT-ACTING` | `A-SA-S05-01`; `A-SA-S05-02` | Snapshot muss `roleState=executor` und einen aktiven Agentenzustand bestaetigen. |
| `A-RA-TARGET-ACTION-REQUEST` | `A-EFF-AGENT-MOVING-TO-TARGET` | `A-SA-S06-01` | Receipt muss die Zielhandlung akzeptieren und den Zielbereich referenzieren. |
| `A-RA-TARGET-OCCUPANCY-SYNC` | `A-EFF-TARGET-OCCUPIED` | `A-SA-S06-02` | Zonensnapshot muss `occupancyState=occupied` fuer `TargetZone` zeigen. |
| `A-RA-BLOCK-PROGRESS-HOLD` | `A-EFF-AGENT-WAITING` | `A-EX-SA03` | Receipt muss bestaetigen, dass der Agentenfortschritt gehalten wird. |
| `A-RA-BLOCK-STATE-SYNC` | `A-EFF-ROLE-BLOCKED` | `A-EX-SA04` | Snapshot muss `roleState=blocked` fuer `AgentBody` zeigen. |

## Keine verbotene Direktreferenz

| Pruefpunkt | Ergebnis |
| --- | --- |
| RuntimeActions liegen nur unter RuntimeBindings | ja |
| ScenarioSteps referenzieren RuntimeActions direkt | nein |
| CapabilityUses referenzieren RuntimeActions direkt | nein |
| Capabilities enthalten Endpoint-Daten | nein |
| RuntimeActions enthalten technische Endpoint- und Schema-Daten | ja, hier ist das erlaubt und beabsichtigt. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.14 | Folgetask |
| --- | --- | --- |
| `ValidationCase` | nicht angelegt | 4.15 |
| Finale Kardinalitaetspruefung | vorbereitet | 4.16 |
| Finale Invariantenpruefung | vorbereitet | 4.17 |

## Abnahmekontrolle

| Kriterium aus Task 4.14 | Erfuellung |
| --- | --- |
| Technische Aktionen angelegt | Sechs RuntimeActions sind formal angelegt. |
| Jede RuntimeBinding besitzt mindestens eine RuntimeAction | Jede der drei RuntimeBindings besitzt zwei RuntimeActions. |
| Jede RuntimeAction hat genau einen Owner | Jede RuntimeAction ist genau einer RuntimeBinding zugeordnet. |
| Input- und Output-Schemas dokumentiert | Jede RuntimeAction referenziert genau ein Input- und ein Output-Schema. |
| Technische Details liegen nur auf RuntimeAction-Ebene | Endpoints und Schemas stehen nur in diesem RuntimeAction-Artefakt. |

## Konsequenz fuer Task 4.15

Task 4.15 kann nun `ValidationCase`-Instanzen anlegen. Diese koennen Stimuli aus Szenario, RuntimeBinding und RuntimeAction verwenden und muessen mindestens ein erwartetes Outcome besitzen.
