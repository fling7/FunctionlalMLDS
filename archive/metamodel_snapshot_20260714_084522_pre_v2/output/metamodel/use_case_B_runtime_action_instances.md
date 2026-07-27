# Anwendungsfall B: RuntimeAction-Instanzen

Stand: 2026-07-07

Task: 8.11 `RuntimeActions fuer technische Ausfuehrung anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Eine `RuntimeAction` ist die konkrete technische Einzelaktion innerhalb genau einer `RuntimeBinding`. Sie ist der Ort fuer technische Endpoints, Topics, Tools sowie optionale Input- und Output-Schemas.

Fuer Anwendungsfall B gilt:

- Jede `RuntimeAction` gehoert genau zu einer `RuntimeBinding`.
- Jede `RuntimeBinding` besitzt mindestens eine `RuntimeAction`.
- `ScenarioStep`, `CapabilityUse`, `Capability` und `Effect` referenzieren keine RuntimeAction direkt.
- Die technischen Namen in diesem Dokument sind generische Schnittstellennamen fuer Vivian-, VR-, Kaffeemaschinenadapter- und Trace-Runtimes.
- Die Namen sind keine Implementierung, kein Code und keine Festlegung auf eine konkrete Engine, LLM-, Voice-, Avatar- oder Maschinenplattform.
- Die fachlichen Effects werden nicht von RuntimeActions besessen. Sie werden nur als Trace genutzt, um zu zeigen, welche beobachtbare Wirkung durch die technische Ausfuehrung unterstuetzt wird.

Der erlaubte Trace bleibt:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Angelegte RuntimeAction-Instanzen

| RuntimeAction-ID | Owner-RuntimeBinding | Aktionstyp | Technischer Endpoint oder Topic | `inputSchema` | `outputSchema` | Technischer Zweck | Unterstuetzter Effect-Trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `B-RA-VIVIAN-SET-GUIDANCE-MODE` | `B-RB-VIVIAN-GUIDANCE-MODE` | `endpoint` | `VivianAssistantRuntime.Mode.setGuidanceMode` | `Schema.VivianModeCommand` | `Schema.ActionReceipt` | Setzt Vivians technischen Assistenzmodus fuer die Bedienfuehrung. | `B-EFF-VIVIAN-GUIDING` |
| `B-RA-VR-SYNC-ASSISTANT-STATE` | `B-RB-VIVIAN-GUIDANCE-MODE` | `endpoint` | `VRInteractionRuntime.AssistantState.sync` | `Schema.AssistantStateSyncRequest` | `Schema.AssistantStateSnapshot` | Synchronisiert Vivians sichtbaren oder hoerbaren Szenenzustand. | `B-EFF-VIVIAN-GUIDING` |
| `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE` | `B-RB-VIVIAN-CUP-GUIDANCE` | `endpoint` | `VivianAssistantRuntime.Guidance.composeCupPlacement` | `Schema.GuidanceCompositionRequest` | `Schema.AssistantContentDraft` | Erzeugt den technischen Inhalt fuer den Tassenplatzierungshinweis. | `B-EFF-CUP-GUIDANCE-ISSUED` |
| `B-RA-VR-PRESENT-CUP-GUIDANCE` | `B-RB-VIVIAN-CUP-GUIDANCE` | `endpoint` | `VRInteractionRuntime.Guidance.presentCupPlacement` | `Schema.GuidancePresentationRequest` | `Schema.ScenePresentationReceipt` | Praesentiert den Tassenhinweis in der virtuellen Szene. | `B-EFF-CUP-GUIDANCE-ISSUED` |
| `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE` | `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `endpoint` | `VivianAssistantRuntime.Guidance.composeProgramSelection` | `Schema.GuidanceCompositionRequest` | `Schema.AssistantContentDraft` | Erzeugt den technischen Inhalt fuer den Programmauswahlhinweis. | `B-EFF-PROGRAM-GUIDANCE-ISSUED` |
| `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `endpoint` | `VRInteractionRuntime.Guidance.presentProgramSelection` | `Schema.GuidancePresentationRequest` | `Schema.ScenePresentationReceipt` | Praesentiert den Programmauswahlhinweis in der virtuellen Szene. | `B-EFF-PROGRAM-GUIDANCE-ISSUED` |
| `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST` | `B-RB-VIVIAN-REQUEST-CONFIRMED` | `endpoint` | `VivianAssistantRuntime.Feedback.confirmBrewingRequest` | `Schema.RequestFeedbackCommand` | `Schema.ActionReceipt` | Gibt Vivians technische Rueckmeldung zur erkannten Bruehanforderung aus. | `B-EFF-BREWING-REQUEST-CONFIRMED` |
| `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | `B-RB-VIVIAN-REQUEST-CONFIRMED` | `topic` | `FunctionalMLDSTraceRuntime.Trace.requestFeedbackObserved` | `Schema.TraceFeedbackEvent` | `Schema.TraceReceipt` | Synchronisiert die Request-Bestaetigung mit dem Ausfuehrungstrace. | `B-EFF-BREWING-REQUEST-CONFIRMED` |
| `B-RA-CM-EVALUATE-READINESS` | `B-RB-COFFEE-READINESS-CHECK` | `endpoint` | `CoffeeMachineAdapterRuntime.Readiness.evaluate` | `Schema.ReadinessEvaluationRequest` | `Schema.ReadinessResult` | Ermittelt technisch das Bereitschaftsergebnis der Kaffeemaschine. | `B-EFF-READINESS-RESULT-PRODUCED` |
| `B-RA-CM-SYNC-READINESS-RESULT` | `B-RB-COFFEE-READINESS-CHECK` | `endpoint` | `CoffeeMachineAdapterRuntime.State.syncReadinessResult` | `Schema.ReadinessStateSyncRequest` | `Schema.MachineStateSnapshot` | Synchronisiert Bereitschaft, Startfreigabe oder Startblockade am Maschinenzustand. | `B-EFF-READINESS-RESULT-PRODUCED` |
| `B-RA-TRACE-SYNC-READINESS-OUTCOME` | `B-RB-COFFEE-READINESS-CHECK` | `topic` | `FunctionalMLDSTraceRuntime.Trace.readinessOutcomeObserved` | `Schema.TraceReadinessOutcomeEvent` | `Schema.TraceReceipt` | Synchronisiert das positive oder negative Readiness-Outcome mit dem Trace. | `B-EFF-READINESS-RESULT-PRODUCED` |
| `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT` | `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `endpoint` | `VivianAssistantRuntime.Prompt.composeStartConfirmation` | `Schema.ConfirmationPromptRequest` | `Schema.AssistantContentDraft` | Erzeugt den technischen Inhalt der Startbestaetigungsfrage. | `B-EFF-CONFIRMATION-REQUESTED` |
| `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `endpoint` | `VRInteractionRuntime.Affordance.showConfirmation` | `Schema.ConfirmationAffordanceRequest` | `Schema.AffordanceReceipt` | Zeigt ein bestaetigbares Szenenangebot fuer die Benutzerfreigabe an. | `B-EFF-CONFIRMATION-REQUESTED` |
| `B-RA-CM-REQUEST-BREWING-START` | `B-RB-COFFEE-START-BREWING` | `endpoint` | `CoffeeMachineAdapterRuntime.Brewing.requestStart` | `Schema.BrewingStartCommand` | `Schema.BrewingStartReceipt` | Fordert den technischen Start des Bruehvorgangs an. | `B-EFF-BREWING-START-ISSUED` |
| `B-RA-CM-SYNC-BREWING-STATE` | `B-RB-COFFEE-START-BREWING` | `endpoint` | `CoffeeMachineAdapterRuntime.State.syncBrewingState` | `Schema.BrewingStateSyncRequest` | `Schema.MachineStateSnapshot` | Synchronisiert den beobachtbaren Bruehzustand der Kaffeemaschine. | `B-EFF-BREWING-START-ISSUED` |
| `B-RA-TRACE-SYNC-START-OUTCOME` | `B-RB-COFFEE-START-BREWING` | `topic` | `FunctionalMLDSTraceRuntime.Trace.startOutcomeObserved` | `Schema.TraceStartOutcomeEvent` | `Schema.TraceReceipt` | Synchronisiert den Startausgang mit dem Ausfuehrungstrace. | `B-EFF-BREWING-START-ISSUED` |
| `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT` | `B-RB-VIVIAN-COMPLETION-REPORT` | `endpoint` | `VivianAssistantRuntime.Report.composeCompletion` | `Schema.CompletionReportRequest` | `Schema.AssistantContentDraft` | Erzeugt den technischen Inhalt der Abschlussmeldung. | `B-EFF-COMPLETION-REPORTED` |
| `B-RA-VR-PRESENT-COMPLETION-REPORT` | `B-RB-VIVIAN-COMPLETION-REPORT` | `endpoint` | `VRInteractionRuntime.Report.presentCompletion` | `Schema.ReportPresentationRequest` | `Schema.ScenePresentationReceipt` | Praesentiert die Abschlussmeldung in der virtuellen Szene. | `B-EFF-COMPLETION-REPORTED` |
| `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION` | `B-RB-VIVIAN-CUP-CORRECTION` | `endpoint` | `VivianAssistantRuntime.Guidance.composeCupCorrection` | `Schema.CupCorrectionCompositionRequest` | `Schema.AssistantContentDraft` | Erzeugt den technischen Inhalt der Korrekturanleitung fuer die Tasse. | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` |
| `B-RA-VR-PRESENT-CUP-CORRECTION` | `B-RB-VIVIAN-CUP-CORRECTION` | `endpoint` | `VRInteractionRuntime.Guidance.presentCupCorrection` | `Schema.GuidancePresentationRequest` | `Schema.ScenePresentationReceipt` | Praesentiert die Korrekturanleitung in der virtuellen Szene. | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` |
| `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION` | `B-RB-VIVIAN-ERROR-EXPLANATION` | `endpoint` | `VivianAssistantRuntime.Explanation.composeReadinessError` | `Schema.ErrorExplanationRequest` | `Schema.AssistantContentDraft` | Erzeugt die technische Fehlererklaerung zur fehlgeschlagenen Bereitschaft. | `B-EFF-ERROR-EXPLAINED` |
| `B-RA-VR-PRESENT-ERROR-EXPLANATION` | `B-RB-VIVIAN-ERROR-EXPLANATION` | `endpoint` | `VRInteractionRuntime.Explanation.presentReadinessError` | `Schema.ErrorPresentationRequest` | `Schema.ScenePresentationReceipt` | Praesentiert die Fehlererklaerung in der virtuellen Szene. | `B-EFF-ERROR-EXPLAINED` |
| `B-RA-TRACE-SYNC-ERROR-OUTCOME` | `B-RB-VIVIAN-ERROR-EXPLANATION` | `topic` | `FunctionalMLDSTraceRuntime.Trace.errorOutcomeObserved` | `Schema.TraceErrorOutcomeEvent` | `Schema.TraceReceipt` | Synchronisiert Fehlerursache und blockierten Start mit dem Trace. | `B-EFF-ERROR-EXPLAINED` |
| `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK` | `B-RB-VIVIAN-EXCEPTION-CLOSE` | `endpoint` | `VivianAssistantRuntime.Exception.closeFeedback` | `Schema.ExceptionClosureFeedbackCommand` | `Schema.ActionReceipt` | Gibt das technische Feedback fuer den abgeschlossenen Exception-Pfad aus. | `B-EFF-EXCEPTION-CLOSED` |
| `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | `B-RB-VIVIAN-EXCEPTION-CLOSE` | `topic` | `FunctionalMLDSTraceRuntime.Trace.exceptionClosedObserved` | `Schema.TraceExceptionClosedEvent` | `Schema.TraceReceipt` | Synchronisiert den abgeschlossenen Exception-Pfad und die Nichtfortsetzung des Hauptpfads mit dem Trace. | `B-EFF-EXCEPTION-CLOSED` |

## Komposition unter RuntimeBindings

| RuntimeBinding-ID | Enthaltene RuntimeActions | Anzahl | Kardinalitaetsbewertung |
| --- | --- | ---: | --- |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `B-RA-VIVIAN-SET-GUIDANCE-MODE`; `B-RA-VR-SYNC-ASSISTANT-STATE` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`; `B-RA-VR-PRESENT-CUP-GUIDANCE` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE`; `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST`; `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-COFFEE-READINESS-CHECK` | `B-RA-CM-EVALUATE-READINESS`; `B-RA-CM-SYNC-READINESS-RESULT`; `B-RA-TRACE-SYNC-READINESS-OUTCOME` | 3 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT`; `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-COFFEE-START-BREWING` | `B-RA-CM-REQUEST-BREWING-START`; `B-RA-CM-SYNC-BREWING-STATE`; `B-RA-TRACE-SYNC-START-OUTCOME` | 3 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT`; `B-RA-VR-PRESENT-COMPLETION-REPORT` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-CUP-CORRECTION` | `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION`; `B-RA-VR-PRESENT-CUP-CORRECTION` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION`; `B-RA-VR-PRESENT-ERROR-EXPLANATION`; `B-RA-TRACE-SYNC-ERROR-OUTCOME` | 3 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK`; `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | 2 | gueltig: `RuntimeBinding -> RuntimeAction [1..*]` erfuellt. |

## Ausfuehrungsreihenfolge innerhalb der Bindings

Die Reihenfolge ist keine eigene Metamodellkante. Sie wird hier als technischer Ausfuehrungshinweis dokumentiert, damit spaetere ValidationCases eindeutige Stimuli und erwartete Outcomes formulieren koennen.

| RuntimeBinding-ID | Empfohlene Reihenfolge | Begruendung |
| --- | --- | --- |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `B-RA-VIVIAN-SET-GUIDANCE-MODE` vor `B-RA-VR-SYNC-ASSISTANT-STATE` | Der Assistenzmodus muss gesetzt sein, bevor der sichtbare Szenenzustand synchronisiert wird. |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE` vor `B-RA-VR-PRESENT-CUP-GUIDANCE` | Inhalt muss erzeugt sein, bevor er praesentiert wird. |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE` vor `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | Inhalt muss erzeugt sein, bevor er praesentiert wird. |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST` vor `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | Der Trace synchronisiert die bereits ausgegebene fachliche Rueckmeldung. |
| `B-RB-COFFEE-READINESS-CHECK` | `B-RA-CM-EVALUATE-READINESS` vor `B-RA-CM-SYNC-READINESS-RESULT` vor `B-RA-TRACE-SYNC-READINESS-OUTCOME` | Zuerst wird das Ergebnis ermittelt, dann der Maschinenzustand synchronisiert, dann der Trace aktualisiert. |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT` vor `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | Die Rueckfrage muss erzeugt sein, bevor die Bestaetigungsmoeglichkeit angezeigt wird. |
| `B-RB-COFFEE-START-BREWING` | `B-RA-CM-REQUEST-BREWING-START` vor `B-RA-CM-SYNC-BREWING-STATE` vor `B-RA-TRACE-SYNC-START-OUTCOME` | Der Start wird angefordert, dann wird der Bruehzustand synchronisiert, dann der Trace aktualisiert. |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT` vor `B-RA-VR-PRESENT-COMPLETION-REPORT` | Inhalt muss erzeugt sein, bevor er praesentiert wird. |
| `B-RB-VIVIAN-CUP-CORRECTION` | `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION` vor `B-RA-VR-PRESENT-CUP-CORRECTION` | Inhalt muss erzeugt sein, bevor er praesentiert wird. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION` vor `B-RA-VR-PRESENT-ERROR-EXPLANATION` vor `B-RA-TRACE-SYNC-ERROR-OUTCOME` | Die Fehlererklaerung wird erzeugt, praesentiert und anschliessend als Outcome synchronisiert. |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK` vor `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | Der Trace bestaetigt den abgeschlossenen Exception-Pfad nach der Rueckmeldung. |

## Technische Schemas

Die folgenden Schemas sind als kompakte technische Schnittstellenbeschreibung zu lesen. Sie sind keine eigenen Metamodellklassen in diesem Artefakt, sondern Werte der optionalen `inputSchema`- und `outputSchema`-Attribute der RuntimeActions.

| Schema-ID | Richtung | Pflichtfelder |
| --- | --- | --- |
| `Schema.VivianModeCommand` | input | `sceneId: Identifier`; `assistantId: Identifier`; `targetMode: String`; `reason: String`; `correlationId: Identifier` |
| `Schema.AssistantStateSyncRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `expectedMode: String`; `correlationId: Identifier` |
| `Schema.GuidanceCompositionRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `audienceActorId: Identifier`; `targetObjectId: Identifier`; `guidanceTopic: String`; `contextObjectId: Identifier [0..1]`; `correlationId: Identifier` |
| `Schema.GuidancePresentationRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `targetObjectId: Identifier`; `contentRef: Identifier`; `presentationMode: String`; `correlationId: Identifier` |
| `Schema.RequestFeedbackCommand` | input | `sceneId: Identifier`; `assistantId: Identifier`; `requestId: Identifier`; `feedbackKind: String`; `correlationId: Identifier` |
| `Schema.TraceFeedbackEvent` | input | `useCaseId: Identifier`; `scenarioId: Identifier`; `stepId: Identifier`; `capabilityId: Identifier`; `effectId: Identifier`; `stateRef: Identifier`; `correlationId: Identifier` |
| `Schema.ReadinessEvaluationRequest` | input | `sceneId: Identifier`; `machineId: Identifier`; `requestId: Identifier`; `requiredCupId: Identifier`; `requiredProgram: String`; `correlationId: Identifier` |
| `Schema.ReadinessStateSyncRequest` | input | `sceneId: Identifier`; `machineId: Identifier`; `readinessResult: String`; `reasonCode: String [0..1]`; `startPermission: String`; `correlationId: Identifier` |
| `Schema.TraceReadinessOutcomeEvent` | input | `useCaseId: Identifier`; `scenarioId: Identifier`; `stepId: Identifier`; `capabilityId: Identifier`; `effectId: Identifier`; `readinessResult: String`; `correlationId: Identifier` |
| `Schema.ConfirmationPromptRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `requestId: Identifier`; `requiredActorId: Identifier`; `promptKind: String`; `correlationId: Identifier` |
| `Schema.ConfirmationAffordanceRequest` | input | `sceneId: Identifier`; `requestId: Identifier`; `actorId: Identifier`; `affordanceKind: String`; `correlationId: Identifier` |
| `Schema.BrewingStartCommand` | input | `sceneId: Identifier`; `machineId: Identifier`; `requestId: Identifier`; `program: String`; `authorizationState: String`; `correlationId: Identifier` |
| `Schema.BrewingStateSyncRequest` | input | `sceneId: Identifier`; `machineId: Identifier`; `expectedLifecycleState: String`; `requestId: Identifier`; `correlationId: Identifier` |
| `Schema.TraceStartOutcomeEvent` | input | `useCaseId: Identifier`; `scenarioId: Identifier`; `stepId: Identifier`; `capabilityId: Identifier`; `effectId: Identifier`; `startAccepted: boolean`; `correlationId: Identifier` |
| `Schema.CompletionReportRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `machineId: Identifier`; `completionState: String`; `correlationId: Identifier` |
| `Schema.ReportPresentationRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `contentRef: Identifier`; `reportKind: String`; `correlationId: Identifier` |
| `Schema.CupCorrectionCompositionRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `audienceActorId: Identifier`; `targetObjectId: Identifier`; `contextObjectId: Identifier`; `reasonCode: String`; `correlationId: Identifier` |
| `Schema.ErrorExplanationRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `machineId: Identifier`; `reasonCode: String`; `blockedRequestId: Identifier`; `correlationId: Identifier` |
| `Schema.ErrorPresentationRequest` | input | `sceneId: Identifier`; `assistantId: Identifier`; `contentRef: Identifier`; `severity: String`; `correlationId: Identifier` |
| `Schema.TraceErrorOutcomeEvent` | input | `useCaseId: Identifier`; `scenarioId: Identifier`; `stepId: Identifier`; `capabilityId: Identifier`; `effectId: Identifier`; `reasonCode: String`; `startBlocked: boolean`; `correlationId: Identifier` |
| `Schema.ExceptionClosureFeedbackCommand` | input | `sceneId: Identifier`; `assistantId: Identifier`; `requestId: Identifier`; `outcome: String`; `correlationId: Identifier` |
| `Schema.TraceExceptionClosedEvent` | input | `useCaseId: Identifier`; `scenarioId: Identifier`; `stepId: Identifier`; `capabilityId: Identifier`; `effectId: Identifier`; `mainPathContinues: boolean`; `correlationId: Identifier` |
| `Schema.ActionReceipt` | output | `actionId: Identifier`; `accepted: boolean`; `message: String`; `correlationId: Identifier` |
| `Schema.AssistantStateSnapshot` | output | `sceneId: Identifier`; `assistantId: Identifier`; `mode: String`; `feedbackState: String`; `timestamp: String`; `correlationId: Identifier` |
| `Schema.AssistantContentDraft` | output | `contentRef: Identifier`; `assistantId: Identifier`; `contentKind: String`; `topic: String`; `correlationId: Identifier` |
| `Schema.ScenePresentationReceipt` | output | `presentationId: Identifier`; `shown: boolean`; `targetObjectId: Identifier [0..1]`; `correlationId: Identifier` |
| `Schema.TraceReceipt` | output | `traceEventId: Identifier`; `accepted: boolean`; `correlationId: Identifier` |
| `Schema.ReadinessResult` | output | `requestId: Identifier`; `result: String`; `reasonCode: String [0..1]`; `startPermission: String`; `correlationId: Identifier` |
| `Schema.MachineStateSnapshot` | output | `sceneId: Identifier`; `machineId: Identifier`; `lifecycleState: String`; `startPermission: String`; `feedbackState: String [0..1]`; `timestamp: String`; `correlationId: Identifier` |
| `Schema.AffordanceReceipt` | output | `affordanceId: Identifier`; `shown: boolean`; `actorId: Identifier`; `correlationId: Identifier` |
| `Schema.BrewingStartReceipt` | output | `requestId: Identifier`; `accepted: boolean`; `machineId: Identifier`; `reason: String [0..1]`; `correlationId: Identifier` |

## Trace auf fachliche Effects und StateAssertions

Diese Tabelle ist eine Rueckverfolgbarkeitshilfe. Sie bedeutet nicht, dass RuntimeActions Effects besitzen. Fachlich gehoeren Effects weiterhin zur Capability; technisch werden sie durch RuntimeBindings und RuntimeActions realisierbar gemacht.

| RuntimeAction-ID | Effect-Trace | StateAssertion-Trace | Pruefidee fuer spaetere ValidationCases |
| --- | --- | --- | --- |
| `B-RA-VIVIAN-SET-GUIDANCE-MODE` | `B-EFF-VIVIAN-GUIDING` | `SA-B-VIVIAN-GUIDING` | Receipt muss bestaetigen, dass Vivians Moduswechsel angenommen wurde. |
| `B-RA-VR-SYNC-ASSISTANT-STATE` | `B-EFF-VIVIAN-GUIDING` | `SA-B-VIVIAN-GUIDING` | Snapshot muss `mode=guiding` fuer Vivian zeigen. |
| `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE` | `B-EFF-CUP-GUIDANCE-ISSUED` | `SA-B-VIVIAN-GUIDANCE-CUP` | ContentDraft muss Topic `placeCup` enthalten. |
| `B-RA-VR-PRESENT-CUP-GUIDANCE` | `B-EFF-CUP-GUIDANCE-ISSUED` | `SA-B-VIVIAN-GUIDANCE-CUP` | PresentationReceipt muss bestaetigen, dass der Tassenhinweis gezeigt wurde. |
| `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE` | `B-EFF-PROGRAM-GUIDANCE-ISSUED` | `SA-B-VIVIAN-GUIDANCE-PROGRAM` | ContentDraft muss Topic `selectProgram` enthalten. |
| `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | `B-EFF-PROGRAM-GUIDANCE-ISSUED` | `SA-B-VIVIAN-GUIDANCE-PROGRAM` | PresentationReceipt muss bestaetigen, dass der Programmauswahlhinweis gezeigt wurde. |
| `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST` | `B-EFF-BREWING-REQUEST-CONFIRMED` | `SA-B-VIVIAN-INTENT-CONFIRMED` | Receipt muss die Rueckmeldung zur Bruehanforderung akzeptieren. |
| `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | `B-EFF-BREWING-REQUEST-CONFIRMED` | `SA-B-VIVIAN-INTENT-CONFIRMED` | TraceReceipt muss den StateAssertion-Bezug akzeptieren. |
| `B-RA-CM-EVALUATE-READINESS` | `B-EFF-READINESS-RESULT-PRODUCED` | `SA-B-CM-READY` oder `SA-B-READINESS-FAILED` | ReadinessResult muss eindeutig `passed` oder `failed` liefern. |
| `B-RA-CM-SYNC-READINESS-RESULT` | `B-EFF-READINESS-RESULT-PRODUCED` | `SA-B-CM-START-PERMISSION` oder `SA-B-CM-START-BLOCKED` | MachineStateSnapshot muss erlaubte oder blockierte Startfreigabe zeigen. |
| `B-RA-TRACE-SYNC-READINESS-OUTCOME` | `B-EFF-READINESS-RESULT-PRODUCED` | `SA-B-CM-READY`, `SA-B-READINESS-FAILED`, `SA-B-CM-SAFE` | TraceReceipt muss das positive oder negative Outcome akzeptieren. |
| `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT` | `B-EFF-CONFIRMATION-REQUESTED` | `SA-B-VIVIAN-AWAITING-CONFIRMATION` | ContentDraft muss eine Startbestaetigungsfrage enthalten. |
| `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | `B-EFF-CONFIRMATION-REQUESTED` | `SA-B-VIVIAN-AWAITING-CONFIRMATION` | AffordanceReceipt muss bestaetigen, dass die Bestaetigung moeglich ist. |
| `B-RA-CM-REQUEST-BREWING-START` | `B-EFF-BREWING-START-ISSUED` | `SA-B-BREWING-START-ISSUED` | BrewingStartReceipt muss den Start akzeptieren. |
| `B-RA-CM-SYNC-BREWING-STATE` | `B-EFF-BREWING-START-ISSUED` | `SA-B-CM-BREWING` | MachineStateSnapshot muss `lifecycleState=brewing` zeigen. |
| `B-RA-TRACE-SYNC-START-OUTCOME` | `B-EFF-BREWING-START-ISSUED` | `SA-B-BREWING-START-ISSUED`, `SA-B-CM-BREWING` | TraceReceipt muss den Startausgang akzeptieren. |
| `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT` | `B-EFF-COMPLETION-REPORTED` | `SA-B-VIVIAN-COMPLETION-REPORTED` | ContentDraft muss eine Abschlussmeldung enthalten. |
| `B-RA-VR-PRESENT-COMPLETION-REPORT` | `B-EFF-COMPLETION-REPORTED` | `SA-B-VIVIAN-COMPLETION-REPORTED` | PresentationReceipt muss bestaetigen, dass die Abschlussmeldung gezeigt wurde. |
| `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION` | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` | `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` | ContentDraft muss Topic `placeCupAgain` oder einen aequivalenten Korrekturgrund enthalten. |
| `B-RA-VR-PRESENT-CUP-CORRECTION` | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` | `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` | PresentationReceipt muss die Korrekturanleitung bestaetigen. |
| `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION` | `B-EFF-ERROR-EXPLAINED` | `SA-B-VIVIAN-ERROR-EXPLAINED` | ContentDraft muss den Grund `waterLevelLow` oder einen fachlichen Fehlergrund enthalten. |
| `B-RA-VR-PRESENT-ERROR-EXPLANATION` | `B-EFF-ERROR-EXPLAINED` | `SA-B-VIVIAN-ERROR-EXPLAINED` | PresentationReceipt muss die Fehlererklaerung bestaetigen. |
| `B-RA-TRACE-SYNC-ERROR-OUTCOME` | `B-EFF-ERROR-EXPLAINED` | `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE`, `SA-B-VIVIAN-ERROR-EXPLAINED` | TraceReceipt muss blockierten Start und Fehlererklaerung akzeptieren. |
| `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK` | `B-EFF-EXCEPTION-CLOSED` | `SA-B-VIVIAN-EXCEPTION-CLOSED` | Receipt muss bestaetigen, dass Vivian den Exception-Abschluss gemeldet hat. |
| `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | `B-EFF-EXCEPTION-CLOSED` | `SA-B-VIVIAN-EXCEPTION-CLOSED`, `SA-B-CM-NOT-BREWING` | TraceReceipt muss `mainPathContinues=false` und nicht gestarteten Bruehvorgang akzeptieren. |

## Keine verbotene Direktreferenz

| Pruefpunkt | Ergebnis |
| --- | --- |
| RuntimeActions liegen nur unter RuntimeBindings | ja |
| ScenarioSteps referenzieren RuntimeActions direkt | nein |
| CapabilityUses referenzieren RuntimeActions direkt | nein |
| Capabilities enthalten Endpoint-, Topic- oder Schema-Daten | nein |
| RuntimeBindings enthalten nur Action-Anschluss-IDs, keine Schemas | ja |
| RuntimeActions enthalten technische Endpoint-, Topic- und Schema-Daten | ja, hier ist das erlaubt und beabsichtigt. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 8.11 | Folgetask |
| --- | --- | --- |
| `ValidationCase` | nicht angelegt | 8.12 |
| Finale Kardinalitaetspruefung | vorbereitet | 8.13 |
| Finale Invariantenpruefung | vorbereitet | 8.13 |

## Abnahmekontrolle

| Kriterium aus Task 8.11 | Erfuellung |
| --- | --- |
| Technische Aktionen angelegt | 25 RuntimeActions sind formal angelegt. |
| Jede RuntimeBinding besitzt mindestens eine RuntimeAction | Alle elf RuntimeBindings besitzen zwei oder drei RuntimeActions. |
| Jede RuntimeAction hat genau einen Owner | Jede RuntimeAction ist genau einer RuntimeBinding zugeordnet. |
| Input- und Output-Schemas dokumentiert | Jede RuntimeAction referenziert genau ein Input- und ein Output-Schema. |
| Technische Details liegen nur auf RuntimeAction-Ebene | Endpoints, Topics und Schemas stehen nur in diesem RuntimeAction-Artefakt. |
| Trace bleibt indirekt | Es gibt keine direkte RuntimeAction-Referenz aus ScenarioStep, CapabilityUse, Capability oder Effect. |

## Konsequenz fuer Task 8.12

Task 8.12 kann nun `ValidationCase`-Instanzen anlegen. Diese koennen Stimuli aus Szenario, RuntimeBinding und RuntimeAction verwenden und muessen mindestens ein erwartetes Outcome besitzen.
