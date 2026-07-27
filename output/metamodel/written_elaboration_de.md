# Schriftliche Ausarbeitung: Dynamisches Functional-MLDS-Metamodell

Stand: 2026-07-07

## Problem

Virtuelle Szenen werden zunehmend nicht mehr als statische 3D-Umgebungen verstanden, sondern als dynamische, interaktive Systeme. In solchen Szenen reagieren Agenten auf Ereignisse, Bedingungen und Zustandsaenderungen; Objekte koennen bedient werden; Assistenzsysteme wie Vivian fuehren Benutzer durch Handlungen; und technische Runtimes muessen fachliche Modellentscheidungen in konkrete Aktionen umsetzen. Dadurch entsteht ein Modellierungsproblem: Die fachliche Bedeutung eines Ablaufs darf nicht in natuerlichem Text, Szenen-Skripten, Promptfragmenten oder technischen Adapteraufrufen verborgen bleiben. Sie muss explizit, pruefbar und tracebar modelliert werden.

Das erste betrachtete Beispiel ist das dynamische Modellieren von Agenten in einer virtuellen Szene. Ein Agent soll nicht nur als Objekt in einer Szene existieren, sondern sein Verhalten in Abhaengigkeit von gueltigen Ereignissen, raeumlichen und fachlichen Bedingungen sowie beobachtbaren Zielzustaenden aendern koennen. Ein solcher Ablauf umfasst zum Beispiel das Erkennen eines Ausloeseereignisses, das Pruefen der Erreichbarkeit einer Zielzone, das Annehmen einer Ausfuehrungsrolle, eine zielgerichtete Handlung und die Rueckmeldung eines erreichten oder nicht erreichten Zielzustands. Ohne ein explizites Metamodell bleibt unklar, ob eine Aussage eine externe Benutzerrolle, einen systeminternen Agenten, ein Szenenobjekt, eine Bedingung, einen Zustand, eine fachliche Faehigkeit oder bereits eine technische Runtime-Aktion beschreibt.

Das zweite betrachtete Beispiel ist die Modellierung von Interaktionsobjekten mit Vivian, etwa die assistierte Bedienung einer virtuellen Kaffeemaschine. Hier liegt das Problem nicht nur im Objekt selbst, sondern in der Kopplung mehrerer fachlicher Ebenen: Ein Visitor handelt als externer Actor, Vivian ist ein im System modellierter Assistenzagent, die Kaffeemaschine ist ein bedienbares Interaktionsobjekt, und der Bruehvorgang darf erst nach Tassenplatzierung, Programmauswahl, Bereitschaftspruefung und expliziter Benutzerbestaetigung starten. Gleichzeitig existieren technische Aktionen, etwa Adapteraufrufe oder VR-Ausgaben, die zwar zur Ausfuehrung notwendig sind, aber nicht mit den fachlichen Use-Case-Schritten verwechselt werden duerfen.

Das zentrale Problem besteht daher in der Trennung und Verbindung dieser Ebenen. Das Modell muss fachliche Anforderungen, Use Cases, Scenarios, ScenarioSteps, Events, Conditions, StateAssertions, Capabilities, Effects, RuntimeBindings, RuntimeActions und ValidationCases so verbinden, dass die Bedeutung des Ablaufs erhalten bleibt. Ein ScenarioStep darf nicht direkt zu einer RuntimeAction werden, weil dadurch fachliche Absicht und technische Ausfuehrung vermischt wuerden. Ebenso darf Vivian nicht als externer Actor modelliert werden, wenn sie Teil des Systems ist, und eine Kaffeemaschine darf nicht nur als technische Startfunktion verstanden werden, wenn sie im Use Case ein beobachtbares Interaktionsobjekt mit Zustand und Bedienbarkeit ist.

Daraus folgt ein Spannungsfeld fuer das Metamodell. Einerseits muss der Kern kompakt bleiben, damit einfache Use Cases nicht durch Spezialklassen fuer Raum, Dialog, Affordances, Entscheidungsregeln oder Runtime-Profile ueberladen werden. Andererseits muessen genau diese Spezialsemantiken bei Bedarf anschlussfaehig modellierbar sein, weil sie fuer automatische Pruefung, Generierung, Validierung und Runtime-Integration entscheidend werden. Der Loesungsraum liegt deshalb nicht in einem grossen monolithischen Metamodell, sondern in einem stabilen Kern mit klaren optionalen Ergaenzungsmodellen.

Fuer eine wissenschaftlich belastbare Modellierung ergeben sich daraus vier Anforderungen:

| Anforderung | Bedeutung |
| --- | --- |
| Fachliche Eindeutigkeit | Jedes Modellelement muss erkennen lassen, ob es Rolle, Agent, Entity, Event, Bedingung, Zustand, Faehigkeit, Wirkung oder technische Aktion beschreibt. |
| Traceability | Anforderungen muessen ueber UseCase, Scenario, ScenarioStep, Capability, Effect und ValidationCase nachvollziehbar bleiben. |
| Trennung von Fachlichkeit und Technik | RuntimeActions duerfen nur ueber RuntimeBindings an fachliche Capabilities angebunden werden, nicht direkt an UseCase- oder ScenarioStep-Ebene. |
| Erweiterbarkeit ohne Kernueberladung | Raumsemantik, Interaktionsobjekte, Vivian-Dialoge, Entscheidungsregeln, Zustandsautomaten, Runtime-Profile und formale Testorakel muessen optional andocken koennen, ohne bestehende Kernmodelle ungueltig zu machen. |

Die Problemstellung dieser Arbeit lautet somit: Es wird ein kompaktes, rueckwaertskompatibles und erweiterbares Metamodell benoetigt, das dynamische Agentenszenen und assistierte Interaktionsobjekte fachlich praezise beschreibt, ihre technische Ausfuehrbarkeit vorbereitet und ihre Validierbarkeit sicherstellt, ohne fachliche Use-Case-Modellierung mit Runtime-Implementierung zu vermischen.

## Abnahmekontrolle 12.1

| Kriterium aus Task 12.1 | Erfuellung |
| --- | --- |
| Abschnitt `Problem` vorhanden | Der Abschnitt ist als `## Problem` angelegt. |
| Dynamische Szenen erklaert | Agentenverhalten, Ereignisse, Bedingungen, Zielzustaende und Rueckmeldungen werden beschrieben. |
| Interaktionsobjekte erklaert | Vivian, Visitor, Kaffeemaschine, Bedienbarkeit, Bereitschaftspruefung und Benutzerbestaetigung werden beschrieben. |
| Modellierungsbedarf klar | Der Text begruendet, warum fachliche Semantik explizit, pruefbar, tracebar und von RuntimeActions getrennt modelliert werden muss. |
| Anschluss an Metamodell klar | Die zentrale Kette von Requirements bis ValidationCases und die Rolle optionaler Ergaenzungsmodule werden eingefuehrt. |

## Anwendungsfall A: Dynamisches Agentenverhalten in einer virtuellen Szene

Der erste Beispielanwendungsfall beschreibt, wie dynamisches Agentenverhalten in einer virtuellen Szene fachlich modelliert wird. Der Use Case traegt die Instanz-ID `UC-A-01` und den Namen `Dynamisches Agentenverhalten in virtueller Szene modellieren`. Sein Ziel ist es, ein Agentenverhalten so zu beschreiben, dass der Agent auf gueltige Ereignisse und Bedingungen reagieren, seine Rolle oder Handlung anpassen und einen pruefbaren Zielzustand der Szene erreichen kann.

Der Anwendungsfall ist bewusst fachlich formuliert. Er beschreibt nicht, welche Engine-Methode, welcher Controlleraufruf oder welche RuntimeAction ausgefuehrt wird. Stattdessen beschreibt er, welche Situation in der Szene gilt, welche Bedingungen geprueft werden, welche Agentenreaktion fachlich erwartet wird und welcher Zustand anschliessend beobachtbar sein muss. Dadurch bleibt die spaetere technische Ausfuehrung anschlussfaehig, ohne die Use-Case-Ebene zu verfaelschen.

### Ziel

Das Ziel von Anwendungsfall A ist die modellierbare Reaktion eines Agenten auf eine veraenderte Szene. Ein gueltiges Ausloeseereignis wird festgestellt, der Agent wird im zulaessigen Szenenbereich und als handlungsbereit erkannt, die Erreichbarkeit der Zielzone wird bewertet, und der Agent nimmt anschliessend eine passende Ausfuehrungsrolle ein. Danach fuehrt er eine zielgerichtete Szenenhandlung aus, erreicht die Zielzone, und der erreichte Zustand wird beobachtbar verifiziert.

Damit steht nicht die Bewegung als technische Pfadplanung im Mittelpunkt, sondern die fachliche Nachvollziehbarkeit des Ablaufs. Das Modell soll beantworten koennen:

| Frage | Bedeutung fuer A |
| --- | --- |
| Was loest den Ablauf aus? | Ein gueltiges Ereignis oder eine relevante Zustandsaenderung der Szene. |
| Welche Bedingungen muessen gelten? | Der Agent muss im gueltigen Szenenbereich, handlungsbereit und die Zielzone fachlich erreichbar sein. |
| Was tut der Agent fachlich? | Er nimmt eine Ausfuehrungsrolle an und fuehrt eine zielgerichtete Handlung aus. |
| Woran erkennt man Erfolg? | Die Zielzone ist erreicht, der Zielzustand ist verifiziert, und eine Ergebnisrueckmeldung ist bestaetigt. |
| Was passiert bei Abweichungen? | Eine temporaere Blockade fuehrt in eine Alternative; eine dauerhafte Blockade fuehrt in eine Exception. |

### Rollen

Die externen Rollen des Anwendungsfalls werden als `Actor` verstanden. Sie sind keine konkreten Avatare, keine Agenten und keine technischen Systeme, sondern Rollen ausserhalb des modellierten Systems.

| Rolle | Bedeutung im Anwendungsfall |
| --- | --- |
| `ScenarioDesigner` | Beschreibt die Modellierungsabsicht, das Zielverhalten, relevante Bedingungen und den erwarteten Zielzustand. |
| `SceneParticipant` | Kann Ereignisse in der Szene ausloesen oder Agentenreaktionen provozieren. |
| `SceneObserver` | Beobachtet und bewertet, ob das Agentenverhalten und der Zielzustand erreicht wurden. |
| `ExternalEventSource` | Repraesentiert externe Ausloeser wie Sensorsignale, Simulationszeit oder Umgebungsaenderungen. |
| `TrainingSupervisor` | Kann im Trainings- oder Demonstrationskontext Korrektur, Wiederholung oder Erklaerung anfordern. |

Der dynamische Agent selbst ist keine externe Rolle. Er gehoert als modelliertes Systemsubjekt in die Agent-/Entity-Ebene. Genau diese Trennung ist fuer die Modellierung wichtig: Externe Rollen formulieren Absichten, loesen Ereignisse aus oder beobachten Ergebnisse; der Agent fuehrt fachliches Verhalten innerhalb des Systems aus.

### Hauptablauf

Der Hauptablauf ist das Scenario `A-MAIN-SC01` mit `Scenario.kind = main`. Es beschreibt den erfolgreichen Normalfall: Der Agent reagiert auf ein gueltiges Ereignis und erreicht eine Zielzone.

Der Ablauf besteht aus neun fachlichen Schritten:

| Schritt | Inhalt |
| --- | --- |
| `A-MAIN-S01` | Ein gueltiges Ausloeseereignis wird festgestellt. |
| `A-MAIN-S02` | Der Agent wird im gueltigen Szenenbereich festgestellt. |
| `A-MAIN-S03` | Der Agent wird als handlungsbereit festgestellt. |
| `A-MAIN-S04` | Die Zielzone wird als fachlich erreichbar festgestellt. |
| `A-MAIN-S05` | Der Agent nimmt die Ausfuehrungsrolle an. |
| `A-MAIN-S06` | Der Agent fuehrt die zielgerichtete Szenenhandlung aus. |
| `A-MAIN-S07` | Der Agent erreicht die Zielzone. |
| `A-MAIN-S08` | Der Zielzustand wird beobachtbar verifiziert. |
| `A-MAIN-S09` | Die Ergebnisrueckmeldung wird bestaetigt. |

Die ersten vier Schritte sind Beobachtungs- und Pruefschritte. Sie stellen sicher, dass der Ablauf fachlich ueberhaupt ausgefuehrt werden darf. Die Schritte fuenf und sechs sind Systemreaktionen des modellierten Agenten. Sie werden nicht als Handlung eines externen Actors verstanden, sondern spaeter ueber `CapabilityUse` und `Capability` beschrieben. Die letzten drei Schritte machen die Zielerreichung und Rueckmeldung beobachtbar.

Im Hauptablauf gibt es keinen `actorIntent`-Schritt. Deshalb bleibt `performedBy` fuer alle Schritte leer. Das ist fachlich korrekt, weil die Agentenhandlung nicht einer externen Rolle zugeschrieben wird.

### Alternative: temporaere Blockade

Das alternative Scenario `A-ALT-SC01` beschreibt eine temporaere Blockade der Zielzone. Es tritt nach `A-MAIN-S04` ein, also genau an der Stelle, an der die Erreichbarkeit der Zielzone bewertet wird.

Der Einstieg in die Alternative gilt, wenn die Zielzone grundsaetzlich erreichbar bleibt, aber eine `ObstacleRegion` temporaer blockiert ist. Der Alternativpfad besteht aus zwei Schritten:

| Schritt | Inhalt |
| --- | --- |
| `A-ALT-S01` | Die temporaere Blockade der Zielzone wird festgestellt. |
| `A-ALT-S02` | Die Blockade wird fachlich als aufgehoben festgestellt. |

Nach der Aufloesung der Blockade wird der Hauptpfad vor `A-MAIN-S05` fortgesetzt. Diese Rueckfuehrung ist wichtig, weil der Agent die Ausfuehrungsrolle erst annehmen soll, wenn die Zielzone wieder erreichbar ist. Die Alternative ist deshalb kein eigenstaendiger Fehlerabschluss, sondern ein korrigierbarer Zwischenpfad.

### Exception: dauerhafte Blockade

Das Exception-Scenario `A-EX-SC01` beschreibt den Fall, dass die Zielzone dauerhaft blockiert ist. Auch dieser Pfad steigt nach `A-MAIN-S04` ein, fuehrt aber nicht in den Hauptpfad zurueck.

Der Exception-Pfad besteht aus drei Schritten:

| Schritt | Inhalt |
| --- | --- |
| `A-EX-S01` | Die dauerhafte Blockade der Zielzone wird festgestellt. |
| `A-EX-S02` | Der Agent wird am Fortsetzen des Zielpfads gehindert. |
| `A-EX-S03` | Der nicht erreichbare Zielzustand wird als Fehlerabschluss rueckgemeldet. |

Die Exception endet in einem sicheren, beobachtbaren Zustand: Die Blockade bleibt erkennbar, die Zielzone wird nicht faelschlich als erreicht markiert, der Agent setzt die Zielhandlung nicht unzulaessig fort, und die Szene meldet einen Fehler- oder Reaktionsbedarf. Eine Rueckfuehrung in den Hauptpfad waere hier inkonsistent, weil die notwendige Bedingung `TargetZone.state = reachable` nicht wiederhergestellt ist.

### Zusammenfassung

Anwendungsfall A zeigt, warum das Metamodell dynamische Szenen fachlich strukturiert beschreiben muss. Der gleiche Ablauf enthaelt externe Rollen, einen modellierten Agenten, beobachtbare Szenenobjekte, Events, Guards, StateAssertions, normale Sequenzen, Alternativen und Exceptions. Die Herausforderung besteht darin, diese Elemente so zu trennen, dass der Ablauf validierbar bleibt und spaeter technisch angebunden werden kann, ohne die fachliche Ebene mit RuntimeActions zu vermischen.

## Abnahmekontrolle 12.2

| Kriterium aus Task 12.2 | Erfuellung |
| --- | --- |
| Ziel beschrieben | Der Abschnitt `Ziel` beschreibt die modellierbare Agentenreaktion und den pruefbaren Zielzustand. |
| Rollen beschrieben | Die externen Rollen `ScenarioDesigner`, `SceneParticipant`, `SceneObserver`, `ExternalEventSource` und `TrainingSupervisor` sind erklaert. |
| Hauptablauf beschrieben | `A-MAIN-S01` bis `A-MAIN-S09` sind als verstaendliche Schrittfolge beschrieben. |
| Alternative beschrieben | `A-ALT-SC01` mit Einstieg nach `A-MAIN-S04`, temporaerer Blockade und Rueckfuehrung vor `A-MAIN-S05` ist erklaert. |
| Exception beschrieben | `A-EX-SC01` mit dauerhafter Blockade, sicherem Halten und Fehlerabschluss ist erklaert. |
| Ohne Diagramm verstaendlich | Der Abschnitt nennt Ziel, Rollen, Schritte, Einstiegspunkte und Endzustaende explizit im Text. |

## Mapping A

Anwendungsfall A wird im Metamodell als fachlich-technische Trace-Kette abgebildet. Der Kern des Mappings lautet:

`Requirement -> Satisfy -> UseCase -> Scenario -> ScenarioStep -> CapabilityUse -> Capability -> Effect -> RuntimeBinding -> RuntimeAction -> ValidationCase`

Diese Kette ist bewusst indirekt. Ein `ScenarioStep` wird nicht direkt einer technischen Aktion zugeordnet. Stattdessen beschreibt der Schritt eine fachliche Situation oder Reaktion. Nur wenn ein Schritt eine aktive systemische Reaktion benoetigt, besitzt er eine `CapabilityUse`. Diese verweist auf eine fachliche `Capability`; erst danach wird ueber `RuntimeBinding` und `RuntimeAction` die technische Ausfuehrung vorbereitet.

### Requirements, UseCase und Actor

Die Anforderungen von A werden als `Requirement`-Instanzen `A-REQ-001` bis `A-REQ-015` angelegt. Sie beschreiben unter anderem den fachlichen Use Case, den ereignisbasierten Start, raeumliche Gueltigkeit, Handlungsbereitschaft, Zielerreichbarkeit, Rollenwechsel, Zielhandlung, Zielverifikation, Ergebnisrueckmeldung, Alternative, Exception, Verbot technischer Kurzschluesse und Traceability.

Der Use Case selbst ist `UC-A-01`. Er beschreibt nicht eine Runtime-Funktion, sondern die Systemnutzung `Dynamisches Agentenverhalten in virtueller Szene modellieren`. Die externen Rollen sind als `Actor`-Instanzen modelliert:

| Actor | Rolle im Mapping |
| --- | --- |
| `ACT-A-01 ScenarioDesigner` | Liefert Modellierungsabsicht, Zieltext und fachlichen Kontext. |
| `ACT-A-02 SceneParticipant` | Kann das Start-Event im Szenenkontext ausloesen. |
| `ACT-A-03 SceneObserver` | Beobachtet Effects, Zielzustaende und Validation-Ergebnisse. |

`Satisfy` wird verwendet, um Requirements und UseCase sauber zu erfuellen. `SAT-A-REQ-001` bis `SAT-A-REQ-015` belegen jeweils den Requirement-Zweig. `SAT-A-UC-001` belegt getrennt den UseCase-Zweig und ordnet `UC-A-01` den Scenarios `A-MAIN-SC01`, `A-ALT-SC01` und `A-EX-SC01` zu. Damit bleibt die XOR-Regel erhalten: Eine einzelne `Satisfy`-Instanz referenziert entweder Requirements oder UseCases, aber nicht beides gleichzeitig.

### Scenario-Ebene

`UC-A-01` besitzt genau drei `Scenario`-Instanzen:

| Scenario | `Scenario.kind` | Bedeutung |
| --- | --- | --- |
| `A-MAIN-SC01` | `main` | Erfolgreicher Ablauf: Agent reagiert und erreicht die Zielzone. |
| `A-ALT-SC01` | `alternative` | Temporaere Blockade wird aufgeloest und der Hauptpfad wird fortgesetzt. |
| `A-EX-SC01` | `exception` | Dauerhafte Blockade verhindert Zielerreichung und fuehrt zum Fehlerabschluss. |

Damit ist die Invariante erfuellt, dass pro Use Case genau ein Main-Scenario existiert. Alternative und Exception werden nicht als `Include` oder `Extend` modelliert, weil sie keine eigenstaendigen oder wiederverwendeten Use Cases sind. Sie sind Ablaufvarianten innerhalb desselben Use Case.

Die Scenarios enthalten geordnete `ScenarioStep`-Instanzen. `A-MAIN-SC01` enthaelt `A-MAIN-S01` bis `A-MAIN-S09`, `A-ALT-SC01` enthaelt `A-ALT-S01` und `A-ALT-S02`, und `A-EX-SC01` enthaelt `A-EX-S01` bis `A-EX-S03`.

Die Ablaufkanten werden als `StepRelation` modelliert. Im Hauptpfad verbinden `A-MAIN-R01` bis `A-MAIN-R08` die neun Schritte sequenziell. Der Alternativpfad nutzt `A-ALT-R01` als Einstieg aus `A-MAIN-S04`, `A-ALT-R02` als interne Sequenz und `A-ALT-R03` als Rueckfuehrung vor `A-MAIN-S05`. Der Exception-Pfad nutzt `A-EX-R01` als Einstieg aus `A-MAIN-S04` und endet ueber `A-EX-R02` und `A-EX-R03` ohne Rueckfuehrung.

### Events, Conditions und StateAssertions

Events modellieren die fachlichen Ausloeser. Fuer A sind acht `Event`-Instanzen vorbereitet. Genutzt werden insbesondere:

| Event | Bedeutung |
| --- | --- |
| `A-E1` | `entered(SceneParticipant, TriggerZone)` startet den Hauptpfad. |
| `A-E4` | `stateChanged(ObstacleRegion, blocked|temporarilyBlocked)` startet Alternative oder Exception. |
| `A-E7` | `verified(ObservationPoint)` stuetzt die Zielverifikation. |
| `A-E8` | `shown(FeedbackSignal)` stuetzt die Abschlussrueckmeldung. |

`Condition` wird fuer Preconditions, Guards und Postconditions verwendet. Beispiele sind `A-P1` fuer die Existenz des Agenten, `A-GUARD-S04` fuer die Zielerreichbarkeit, `A-GUARD-ALT-R01` fuer den Einstieg in die temporaere Blockade und `A-GUARD-EX-R01` fuer den Einstieg in die dauerhafte Blockade.

`StateAssertion` beschreibt erwartete oder beobachtbare Zustandsaussagen. A besitzt 28 StateAssertions. Beispiele:

| StateAssertion | Subjekt | Erwarteter Zustand |
| --- | --- | --- |
| `A-SA-S05-01` | `AgentBody` | `roleState=executor` |
| `A-SA-S06-01` | `AgentBody` | `movingTo(TargetZone)` |
| `A-SA-S07-02` | `TargetZone` | `reached` |
| `A-ALT-SA03` | `ObstacleRegion` | `cleared` |
| `A-EX-SA04` | `AgentBody` | `roleState=blocked` |
| `A-EX-SA05` | `FeedbackSignal` | `failed` |

Damit bleiben Bedingungen und Ergebnisse maschinenlesbar. Sie werden nicht als technische Messaufrufe formuliert, sondern als fachliche Aussagen ueber identifizierbare Subjekte.

### Entity und Agent

Die beobachtbaren und ausfuehrenden Subjekte des Anwendungsfalls werden ueber `Entity` und `Agent` abgebildet. Der zentrale Agent ist `AgentBody`. Er ist als `Agent` und damit als spezialisierte `Entity` zu verstehen. Weitere relevante Entities sind unter anderem `TargetZone`, `TriggerZone`, `ObstacleRegion`, `ObservationPoint`, `FeedbackSignal`, `SceneStateFlag` und `SceneBoundary`.

Die optionale Kernpraezisierung `Entity.kind [0..1]` kann diese Entities grob typisieren, ist aber keine Pflichtmigration. Nach aktuellem Stand waere eine konsistente Nachpflege:

| Entity | Naheliegende aktuelle `Entity.kind`-Typisierung |
| --- | --- |
| `AgentBody` | `agent` |
| `TargetZone`, `TriggerZone`, `ObstacleRegion`, `SceneBoundary` | `zone` |
| `FeedbackSignal` | `signal` |
| `SceneStateFlag`, `ObservationPoint` | `stateObject` |

Diese Typisierung ist optional. Das A-Mapping bleibt auch ohne gesetztes `Entity.kind` gueltig.

### Capability, Effect und Runtime

Nur aktive systemische Reaktionen werden als `CapabilityUse` modelliert. In A sind das drei Stellen:

| ScenarioStep | CapabilityUse | Capability |
| --- | --- | --- |
| `A-MAIN-S05` | `A-CU-001` | `A-CAP-ADOPT-EXECUTOR-ROLE` |
| `A-MAIN-S06` | `A-CU-002` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` |
| `A-EX-S02` | `A-CU-003` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` |

Jede `Capability` besitzt fachliche Preconditions und mindestens einen versprochenen `Effect`. A nutzt sechs Effects:

| Capability | Effects |
| --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-EFF-ROLE-EXECUTOR`, `A-EFF-AGENT-ACTING` |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-EFF-AGENT-MOVING-TO-TARGET`, `A-EFF-TARGET-OCCUPIED` |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-EFF-AGENT-WAITING`, `A-EFF-ROLE-BLOCKED` |

Die Effects sind fachlich beobachtbar und werden durch `ACT-A-03 SceneObserver` beobachtbar gemacht. Sie sind zudem auf StateAssertions rueckgebunden, zum Beispiel `A-EFF-ROLE-EXECUTOR` auf `A-SA-S05-01` und `A-EFF-TARGET-OCCUPIED` auf `A-SA-S06-02`. Die optionale Kernkante `Effect.evidencedBy -> StateAssertion [0..*]` kann diese Rueckbindung spaeter formal ausdruecken.

Die technische Anbindung beginnt erst mit `RuntimeBinding`. A besitzt drei RuntimeBindings:

| RuntimeBinding | Capability | RuntimeActions |
| --- | --- | --- |
| `A-RB-ROLE-EXECUTOR-VR` | `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-RA-ROLE-SET`, `A-RA-ROLE-SYNC` |
| `A-RB-TARGET-ACTION-VR` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-RA-TARGET-ACTION-REQUEST`, `A-RA-TARGET-OCCUPANCY-SYNC` |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-RA-BLOCK-PROGRESS-HOLD`, `A-RA-BLOCK-STATE-SYNC` |

Damit ist die technische Ausfuehrung erreichbar, aber nicht direkt an ScenarioSteps gekoppelt.

### ValidationCase

`ValidationCase` prueft die fachliche und technische Trace-Kette. A besitzt acht ValidationCases:

| ValidationCase | Pruefschwerpunkt |
| --- | --- |
| `A-VC-001-MAIN-PRECONDITION-CHAIN` | Preconditions und Startkette des Hauptpfads. |
| `A-VC-002-ROLE-BINDING` | Rollenwechsel und RuntimeBinding fuer `A-MAIN-S05`. |
| `A-VC-003-TARGET-ACTION-BINDING` | Zielhandlung und RuntimeBinding fuer `A-MAIN-S06`. |
| `A-VC-004-MAIN-COMPLETION` | End-to-end-Abschluss des Hauptpfads. |
| `A-VC-005-ALTERNATIVE-TEMPORARY-BLOCK` | Alternative bei temporaerer Blockade. |
| `A-VC-006-EXCEPTION-BLOCKED-PROGRESS` | Exception bei dauerhafter Blockade. |
| `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | Keine direkte `ScenarioStep -> RuntimeAction`-Kante. |
| `A-VC-008-NO-ARTIFICIAL-PARALLELGROUP` | Keine kuenstliche ParallelGroup. |

ValidationCases duerfen RuntimeBindings pruefen, besitzen sie aber nicht. RuntimeActions erscheinen nur als technische Details innerhalb der jeweiligen RuntimeBinding oder als Stimulusbeschreibung eines ValidationCase.

### Bewusst ausgelassene zentrale Klassen

Nicht jede zentrale Metamodellklasse muss in A instanziiert werden. Einige Klassen bleiben bewusst leer, weil der A-Ablauf sie nicht benoetigt:

| Metamodellklasse | Status in A | Begruendung |
| --- | --- | --- |
| `ExtensionPoint` | nicht instanziiert | A nutzt keine formale Use-Case-Erweiterung; Alternative und Exception sind Scenarios desselben Use Case. |
| `Include` | nicht instanziiert | Es gibt keinen verpflichtend wiederverwendeten Sub-Use-Case. |
| `Extend` | nicht instanziiert | Es gibt keinen eigenstaendigen Erweiterungs-Use-Case mit ExtensionPoint. |
| `ParallelGroup` | nicht instanziiert | Hauptpfad, Alternative und Exception sind sequenziell modellierbar. |
| `FunctionBehavior` | nicht instanziiert | A benoetigt keine EAST-ADL-FunctionBehavior-Bruecke; Capabilities reichen fuer die fachliche Ebene. |
| `RandomVariable` | nicht instanziiert | A nutzt keine probabilistische Condition; Timing bleibt als deterministische Condition beschreibbar. |

Diese Auslassungen sind kein Modellierungsfehler, weil die jeweiligen Kardinalitaeten `0..*` oder `0..1` erlauben und die Nichtnutzung fachlich begruendet ist.

### Klassenabdeckung fuer A

| Zentrale Klasse | A-Abbildung |
| --- | --- |
| `RequirementsModel` | Der A-Requirements-Kontext enthaelt `A-REQ-001` bis `A-REQ-015` und `UC-A-01`. |
| `Requirement` | `A-REQ-001` bis `A-REQ-015`. |
| `UseCase` | `UC-A-01`. |
| `Actor` | `ACT-A-01`, `ACT-A-02`, `ACT-A-03`. |
| `Satisfy` | `SAT-A-REQ-001` bis `SAT-A-REQ-015`, `SAT-A-UC-001`. |
| `ExtensionPoint` | begruendet ausgelassen. |
| `Include` | begruendet ausgelassen. |
| `Extend` | begruendet ausgelassen. |
| `Scenario` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01`. |
| `ScenarioStep` | `A-MAIN-S01` bis `A-MAIN-S09`, `A-ALT-S01` bis `A-ALT-S02`, `A-EX-S01` bis `A-EX-S03`. |
| `StepRelation` | `A-MAIN-R01` bis `A-MAIN-R08`, `A-ALT-R01` bis `A-ALT-R03`, `A-EX-R01` bis `A-EX-R03`. |
| `ParallelGroup` | begruendet ausgelassen. |
| `Event` | `A-E1` bis `A-E8`, mit genutzten Events `A-E1`, `A-E4`, `A-E7`, `A-E8`. |
| `Condition` | `A-P1` bis `A-P12`, `A-GUARD-*`, `A-Q1` bis `A-Q11`. |
| `StateAssertion` | 28 Instanzen, unter anderem `A-SA-S05-01`, `A-SA-S07-02`, `A-ALT-SA03`, `A-EX-SA04`. |
| `Entity` | `AgentBody`, `TargetZone`, `TriggerZone`, `ObstacleRegion`, `ObservationPoint`, `FeedbackSignal`, `SceneStateFlag`, `SceneBoundary`. |
| `Agent` | `AgentBody` als ausfuehrende und beobachtbare Agent-Entity. |
| `CapabilityUse` | `A-CU-001`, `A-CU-002`, `A-CU-003`. |
| `Capability` | `A-CAP-ADOPT-EXECUTOR-ROLE`, `A-CAP-PERFORM-TARGETED-SCENE-ACTION`, `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS`. |
| `Effect` | `A-EFF-ROLE-EXECUTOR`, `A-EFF-AGENT-ACTING`, `A-EFF-AGENT-MOVING-TO-TARGET`, `A-EFF-TARGET-OCCUPIED`, `A-EFF-AGENT-WAITING`, `A-EFF-ROLE-BLOCKED`. |
| `FunctionBehavior` | begruendet ausgelassen. |
| `RuntimeBinding` | `A-RB-ROLE-EXECUTOR-VR`, `A-RB-TARGET-ACTION-VR`, `A-RB-BLOCKED-PROGRESS-VR`. |
| `RuntimeAction` | `A-RA-ROLE-SET`, `A-RA-ROLE-SYNC`, `A-RA-TARGET-ACTION-REQUEST`, `A-RA-TARGET-OCCUPANCY-SYNC`, `A-RA-BLOCK-PROGRESS-HOLD`, `A-RA-BLOCK-STATE-SYNC`. |
| `ValidationCase` | `A-VC-001-MAIN-PRECONDITION-CHAIN` bis `A-VC-008-NO-ARTIFICIAL-PARALLELGROUP`. |
| `RandomVariable` | begruendet ausgelassen. |

## Abnahmekontrolle 12.3

| Kriterium aus Task 12.3 | Erfuellung |
| --- | --- |
| Abschnitt `Mapping A` vorhanden | Der Abschnitt ist als `## Mapping A` angelegt. |
| Zentrale Klassen konkret verwendet | Requirements, UseCase, Actors, Satisfy, Scenarios, Steps, StepRelations, Events, Conditions, StateAssertions, Entities, Agent, CapabilityUse, Capability, Effect, RuntimeBinding, RuntimeAction und ValidationCase sind mit A-Instanzen belegt. |
| Ausgelassene Klassen begruendet | `ExtensionPoint`, `Include`, `Extend`, `ParallelGroup`, `FunctionBehavior` und `RandomVariable` werden begruendet ausgelassen. |
| Keine technische Kurzschaltung | Das Mapping beschreibt die indirekte Kette `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`. |
| Aktuelle Kernanpassungen beruecksichtigt | `Entity.kind [0..1]` und `Effect.evidencedBy -> StateAssertion [0..*]` werden als optionale Nachpflege eingeordnet. |

## Bewertung A

Anwendungsfall A ist mit dem kompakten Kernmetamodell vollstaendig beschreibbar, ohne dass ein bestehender UseCase, ein Scenario oder ein ScenarioStep ungueltig wird. Die Abbildung ist insbesondere fuer Requirements, UseCase, Actors, Scenarios, ScenarioSteps, StepRelations, Events, Conditions, StateAssertions, Capabilities, Effects, RuntimeBindings, RuntimeActions und ValidationCases direkt tragfaehig.

Gleichzeitig zeigt A mehrere Praezisionsgrenzen. Diese Grenzen blockieren das Beispiel nicht, werden aber relevant, sobald Raumsemantik, Zustandsuebergaenge, Eventdetails, Runtime-Orchestrierung oder Testorakel automatisch ausgewertet oder generiert werden sollen. Die Bewertung unterscheidet deshalb drei Ebenen: direkte Abbildung, unscharfe Abbildung und Luecken.

### Direkte Abbildung

Die direkte Abbildung umfasst alle Elemente, die ohne neue Metamodellklasse und ohne semantischen Umweg auf vorhandene Klassen, Attribute oder Beziehungen gemappt werden koennen.

| Bereich | Bewertung | Begruendung |
| --- | --- | --- |
| Requirements und UseCase | direkt abbildbar | `A-REQ-001` bis `A-REQ-015`, `UC-A-01` und die `Satisfy`-Instanzen passen in den EAST-ADL-nahen Kern. |
| Externe Rollen | direkt abbildbar | `ACT-A-01`, `ACT-A-02` und `ACT-A-03` sind klare `Actor`-Rollen und werden nicht mit Agenten oder Entities vermischt. |
| Scenario-Struktur | direkt abbildbar | `A-MAIN-SC01`, `A-ALT-SC01` und `A-EX-SC01` nutzen `Scenario.kind = main|alternative|exception` korrekt. |
| Schrittfolge | direkt abbildbar | 14 `ScenarioStep`-Instanzen mit `stepNumber`, `kind`, `text` und Owner-Scenario sind kardinalitaetskonform. |
| Ablaufkanten | direkt abbildbar | `StepRelation` modelliert Sequenz, Alternative, Rueckfuehrung und Exception mit Source und Target. |
| Events und Conditions | direkt abbildbar | `Event.kind`, `Event.expression`, `Condition.kind` und `Condition.expression` tragen die fachlichen Ausloeser und Guards. |
| Zustandsaussagen | direkt abbildbar | 28 `StateAssertion`-Instanzen beschreiben erwartete Zustaende identifizierbarer Subjekte. |
| Agent als Subjekt | direkt abbildbar | `AgentBody` ist als `Agent` und damit als spezialisierte `Entity` modellierbar. |
| Fachliche Faehigkeiten | direkt abbildbar | `CapabilityUse`, `Capability` und `Effect` bilden Rollenwechsel, Zielhandlung und Blockadebehandlung ab. |
| Runtime-Anbindung | direkt abbildbar | `RuntimeBinding` und `RuntimeAction` bilden die technische Ausfuehrung, ohne ScenarioSteps direkt zu technisieren. |
| Validierung | direkt abbildbar | Acht `ValidationCase`-Instanzen pruefen Hauptpfad, Alternative, Exception, RuntimeBindings und Strukturregeln. |

Das wichtigste positive Ergebnis ist die durchgehende Trace-Kette. Ein Beispiel ist der Rollenwechsel:

`A-REQ-006 -> SAT-A-REQ-006 -> UC-A-01 -> A-MAIN-SC01 -> A-MAIN-S05 -> A-CU-001 -> A-CAP-ADOPT-EXECUTOR-ROLE -> A-EFF-ROLE-EXECUTOR -> A-RB-ROLE-EXECUTOR-VR -> A-RA-ROLE-SET -> A-VC-002-ROLE-BINDING`

Dieser Pfad zeigt, dass der Kern die fachliche Absicht, den Szenarioschritt, die Faehigkeit, den Effekt, die technische Bindung und die Validierung verbinden kann.

### Unscharfe Abbildung

Unscharf oder indirekt ist eine Abbildung dann, wenn sie im aktuellen Kern moeglich ist, aber nur ueber Strings, Konventionen oder dokumentierte Trace-Hinweise. Fuer A betrifft das vor allem raeumliche, zustandsbezogene und runtime-nahe Praezision.

| Konzept | Aktuelle Abbildung | Warum unscharf? |
| --- | --- | --- |
| Raumrelationen wie `inside`, `at`, `reachable`, `movingTo` | `Condition.expression` und `StateAssertion.expectedState` | Es gibt keine eigene Struktur fuer Raumrelation, Bezugssystem, Toleranz oder Geometrie. |
| Agentenrolle und Aktivitaetszustand | `StateAssertion.expectedState`, z. B. `roleState=executor` | Rollen und Aktivitaetszustaende sind keine eigenen Zustandsautomaten. |
| Zustandsuebergang des Agenten | Kombination aus `Event`, `Condition`, `ScenarioStep`, `StateAssertion` und `Effect` | Der Uebergang selbst ist kein eigenes Modellobjekt. |
| Eventquelle und Eventziel | `Event.expression`, z. B. `entered(SceneParticipant, TriggerZone)` | Quelle, Ziel, Payload, Kanal und Verbrauchsstatus sind nicht strukturiert. |
| RuntimeAction-Reihenfolge | Text in der RuntimeAction-Beschreibung | `RuntimeBinding` besitzt RuntimeActions, aber keine formale Reihenfolge oder Dependency-Kante. |
| Runtime-Schemas und Endpoints | `RuntimeAction.inputSchema`, `outputSchema`, Endpoint-Text | Schemas sind Werte, keine eigenen strukturierbaren Schemaobjekte. |
| Validation-ExpectedOutcome | StateAssertion-Listen plus Strukturregeltext | Logische Operatoren, Zeitbedingungen, Negation und Toleranzen sind nicht formal modelliert. |
| Effect-StateAssertion-Trace | Tabellen-Trace zwischen Effect und StateAssertion | Ohne Kernanpassung ist diese Verbindung dokumentarisch, nicht als Modellkante vorhanden. |

Diese Unschaerfen sind fuer die aktuelle A-Baseline akzeptabel. Sie werden erst dann kritisch, wenn ein Werkzeug aus dem Modell automatisch Raumpruefungen, Zustandsautomaten, Event-Korrelationen, Runtime-Aktionsplaene oder formale Testorakel generieren soll.

### Luecken

Fuer den aktuellen Anwendungsfall A existiert keine blockierende harte Luecke. Der Use Case kann mit dem bestehenden Kern abgebildet und validiert werden. Es gibt aber acht Lueckenkandidaten, die bei hoeherer Praezisionsanforderung relevant werden.

| Gap | Bewertung | Entscheidung |
| --- | --- | --- |
| `A-GAP-01` Strukturierte Raumsemantik | Nicht blockierend, aber fuer automatische Raumpruefung relevant. | `SpatialSemanticsModule` als Ergaenzung. |
| `A-GAP-02` Explizite Zustandsuebergaenge des Agenten | Nicht blockierend, aber fuer formale Rollen-/Aktivitaetsautomaten relevant. | `StateTransitionModule` als Ergaenzung. |
| `A-GAP-03` Strukturierte Eventquelle, Eventziel und Payload | Nicht blockierend, aber fuer Event-Korrelation und Runtime-Signalabgleich relevant. | `EventDetailModule` als Ergaenzung. |
| `A-GAP-04` Ordnung und Abhaengigkeit innerhalb einer RuntimeBinding | Nicht blockierend, aber fuer ausfuehrbare Aktionsplaene relevant. | `RuntimeExecutionModule` als Ergaenzung. |
| `A-GAP-05` Formale Testorakel | Nicht blockierend, aber fuer automatische Testauswertung relevant. | `ValidationAssertionModule` als Ergaenzung. |
| `A-GAP-06` Explizite Typisierung von Entity-Instanzen | Allgemein, kompakt und in A/B nuetzlich. | minimale Kernanpassung: `Entity.kind [0..1]`. |
| `A-GAP-07` Objekt-Affordances | Fuer A nur vorbereitend, fuer B stark relevant. | `InteractionObjectModule` als Ergaenzung. |
| `A-GAP-08` Trace-Kante von Effect zu StateAssertion | Allgemein traceability-relevant und kompakt. | minimale Kernanpassung: `Effect.evidencedBy -> StateAssertion [0..*]`. |

Die beiden Kernanpassungen sind optional und rueckwaertskompatibel. `Entity.kind [0..1]` darf fehlende Typisierung nicht als Fehler werten. `Effect.evidencedBy -> StateAssertion [0..*]` darf Effects nicht zwingen, immer einen formalen Evidence-Link zu besitzen. Alle anderen A-Gaps bleiben optionale Ergaenzungsmodule und duerfen keine direkte `ScenarioStep -> RuntimeAction`-Kante erzeugen.

### Gesamturteil

Anwendungsfall A bestaetigt den Nutzen des kompakten Kerns. Der Kern reicht aus, um den fachlichen Ablauf, die relevanten Rollen, den Agenten, die Szenarien, den Hauptpfad, die Alternative, die Exception, die Zustandsaussagen, die Capabilities, die Runtime-Anbindung und die Validierung konsistent zu beschreiben.

Die Modellierbarkeitsgrenzen liegen nicht in der Use-Case- oder Scenario-Struktur, sondern in der Tiefe bestimmter Semantiken. Raum, Zustandsuebergaenge, Eventdetails, Runtime-Orchestrierung und formale Testlogik koennen im Kern qualitativ beschrieben werden, sind aber fuer maschinenlesbare Spezialauswertungen als optionale Module besser aufgehoben. Dadurch bleibt der Kern lesbar und EAST-ADL-nah, ohne die spaetere Praezisierung zu verhindern.

Fuer die Dissertation ist die wichtigste Aussage: A ist nicht nur exemplarisch modellierbar, sondern zeigt auch, warum ein modularer Metamodellansatz notwendig ist. Ein monolithischer Kern wuerde die A-Spezifika zu frueh verallgemeinern; ein zu schwacher Kern wuerde die Trace-Kette verlieren. Die gewaehlte Loesung liegt dazwischen: kompakter Kern, minimale optionale Kernpraezisierungen und fachlich begruendete Ergaenzungsmodule.

## Abnahmekontrolle 12.4

| Kriterium aus Task 12.4 | Erfuellung |
| --- | --- |
| Abschnitt `Bewertung A` vorhanden | Der Abschnitt ist als `## Bewertung A` angelegt. |
| Direkte Abbildung getrennt | Der Abschnitt `Direkte Abbildung` benennt direkt modellierbare Bereiche. |
| Unscharfe Abbildung getrennt | Der Abschnitt `Unscharfe Abbildung` beschreibt indirekte oder stringbasierte Modellierungen. |
| Luecken getrennt | Der Abschnitt `Luecken` bewertet `A-GAP-01` bis `A-GAP-08` separat. |
| Kern und Ergaenzung unterschieden | `A-GAP-06` und `A-GAP-08` sind minimale Kernanpassungen; die uebrigen A-Gaps bleiben Ergaenzungsmodule. |
| Gesamturteil formuliert | A ist im Kern modellierbar; Praezisionsgrenzen werden modular behandelt. |

## Anwendungsfall B: Assistierte Kaffeemaschinenbedienung mit Vivian

Anwendungsfall B beschreibt die Bedienung einer virtuellen Kaffeemaschine in einer immersiven Szene. Der Visitor moechte einen Kaffeevorgang ausloesen, nutzt dafuer aber nicht nur direkt ein Objekt, sondern wird von Vivian durch die Handlung gefuehrt. Vivian erklaert die naechsten Schritte, bestaetigt erkannte Absichten, fordert bei Bedarf Korrekturen an und meldet den Abschluss. Die Kaffeemaschine selbst ist kein Actor, sondern ein Interaktionsobjekt mit beobachtbaren Zustaenden wie `cupPresent`, `selectedProgram`, `startPermission`, `brewing`, `finished` oder `safeState`.

Der Use Case `UC-B-01` heisst `Assistierte Kaffeemaschinenbedienung mit Vivian`. Sein Ziel ist, Benutzerabsicht, Vivian-Fuehrung, Objektzustand, Startfreigabe, Bruehstart und Abschluss so zu modellieren, dass der Ablauf fachlich nachvollziehbar und pruefbar bleibt. Entscheidend ist dabei die Trennung der Ebenen: Der Visitor handelt als externe Benutzerrolle, Vivian ist ein im System modellierter Assistenzagent, und die Kaffeemaschine ist das bedienbare Objekt mit eigenem Zustand. Der Use Case ist daher nicht `CoffeeMachineController.startBrewing`, sondern die vollstaendige assistierte Bedienhandlung.

### Ziel

Der Visitor soll mit Vivians Unterstuetzung eine virtuelle Kaffeemaschine bedienen koennen. Das System muss dabei folgende fachliche Fragen beantworten:

- Was will der Visitor tun?
- Welche Handlung erklaert oder fordert Vivian als naechstes an?
- Welchen Zustand meldet die Kaffeemaschine?
- Sind Tasse, Programmauswahl, Bedienbereitschaft und Startbestaetigung vorhanden?
- Darf der Bruehvorgang gestartet werden?
- Wurde der Abschluss sichtbar und verstaendlich zurueckgemeldet?

Der Anwendungsfall ist erfolgreich, wenn nach einer expliziten Bestaetigung durch den Visitor ein pruefbarer Brueh- und Abschlusszustand erreicht wird. Er ist nicht erfolgreich, wenn eine notwendige Voraussetzung nicht hergestellt werden kann; dann muss der Ablauf sicher abbrechen und Vivian muss den Grund erklaeren.

### Rollen und zentrale Entitaeten

| Element | Modellrolle | Bedeutung im Beispiel |
| --- | --- | --- |
| `ACT-B-01 Visitor` | externer `Actor` | fordert Hilfe an, platziert die Tasse, waehlt ein Programm, betaetigt Start und bestaetigt den assistierten Start. |
| `ENT-B-01 VivianAssistant` | `Agent` und spezialisierte `Entity` | fuehrt durch die Bedienung, bestaetigt erkannte Absichten, fordert Korrekturen an, erklaert Fehler und meldet den Abschluss. |
| `ENT-B-02 CoffeeMachine` | `Entity` mit Rolle `interactionObject` | stellt den bedienbaren Gegenstand dar und liefert beobachtbare Zustaende. |
| `ENT-B-03 Cup` | fachliche `Entity` | ist Voraussetzung fuer einen sinnvollen Bruehvorgang und wird ueber `cupPresent` beobachtbar. |
| `ENT-B-04 BrewingRequest` | fachliche `Entity` oder Anforderungskontext | buendelt die erkannte Absicht, Programmwahl und Startbestaetigung. |

Vivian wird bewusst nicht als externer Actor modelliert. Vivian gehoert zum System und reagiert auf Benutzerabsichten, Objektzustaende und fachliche Regeln. Ebenso wird die Kaffeemaschine nicht als RuntimeAction modelliert. Sie ist das Interaktionsobjekt, dessen Zustand im Szenario beobachtet und bewertet wird.

### Kaffeemaschine als Interaktionsobjekt

Die Kaffeemaschine besitzt im Beispiel mehrere fachliche Zustandsdimensionen. Einige davon beschreiben die Betriebsphase, andere die Voraussetzungen fuer einen Start oder die sichtbare Rueckmeldung:

| Zustandsgruppe | Beispiele | Zweck |
| --- | --- | --- |
| Betriebszustand | `idle`, `ready`, `notReady`, `brewing`, `finished`, `error`, `cancelled` | beschreibt, in welcher Phase sich das Objekt befindet. |
| Startvoraussetzungen | `cupPresent`, `waterLevel`, `selectedProgram`, `startPermission` | entscheidet, ob der Bruehstart fachlich erlaubt ist. |
| Rueckmeldungen | `readyFeedback`, `selectionFeedback`, `progressIndicator`, `completionFeedback`, `errorFeedback` | macht fuer Visitor und Vivian sichtbar, was das Objekt meldet. |
| Sicherheitszustand | `safeState`, `startPermission=blocked`, `notBrewing` | sichert Exception-Faelle ab. |

Damit ist das Objekt mehr als Dekoration in der Szene. Es traegt fachliche Wahrheit: Eine fehlende Tasse, ein niedriger Wasserstand oder eine blockierte Startfreigabe veraendern den Ablauf.

### Hauptablauf

Das Hauptszenario `SC-B-01-MAIN` beschreibt den erfolgreichen Ablauf von der Hilmeanfrage bis zur Abschlussmeldung.

| Phase | Steps | Fachlicher Inhalt |
| --- | --- | --- |
| Assistenz starten | `B-MAIN-S01` bis `B-MAIN-S03` | Der Visitor fordert Hilfe an. Vivian wechselt in den Fuehrungsmodus und erklaert, dass zuerst eine Tasse platziert werden muss. |
| Vorbereitung herstellen | `B-MAIN-S04` bis `B-MAIN-S08` | Der Visitor platziert die Tasse, die Kaffeemaschine meldet `cupPresent=true`, Vivian fuehrt zur Programmauswahl, und das Objekt bestaetigt die Wahl des Kaffeeprogramms. |
| Startabsicht pruefen | `B-MAIN-S09` bis `B-MAIN-S12` | Der Visitor betaetigt Start, Vivian bestaetigt die erkannte Bruehanforderung, das System prueft die Bedienbereitschaft, und die Kaffeemaschine meldet die Startbereitschaft. |
| Start freigeben | `B-MAIN-S13` bis `B-MAIN-S16` | Vivian fordert eine explizite Startbestaetigung an. Erst nach der Bestaetigung durch den Visitor startet das System den Bruehvorgang fachlich, und die Kaffeemaschine wechselt in `brewing`. |
| Abschluss melden | `B-MAIN-S17` bis `B-MAIN-S20` | Die Kaffeemaschine zeigt Fortschritt, wechselt nach `finished`, zeigt die Abschlussrueckmeldung, und Vivian meldet den erfolgreichen Abschluss. |

Der Ablauf verhindert damit zwei typische Fehlmodellierungen. Erstens startet Vivian die Kaffeemaschine nicht eigenmaechtig, sondern wartet auf die explizite Bestaetigung des Visitors. Zweitens wird der Bruehstart nicht direkt als technische Controlleraktion beschrieben, sondern als fachliche Systemreaktion, die spaeter ueber Capabilities und RuntimeBindings angebunden werden kann.

### Alternative: fehlende Tasse korrigieren

Das alternative Szenario `SC-B-01-ALT01` beschreibt einen korrigierbaren Zweig. Es beginnt nach `B-MAIN-S05`, wenn die Kaffeemaschine meldet, dass keine Tasse erkannt wurde:

| Step | Inhalt |
| --- | --- |
| `B-ALT-S01` | Die Kaffeemaschine meldet `cupPresent=false`. |
| `B-ALT-S02` | Vivian erklaert, dass die Tasse korrekt platziert oder neu ausgerichtet werden muss. |
| `B-ALT-S03` | Der Visitor korrigiert die Tassenposition. |
| `B-ALT-S04` | Die Kaffeemaschine meldet `cupPresent=true`. |

Danach kehrt der Ablauf vor `B-MAIN-S06` in den Hauptpfad zurueck. Diese Alternative ist kein `Extend`-Use-Case und benoetigt keinen ExtensionPoint. Sie ist ein fachlicher Korrekturzweig innerhalb desselben Use Case.

### Exception: Bereitschaftspruefung schlaegt fehl

Das Exception-Szenario `SC-B-01-EX01` beschreibt einen nicht direkt korrigierbaren Fehler im laufenden Ablauf. Es beginnt nach `B-MAIN-S11`, wenn die Bereitschaftspruefung fehlschlaegt, zum Beispiel weil der Wasserstand zu niedrig ist:

| Step | Inhalt |
| --- | --- |
| `B-EX-S01` | Die Kaffeemaschine meldet `waterLevel=low` und keine Startbereitschaft. |
| `B-EX-S02` | Vivian erklaert, dass der Bruehstart wegen fehlender Startbereitschaft nicht ausgefuehrt wird. |
| `B-EX-S03` | Die Kaffeemaschine bleibt startblockiert und in einem sicheren nicht bruehenden Zustand. |
| `B-EX-S04` | Vivian schliesst den Ausnahmefall ab und laesst den Hauptpfad nicht weiterlaufen. |

Im Unterschied zur Alternative gibt es hier keine Rueckfuehrung zu `B-MAIN-S12`. Der Bruehvorgang startet nicht. Das gewuenschte Ergebnis ist ein sicherer, erklaerter Nicht-Start.

### Zusammenfassung

Anwendungsfall B macht deutlich, dass interaktive VR-Objekte nicht nur als 3D-Assets beschrieben werden duerfen. Die Kaffeemaschine ist ein zustandsbehaftetes Interaktionsobjekt; Vivian ist ein Assistenzagent mit fachlichem Dialog- und Fuehrungsverhalten; der Visitor bleibt die externe Benutzerrolle. Das Szenario prueft, ob diese drei Perspektiven sauber zusammenspielen: Benutzerabsicht, Assistenzreaktion und Objektzustand.

Die Beschreibung bleibt bewusst auf der Use-Case- und Scenario-Ebene. Capabilities, RuntimeBindings und RuntimeActions werden erst im Mapping beschrieben. Dadurch bleibt der Anwendungsfall fachlich lesbar und vermeidet eine direkte technische Kurzschaltung.

## Abnahmekontrolle 12.5

| Kriterium aus Task 12.5 | Erfuellung |
| --- | --- |
| Abschnitt zu B vorhanden | Der Abschnitt `Anwendungsfall B: Assistierte Kaffeemaschinenbedienung mit Vivian` ist angelegt. |
| Vivian enthalten | Vivian wird als Assistenzagent mit Fuehrung, Rueckfrage, Fehlererklaerung und Abschlussmeldung beschrieben. |
| Kaffeemaschine enthalten | Die Kaffeemaschine wird als Interaktionsobjekt mit beobachtbaren Zustaenden beschrieben. |
| Hauptablauf enthalten | `SC-B-01-MAIN` ist in fuenf Phasen von `B-MAIN-S01` bis `B-MAIN-S20` beschrieben. |
| Alternative enthalten | `SC-B-01-ALT01` beschreibt die korrigierbare fehlende Tasse mit Rueckkehr in den Hauptpfad. |
| Exception enthalten | `SC-B-01-EX01` beschreibt die fehlgeschlagene Bereitschaftspruefung ohne Rueckkehr in den Hauptpfad. |
| Ohne Diagramm verstaendlich | Rollen, Ziel, Objektzustand, Hauptpfad, Alternative und Exception werden textuell erklaert. |

## Mapping B

Das Mapping von Anwendungsfall B zeigt, wie eine assistierte Objektbedienung mit Vivian in den kompakten Metamodellkern eingeordnet wird. Die wichtigste Modellierungsentscheidung lautet: Rollen, Objektzustand, fachliche Faehigkeiten und technische Bindungen duerfen nicht vermischt werden.

Der Visitor ist die externe Use-Case-Rolle. Vivian ist ein modellierter Assistenzagent im System. Die Kaffeemaschine ist eine fachliche Entity und zugleich das Interaktionsobjekt. Der Ablauf selbst liegt auf der Scenario-Ebene. Objektzustaende werden ueber Events, Conditions und StateAssertions beschrieben. Systemische Reaktionen werden ueber CapabilityUse und Capability angebunden. Technische Ausfuehrung beginnt erst bei RuntimeBinding und RuntimeAction.

### Requirements, UseCase und Rollen

Anwendungsfall B besitzt 18 fachliche Requirements `B-REQ-001` bis `B-REQ-018`. Sie beschreiben unter anderem die Actor/Agent-Trennung, Vivians Fuehrung, die Tassenbedingung, Programmauswahl, Bereitschaftspruefung, Startbestaetigung, sicheren Exception-Abschluss und die verbotene technische Kurzschaltung.

Der Use Case `UC-B-01` ist die fachliche Klammer. Er beschreibt nicht einen einzelnen Startaufruf, sondern die vollstaendige assistierte Kaffeemaschinenbedienung mit Hauptpfad, Alternative und Exception.

| Modellklasse | B-Instanz | Bedeutung |
| --- | --- | --- |
| `Requirement` | `B-REQ-001` bis `B-REQ-018` | fachliche Anforderungen an assistierte Bedienung, Objektzustand, Safety und Traceability. |
| `UseCase` | `UC-B-01` | assistierte Kaffeemaschinenbedienung mit Vivian. |
| `Actor` | `ACT-B-01 Visitor` | externe Benutzerrolle; nur diese Rolle wird in `actorIntent`-Schritten als `performedBy` gesetzt. |
| `Agent` | `ENT-B-01 VivianAssistant` | systeminterner Assistenzagent; Vivian ist keine externe Actor-Rolle in dieser Baseline. |
| `Entity` | `ENT-B-02 CoffeeMachine`, `ENT-B-03 Cup`, `ENT-B-04 BrewingRequest` | fachliche Objekte und Zustandskontexte des Use Case. |

Die Instanz `ACT-B-01 Visitor` interagiert mit `UC-B-01`. `ENT-B-01 VivianAssistant` wird nicht als Actor modelliert, weil Vivian innerhalb der betrachteten assistierten VR-Interaktion liegt. Die Regel fuer `ScenarioStep.performedBy` bleibt dadurch eindeutig: Nur Benutzerhandlungen des Visitors erhalten eine Actor-Referenz; Vivian- und Systemschritte bleiben `systemResponse`.

Formale `Satisfy`-Instanzen wurden fuer B noch nicht angelegt. Das ist zulaessig, weil `Satisfy` optional ist und die XOR-Regel erst bei konkreten Satisfy-Instanzen greift. Die Requirement-Abdeckung wird in B derzeit ueber ValidationCases und Rueckverweise in den Artefakten nachgewiesen.

### Scenario-Ebene

`UC-B-01` besitzt genau drei Scenarios:

| Scenario | `Scenario.kind` | Inhalt |
| --- | --- | --- |
| `SC-B-01-MAIN` | `main` | erfolgreicher assistierter Bedienablauf von `B-MAIN-S01` bis `B-MAIN-S20`. |
| `SC-B-01-ALT01` | `alternative` | fehlende oder nicht erkannte Tasse wird korrigiert und der Ablauf kehrt vor `B-MAIN-S06` zurueck. |
| `SC-B-01-EX01` | `exception` | fehlgeschlagene Bereitschaftspruefung verhindert den Bruehstart und endet sicher ohne Rueckkehr in den Hauptpfad. |

Damit ist die Main-Scenario-Invariante erfuellt: `UC-B-01` besitzt genau ein `Scenario.kind = main`. Alternative und Exception sind keine eigenen Use Cases und keine `Extend`-Instanzen. Sie sind Ablaufvarianten innerhalb desselben fachlichen Use Case.

Die 28 `ScenarioStep`-Instanzen teilen sich in drei Arten:

| `ScenarioStep.kind` | Anzahl | Modellierungsregel |
| --- | ---: | --- |
| `actorIntent` | 6 | nur diese Steps erhalten `performedBy = ACT-B-01 Visitor`. |
| `systemResponse` | 11 | erhalten keine Actor-Referenz, sondern je eine `CapabilityUse`. |
| `environmentObservation` | 11 | beschreiben beobachtete Objekt- oder Umweltzustaende ueber Events und StateAssertions. |

Die Ablaufkanten liegen in `StepRelation`. Der Hauptpfad besitzt 19 lineare `sequence`-Relationen. Die Alternative wird ueber `B-ALT-R-IN01` betreten und ueber `B-ALT-R-OUT01` in den Hauptpfad zurueckgefuehrt. Die Exception wird ueber `B-EX-R-IN01` betreten und besitzt keine Rueckfuehrung.

### Objektzustand

Der Objektzustand der Kaffeemaschine wird nicht als RuntimeAction und nicht als Actor-Verhalten modelliert. Er wird ueber `Condition`, `Event` und `StateAssertion` abgebildet.

| Modellklasse | B-Nutzung | Beispiel |
| --- | --- | --- |
| `Event` | fachlich beobachtbare Ausloeser oder Signale | `B-E04 TasseErkannt`, `B-E09 StartbereitschaftGemeldet`, `B-EX-E01 BereitschaftFehlgeschlagen`. |
| `Condition` | Preconditions, Guards und Postconditions | `B-MAIN-G06` prueft Tasse, Wasser, Programm und Maschinenzustand; `B-EX-G01` aktiviert die Exception. |
| `StateAssertion` | erwartete oder beobachtete Zustaende identifizierbarer Subjekte | `SA-B-CM-CUP-PRESENT`, `SA-B-CM-START-PERMISSION`, `SA-B-CM-BREWING`, `SA-B-CM-SAFE`. |

Die Kaffeemaschine `ENT-B-02 CoffeeMachine` ist dabei `subjectRef` vieler StateAssertions. Das ist entscheidend, weil Erfolg oder Fehler nicht nur textuell behauptet werden. Der erfolgreiche Pfad endet mit beobachtbaren Aussagen wie `CoffeeMachine.lifecycleState = finished` und `CoffeeMachine.completionFeedback = visible`. Der Exception-Pfad endet mit Aussagen wie `CoffeeMachine.startPermission = blocked`, `CoffeeMachine.safeState = true` und `CoffeeMachine.lifecycleState != brewing`.

Die Zustandsaussagen sind orthogonal. `Cup.state = placed` ist nicht dasselbe wie `CoffeeMachine.cupPresent = true`. Ebenso ist `CoffeeMachine.lifecycleState = brewing` nicht dasselbe wie `CoffeeMachine.progressIndicator = visible`. Diese Trennung verhindert, dass ein einzelnes Objektflag mehrere fachliche Nachweise ersetzt.

### Capability-Ebene

Jeder systemische Schritt aus B ist ueber eine `CapabilityUse` an genau eine fachliche `Capability` gebunden. Actor-Intents und Environment-Observations erhalten keine CapabilityUse, weil sie externe Benutzerhandlungen oder beobachtete Zustaende sind.

| Bereich | CapabilityUse | Capability | Fachlicher Zweck |
| --- | --- | --- | --- |
| Vivian-Fuehrung | `B-CU-001`, `B-CU-002`, `B-CU-003` | `CAP-B-VIVIAN-ENTER-GUIDANCE`, `CAP-B-VIVIAN-GUIDE-CUP`, `CAP-B-VIVIAN-GUIDE-PROGRAM` | Vivian wechselt in den Fuehrungsmodus und gibt Bedienhinweise. |
| Request und Freigabe | `B-CU-004`, `B-CU-006` | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST`, `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | Vivian bestaetigt die Bruehanforderung und fordert die explizite Startbestaetigung an. |
| Kaffeemaschine | `B-CU-005`, `B-CU-007` | `CAP-B-CHECK-MACHINE-READY`, `CAP-B-START-BREWING` | Objektbezogene fachliche Pruefung und fachlicher Bruehstart. |
| Abschluss | `B-CU-008` | `CAP-B-VIVIAN-REPORT-COMPLETION` | Vivian meldet den erfolgreichen Abschluss. |
| Alternative | `B-CU-009` | `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | Vivian fuehrt die Tassenkorrektur. |
| Exception | `B-CU-010`, `B-CU-011` | `CAP-B-VIVIAN-EXPLAIN-ERROR`, `CAP-B-VIVIAN-CLOSE-EXCEPTION` | Vivian erklaert die Fehlerursache und schliesst den Ausnahmefall ab. |

Die elf Capabilities besitzen jeweils Preconditions und mindestens einen `Effect`. Die Effects bleiben fachlich, zum Beispiel `B-EFF-READINESS-RESULT-PRODUCED`, `B-EFF-BREWING-START-ISSUED` oder `B-EFF-ERROR-EXPLAINED`. Sie enthalten keine Endpoints, Topics, Toolaufrufe oder Schemas.

Ein wichtiger Sonderfall ist `CAP-B-CHECK-MACHINE-READY`. Diese Capability besitzt fachlich zwei erlaubte Ausgaenge: positiv in den Hauptpfad mit Startfreigabe oder negativ in den Exception-Pfad mit blockiertem Start. Der ScenarioStep `B-MAIN-S11` wird dadurch nicht technisch, sondern bleibt eine fachliche Bereitschaftspruefung.

### RuntimeBinding und RuntimeAction

Die technische Ebene beginnt erst bei `RuntimeBinding`. Jede der elf Capabilities besitzt in der B-Baseline genau eine RuntimeBinding. Jede RuntimeBinding referenziert genau eine Capability und besitzt zwei oder drei RuntimeActions.

| RuntimeBinding | Capability | Runtime-Kontext | RuntimeActions |
| --- | --- | --- | ---: |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `CAP-B-VIVIAN-ENTER-GUIDANCE` | Vivian und VR-Interaktion | 2 |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `CAP-B-VIVIAN-GUIDE-CUP` | Vivian und VR-Interaktion | 2 |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `CAP-B-VIVIAN-GUIDE-PROGRAM` | Vivian und VR-Interaktion | 2 |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | Vivian und Trace | 2 |
| `B-RB-COFFEE-READINESS-CHECK` | `CAP-B-CHECK-MACHINE-READY` | Kaffeemaschinenadapter, VR und Trace | 3 |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | Vivian und VR-Interaktion | 2 |
| `B-RB-COFFEE-START-BREWING` | `CAP-B-START-BREWING` | Kaffeemaschinenadapter, VR und Trace | 3 |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `CAP-B-VIVIAN-REPORT-COMPLETION` | Vivian und VR-Interaktion | 2 |
| `B-RB-VIVIAN-CUP-CORRECTION` | `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | Vivian und VR-Interaktion | 2 |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `CAP-B-VIVIAN-EXPLAIN-ERROR` | Vivian, VR und Trace | 3 |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `CAP-B-VIVIAN-CLOSE-EXCEPTION` | Vivian und Trace | 2 |

Die 25 RuntimeActions enthalten die technischen Endpoints, Topics und optionalen Input-/Output-Schemas. Das ist genau die Ebene, auf der solche Details erlaubt sind. Beispiele sind `B-RA-CM-EVALUATE-READINESS`, `B-RA-CM-REQUEST-BREWING-START`, `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION` oder `B-RA-TRACE-SYNC-EXCEPTION-CLOSED`.

Der erlaubte Pfad bleibt damit:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

Verboten und in B nicht vorhanden sind:

`ScenarioStep -> RuntimeAction`

`CapabilityUse -> RuntimeAction`

`Capability -> technischer Endpoint`

### Beispielpfad im Mapping

Der fachliche Bruehstart im Hauptpfad zeigt die Trennung besonders klar:

`B-MAIN-S15 -> B-CU-007 -> CAP-B-START-BREWING -> B-EFF-BREWING-START-ISSUED -> B-RB-COFFEE-START-BREWING -> B-RA-CM-REQUEST-BREWING-START / B-RA-CM-SYNC-BREWING-STATE / B-RA-TRACE-SYNC-START-OUTCOME -> SA-B-BREWING-START-ISSUED / SA-B-CM-BREWING -> B-VC-005-CONFIRMATION-AND-START`

Dieser Pfad zeigt, dass `B-MAIN-S15` nicht direkt eine technische Maschinenfunktion aufruft. Der ScenarioStep benennt nur die fachliche Systemreaktion. Die Capability beschreibt, was fachlich geleistet wird. Die RuntimeBinding ordnet diese Faehigkeit einer technischen Laufzeit zu. Erst die RuntimeActions enthalten konkrete technische Ausfuehrungsdetails. Der ValidationCase prueft anschliessend, ob die erwarteten StateAssertions eintreten.

### ValidationCase

B besitzt zehn `ValidationCase`-Instanzen. Sie decken Struktur, Hauptpfad, Alternative, Exception, RuntimeBinding-Abdeckung und die verbotene technische Kurzschaltung ab.

| ValidationCase-Gruppe | Instanzen | Zweck |
| --- | --- | --- |
| Struktur | `B-VC-001`, `B-VC-009`, `B-VC-010` | Actor/Agent/Entity-Trennung, keine Include/Extend-Fehlverwendung, keine direkte RuntimeAction-Kante, RuntimeCoverage. |
| Hauptpfad | `B-VC-002` bis `B-VC-006` | Assistenzstart, Tasse, Programm, Readiness, Startbestaetigung, Bruehstart und Abschluss. |
| Alternative | `B-VC-007` | fehlende Tasse mit Korrektur und Rueckkehr in den Hauptpfad. |
| Exception | `B-VC-008` | fehlgeschlagene Bereitschaftspruefung, blockierter Start, sicherer Zustand und Vivian-Erklaerung. |

ValidationCases duerfen RuntimeBindings pruefen oder ausfuehren. Sie besitzen diese Bindings aber nicht. RuntimeActions erscheinen in ValidationCases nur als Stimulusbeschreibung und bleiben formal unter ihrer RuntimeBinding.

### Bewusst ausgelassene zentrale Klassen

| Metamodellklasse | Status in B | Begruendung |
| --- | --- | --- |
| `Satisfy` | noch nicht formal instanziiert | B dokumentiert Requirement-Abdeckung ueber ValidationCases; formale Satisfy-Konsolidierung bleibt offen und verletzt keine Kardinalitaet. |
| `ExtensionPoint` | nicht instanziiert | Kein formales Extend in der B-Baseline. |
| `Include` | nicht instanziiert | Die Bereitschaftspruefung ist ein gueltiger Include-Kandidat fuer spaetere Wiederverwendung, wird hier aber als ScenarioStep plus Capability modelliert. |
| `Extend` | nicht instanziiert | Alternative und Exception sind keine optionalen Zusatz-Use-Cases mit ExtensionPoint. |
| `ParallelGroup` | nicht instanziiert | B ist sequenziell modellierbar; keine nebenlaeufigen Steps muessen gruppiert werden. |
| `FunctionBehavior` | nicht instanziiert | Keine EAST-ADL-FunctionBehavior-Bruecke erforderlich; Capabilities und RuntimeBindings reichen fuer die aktuelle Abbildung. |
| `RandomVariable` | nicht instanziiert | B nutzt keine probabilistischen Bedingungen. |

### Klassenabdeckung fuer B

| Zentrale Klasse | B-Abbildung |
| --- | --- |
| `RequirementsModel` | B-Requirements-Kontext mit `B-REQ-001` bis `B-REQ-018` und `UC-B-01`. |
| `Requirement` | `B-REQ-001` bis `B-REQ-018`. |
| `UseCase` | `UC-B-01`. |
| `Actor` | `ACT-B-01 Visitor`. |
| `Satisfy` | begruendet noch nicht formal instanziiert. |
| `ExtensionPoint` | begruendet ausgelassen. |
| `Include` | begruendet ausgelassen; Readiness-Use-Case nur Kandidat. |
| `Extend` | begruendet ausgelassen; optionale Vivian-Erklaerungen nur Kandidaten. |
| `Scenario` | `SC-B-01-MAIN`, `SC-B-01-ALT01`, `SC-B-01-EX01`. |
| `ScenarioStep` | 28 Steps: 20 Main, 4 Alternative, 4 Exception. |
| `StepRelation` | 28 formale Relationen: 19 Main, 5 Alternative, 4 Exception. |
| `ParallelGroup` | begruendet ausgelassen. |
| `Event` | 24 Events, unter anderem `B-E01`, `B-E04`, `B-E09`, `B-EX-E01`. |
| `Condition` | 34 Conditions, unter anderem `B-MAIN-G06`, `B-MAIN-G08`, `B-EX-G01`. |
| `StateAssertion` | 30 StateAssertions fuer Vivian, CoffeeMachine, Cup und BrewingRequest. |
| `Entity` | `ENT-B-01 VivianAssistant`, `ENT-B-02 CoffeeMachine`, `ENT-B-03 Cup`, `ENT-B-04 BrewingRequest`. |
| `Agent` | `ENT-B-01 VivianAssistant`. |
| `CapabilityUse` | `B-CU-001` bis `B-CU-011`. |
| `Capability` | elf B-Capabilities von Vivian-Guide bis CoffeeMachine-Start. |
| `Effect` | elf fachliche Effects, jeweils einer pro Capability. |
| `FunctionBehavior` | begruendet ausgelassen. |
| `RuntimeBinding` | elf RuntimeBindings, je eine pro Capability. |
| `RuntimeAction` | 25 RuntimeActions unter den elf RuntimeBindings. |
| `ValidationCase` | `B-VC-001` bis `B-VC-010`. |
| `RandomVariable` | begruendet ausgelassen. |

## Abnahmekontrolle 12.6

| Kriterium aus Task 12.6 | Erfuellung |
| --- | --- |
| Abschnitt `Mapping B` vorhanden | Der Abschnitt ist als `## Mapping B` angelegt. |
| Rollen klar getrennt | `ACT-B-01 Visitor`, `ENT-B-01 VivianAssistant` und `ENT-B-02 CoffeeMachine` werden als Actor, Agent/Entity und Interaktionsobjekt getrennt. |
| Objektzustand klar getrennt | CoffeeMachine-Zustaende werden ueber Events, Conditions und StateAssertions modelliert, nicht als RuntimeAction. |
| Capability klar getrennt | Systemische Steps nutzen `CapabilityUse -> Capability`; Capabilities enthalten Intent, Preconditions und Effects, aber keine technischen Endpoints. |
| RuntimeBinding klar getrennt | RuntimeBindings referenzieren je eine Capability und besitzen RuntimeActions; technische Details liegen erst in RuntimeActions. |
| Keine technische Kurzschaltung | Der erlaubte Pfad `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction` ist beschrieben und direkte RuntimeAction-Kanten sind ausgeschlossen. |
| Zentrale Klassen abgedeckt oder begruendet ausgelassen | Die Klassenabdeckung fuer B listet genutzte und bewusst ausgelassene Kernklassen. |

## Bewertung B

Anwendungsfall B ist mit dem kompakten Kernmetamodell vollstaendig beschreibbar. Es gibt keine Pflichtkardinalitaet, die verletzt wird, und keine zentrale Invariante, die fuer die aktuelle B-Baseline bricht. Visitor, Vivian, Kaffeemaschine, Hauptpfad, Alternative, Exception, Objektzustaende, Capabilities, RuntimeBindings, RuntimeActions und ValidationCases koennen konsistent modelliert werden.

Die Bewertung ist trotzdem nicht trivial. B zeigt deutlicher als A, wo der kompakte Kern bewusst endet: bei strukturierter Dialogsemantik fuer Vivian, bei objektseitigen Affordances der Kaffeemaschine, bei formalen Zustandsautomaten, bei Readiness-Regeln, bei Runtime-Orchestrierung und bei feiner Traceability. Diese Punkte blockieren die aktuelle Modellierung nicht, werden aber relevant, sobald aus dem Modell automatisch Interaktionsobjekte, Vivian-Dialoge, Tests, Runtimeplaene oder Safety-nahe Nachweise generiert werden sollen.

### Direkte Abbildung

Direkt abbildbar sind alle Elemente, die ohne neue Metamodellklasse und ohne semantischen Umweg auf vorhandene Klassen, Attribute oder Beziehungen gemappt werden koennen.

| Bereich | Bewertung | Begruendung |
| --- | --- | --- |
| Requirements und UseCase | direkt abbildbar | `B-REQ-001` bis `B-REQ-018` und `UC-B-01` passen in RequirementsModel, Requirement und UseCase. |
| Rollen und Instanzen | direkt abbildbar | `ACT-B-01 Visitor` ist Actor; `ENT-B-01 VivianAssistant` ist Agent/Entity; `ENT-B-02 CoffeeMachine` ist Entity. |
| Scenario-Struktur | direkt abbildbar | `SC-B-01-MAIN`, `SC-B-01-ALT01` und `SC-B-01-EX01` nutzen `Scenario.kind = main|alternative|exception` korrekt. |
| Schrittfolge und Zweige | direkt abbildbar | 28 ScenarioSteps und 28 formale StepRelations decken Hauptpfad, Alternative und Exception ab. |
| Events, Conditions und StateAssertions | direkt abbildbar | Benutzerereignisse, Vivian-Signale, Kaffeemaschinenereignisse, Guards und erwartete Zustaende sind modelliert. |
| Fachliche Faehigkeiten | direkt abbildbar | Elf CapabilityUses referenzieren elf Capabilities mit Effects. |
| Runtime-Anbindung | direkt abbildbar | Elf RuntimeBindings und 25 RuntimeActions bilden die technische Ebene ohne direkte Step-Abkuerzung. |
| Validierung | direkt abbildbar | Zehn ValidationCases pruefen Struktur, Hauptpfad, Alternative, Exception und RuntimeCoverage. |

Der wichtigste direkte Trace fuer B ist der assistierte Bruehstart:

`B-MAIN-S15 -> B-CU-007 -> CAP-B-START-BREWING -> B-EFF-BREWING-START-ISSUED -> B-RB-COFFEE-START-BREWING -> B-RA-CM-REQUEST-BREWING-START -> SA-B-CM-BREWING -> B-VC-005-CONFIRMATION-AND-START`

Dieser Pfad ist gueltig, weil der ScenarioStep fachlich bleibt und erst die RuntimeAction technische Ausfuehrungsdetails enthaelt.

### Vivian-spezifische Bewertung

Vivian ist in der B-Baseline korrekt als `Agent` und damit als spezialisierte `Entity` modelliert. Vivian ist kein externer Actor, solange die Systemgrenze die assistierte VR-Interaktion umfasst. Der Visitor bleibt die externe Rolle; Vivian-Reaktionen sind `systemResponse`-Schritte und werden ueber `CapabilityUse -> Capability` angebunden.

| Vivian-Aspekt | Aktuelle Abbildung | Bewertung |
| --- | --- | --- |
| Vivian als Systeminstanz | `ENT-B-01 VivianAssistant` als Agent/Entity | fuer die Baseline direkt und korrekt abbildbar. |
| Vivian-Fuehrungsmodus | `SA-B-VIVIAN-GUIDING`, `CAP-B-VIVIAN-ENTER-GUIDANCE` | ausreichend fuer beobachtbaren Assistenzzustand. |
| Tassen- und Programmanleitung | `CAP-B-VIVIAN-GUIDE-CUP`, `CAP-B-VIVIAN-GUIDE-PROGRAM` | fachlich sauber als Capability, nicht als RuntimeAction. |
| Startbestaetigungsfrage | `CAP-B-VIVIAN-REQUEST-CONFIRMATION`, `SA-B-VIVIAN-AWAITING-CONFIRMATION` | ausreichend fuer Baseline; Antwortpolitik bleibt grob. |
| Fehlererklaerung | `CAP-B-VIVIAN-EXPLAIN-ERROR`, `B-EFF-ERROR-EXPLAINED` | fachlich abbildbar; Erklaerstrategie bleibt nicht strukturiert. |
| Abschlussmeldung | `CAP-B-VIVIAN-REPORT-COMPLETION` | direkt abbildbar. |
| Technische Ausgabe | Vivian-/VR-RuntimeActions wie `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE` | richtig auf RuntimeAction-Ebene eingeordnet. |

Unscharf bleibt Vivians Dialogverhalten. Der Kern kann modellieren, dass Vivian fuehrt, bestaetigt, fragt, erklaert oder abschliesst. Er kann aber nicht formal modellieren, welcher Dialogakt vorliegt, welche genaue Guidance formuliert wird, welche Modalitaet genutzt wird, welche Antwortoptionen erlaubt sind, wie Wiederholung, Ablehnung, Timeout oder Personalisierung funktionieren.

Fuer die B-Baseline reicht das aus. Fuer eine generierbare Vivian-Interaktion waere ein optionales `AssistantInteractionModule` sinnvoll. Dieses Modul sollte Dialogakte, GuidanceContent, PresentationMode, ResponseOptions und InteractionPolicy beschreiben, ohne Vivian zu einem Actor zu machen und ohne die Kernkette zu ersetzen.

### Objekt-spezifische Bewertung

Die Kaffeemaschine ist in der B-Baseline korrekt als fachliche `Entity` mit `Entity.kind = asset` und semantischer Rolle `interactionObject` modelliert. Sie ist weder Actor noch Agent noch RuntimeAction. Ihr Verhalten wird ueber Events, Conditions, StateAssertions, Capabilities und RuntimeBindings abgebildet.

| Objekt-Aspekt | Aktuelle Abbildung | Bewertung |
| --- | --- | --- |
| Objektidentitaet | `ENT-B-02 CoffeeMachine` als Entity | direkt und korrekt abbildbar. |
| Tasse vorhanden | `B-E04`, `B-MAIN-G03`, `SA-B-CM-CUP-PRESENT` | direkt pruefbar. |
| Programmauswahl | `B-E05`, `B-E06`, `SA-B-CM-PROGRAM-COFFEE` | direkt pruefbar. |
| Readiness | `B-MAIN-G06`, `CAP-B-CHECK-MACHINE-READY`, `B-EFF-READINESS-RESULT-PRODUCED` | fachlich abbildbar, aber Regelstruktur bleibt grob. |
| Startfreigabe | `SA-B-CM-START-PERMISSION`, `B-MAIN-G08` | direkt pruefbar. |
| Bruehzustand | `SA-B-CM-BREWING`, `SA-B-CM-FINISHED` | direkt als StateAssertion abbildbar. |
| Feedback | `readyFeedback`, `progressIndicator`, `completionFeedback` als Events/StateAssertions | direkt sichtbar, aber Medium und Dauer bleiben unstrukturiert. |
| Sicherer Nicht-Start | `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE`, `SA-B-CM-NOT-BREWING` | direkt abbildbar und validierbar. |

Unscharf bleiben die objektseitigen Bedienmoeglichkeiten. Starttaste, Tassenbereich, Programmauswahlfeld, Feedbackanzeige, Aktivierungsbedingungen und erlaubte Manipulationen stehen derzeit in `Event.expression`, `Condition.expression`, StateAssertions und RuntimeSchemas. Das reicht, um den Ablauf zu verstehen und zu validieren. Es reicht nicht, wenn aus dem Modell automatisch VR-Hotspots, Bedienflaechen, Affordance-Constraints oder interaktive Objektoberflaechen generiert werden sollen.

Fuer eine praezise Interaktionsobjektmodellierung waere ein optionales `InteractionObjectModule` sinnvoll. Es sollte an `Entity`, `Event`, `Condition`, `StateAssertion` und `Capability` andocken und Konzepte wie `InteractionObject`, `ControlSurface`, `InteractionZone`, `Affordance`, `ManipulationKind`, `activationCondition`, `producesEvent` und `resultingState` modellieren.

### Unscharfe Abbildung

Die unscharfen Punkte sind keine aktuellen Modellierungsfehler. Sie markieren Stellen, an denen der Kern mit Strings, Tabellenkonventionen oder dokumentierten Trace-Hinweisen arbeitet.

| Problemtyp | Betroffene B-Elemente | Bewertung |
| --- | --- | --- |
| Dialog- und Guidance-Semantik | Vivian-Modus, GuidanceTopic, Fehlererklaerung, Startbestaetigung | fuer Baseline ausreichend, fuer formalen Dialog zu grob. |
| Affordances | Starttaste, Tassenbereich, Programmauswahl, Bestaetigungsmoeglichkeit | fuer Ablaufbeschreibung ausreichend, fuer generierbare Bedienobjekte zu grob. |
| Objektzustandsautomat | CoffeeMachine-Lifecycle, BrewingRequest-Lifecycle, safeState | StateAssertions reichen fuer erwartete Zustaende, nicht fuer formale Transitionen. |
| Readiness-Regeln | Wasserstand, Tasse, Programm, Maschinenzustand, Startpermission | als Guard/Capability abbildbar, aber nicht als geordnetes RuleSet. |
| Eventdetails | Quelle, Ziel, Payload, Kanal und Korrelation | in `Event.expression` abbildbar, aber nicht strukturiert. |
| Runtime-Orchestrierung | Reihenfolge, Dependencies, Retry, Timeout, Schemas und Profile | dokumentierbar, aber nicht als ausfuehrbarer Runtimeplan formalisiert. |
| Trace-Feinstruktur | Effect zu StateAssertion, ValidationOutcome zu StateAssertion | nachvollziehbar dokumentiert, aber nicht vollstaendig als Kante modelliert. |

Diese Unschaerfen zeigen, warum ein modularer Ansatz sinnvoller ist als ein grosser Kern. Die B-Baseline bleibt gueltig; Spezialisierungen koennen dort ergaenzt werden, wo sie wirklich gebraucht werden.

### Luecken

Fuer den aktuell abgegrenzten Anwendungsfall B gibt es keine blockierende harte Luecke. Das bedeutet: Kein zentrales B-Element ist voellig unmodellierbar. Es gibt aber zwoelf Lueckenkandidaten, die bei hoeherer Praezisionsanforderung relevant werden.

| Gap | Bewertung fuer aktuelle B-Baseline | Naheliegende Behandlung |
| --- | --- | --- |
| `B-GAP-01` Interaktionsobjekt-Affordances | nicht blockierend, aber fuer generierbare Kaffeemaschinenbedienung hoch relevant | `InteractionObjectModule`. |
| `B-GAP-02` Objektzustandsautomat | nicht blockierend, aber fuer erlaubte/verbotene Uebergaenge relevant | `StateTransitionModule`. |
| `B-GAP-03` Vivian-Dialog und GuidanceContent | nicht blockierend, aber fuer maschinenlesbare Assistenz zentral | `AssistantInteractionModule`. |
| `B-GAP-04` Benutzerbestaetigung und Autorisierung | fuer positiven Baseline-Pfad ausreichend, bei Timeout/Ablehnung relevant | Authorization-/Recovery-Ergaenzung. |
| `B-GAP-05` Readiness-Regeln | als Guard/Capability abbildbar, bei automatischer Diagnose relevant | `DecisionRuleModule`. |
| `B-GAP-06` Eventquelle, Ziel und Payload | als Expression abbildbar, bei Event-Korrelation relevant | `EventDetailModule`. |
| `B-GAP-07` RuntimeAction-Reihenfolge und Fehlerbehandlung | dokumentiert, bei Ausfuehrbarkeit relevant | `RuntimeExecutionModule`. |
| `B-GAP-08` RuntimeProfile und Schemas | dokumentiert, bei Codegenerierung relevant | RuntimeProfile-/Schema-Ergaenzung. |
| `B-GAP-09` Effect-Nachweis durch StateAssertions | nicht blockierend, aber allgemein traceability-relevant | minimaler Kernkandidat `Effect.evidencedBy -> StateAssertion [0..*]`; ValidationOutcome als Modul. |
| `B-GAP-10` Cross-Scenario Entry/Return | mit StepRelation ausreichend, bei Variantenanalyse relevant | optionales `ScenarioVariationModule`. |
| `B-GAP-11` Safety-/Hazard-Argumentation | sicherer Nicht-Start abbildbar, SafetyCase fehlt | optionales `SafetyArgumentModule`. |
| `B-GAP-12` Abbruch, Timeout und Recovery | weitere Scenarios moeglich, Policy nicht formal | optionales Recovery-/Temporal-Modul bei erweitertem Scope. |

Nur `B-GAP-09` besitzt in B eine klare Tendenz zu einer minimalen Kernpraezisierung, und auch dort nur die optionale Trace-Kante von `Effect` zu `StateAssertion`. Die uebrigen B-Gaps sind wichtig, aber zu domaenen-, dialog-, objekt-, safety- oder runtime-spezifisch fuer den Kern.

### Gesamturteil

B bestaetigt den kompakten Kern, weil der gesamte fachliche Ablauf ohne Kardinalitaetsverletzung abbildbar ist. Gleichzeitig zeigt B, dass der Kern nicht versuchen sollte, jede Detailsemantik selbst zu tragen. Vivian-Dialog, Interaktionsobjekt-Affordances, Readiness-Regeln, Zustandsautomaten, Eventpayloads, Runtime-Orchestrierung und Safety-Argumentation sind echte Praezisierungsthemen, aber sie gehoeren ueberwiegend in optionale Ergaenzungsmodule.

Fuer die Dissertation ist die zentrale Aussage: B ist nicht ein Gegenbeispiel gegen den Kern, sondern ein Belastungstest fuer seine Modularitaet. Der Kern stellt die durchgehende Trace-Kette bereit. Die spezialisierten Module machen spaeter die Stellen maschinenlesbar, die fuer eine bestimmte Toolchain, Runtime oder Validierungstiefe wirklich gebraucht werden.

## Abnahmekontrolle 12.7

| Kriterium aus Task 12.7 | Erfuellung |
| --- | --- |
| Abschnitt `Bewertung B` vorhanden | Der Abschnitt ist als `## Bewertung B` angelegt. |
| Vivian-spezifische Punkte getrennt | Eigener Abschnitt `Vivian-spezifische Bewertung` bewertet Agent, Dialog, Guidance, Bestaetigung und Runtime-Ausgabe. |
| Objekt-spezifische Punkte getrennt | Eigener Abschnitt `Objekt-spezifische Bewertung` bewertet CoffeeMachine, Objektzustand, Affordances, Readiness und sicheren Nicht-Start. |
| Direkte Abbildung bewertet | Der Abschnitt `Direkte Abbildung` benennt direkt modellierbare B-Bereiche. |
| Unscharfe Abbildung bewertet | Der Abschnitt `Unscharfe Abbildung` benennt Dialog-, Objekt-, Runtime-, Event- und Trace-Unschaerfen. |
| Luecken bewertet | Der Abschnitt `Luecken` bewertet `B-GAP-01` bis `B-GAP-12` ohne die finale Modellentscheidung aus 12.8 vorwegzunehmen. |
| Gesamturteil formuliert | B ist im Kern modellierbar; Praezisionsgrenzen werden modular behandelt. |

## Modellentscheidung

Die Auswertung der beiden Beispiele fuehrt zu einer bewusst kleinen Kernentscheidung: Der Kern wird nur dort praezisiert, wo A und B denselben allgemeinen, kompakten und traceability-relevanten Bedarf zeigen. Alles, was raeumlich, dialogisch, objektbezogen, regelbasiert, runtime-spezifisch, safety-nah oder testorakel-spezifisch ist, wird nicht in den Kern gezogen, sondern als optionales Ergaenzungsmodell behandelt.

Damit bleibt der Kern auf seine Hauptaufgabe fokussiert: eine stabile fachliche Trace-Kette von Requirements ueber Use Cases, Scenarios, ScenarioSteps, Conditions, Events, StateAssertions, Capabilities, Effects und RuntimeBindings bis zu RuntimeActions und ValidationCases bereitzustellen.

### Entscheidungskriterien

Eine Kernanpassung wird nur vorgenommen, wenn alle folgenden Kriterien erfuellt sind:

| Kriterium | Bedeutung fuer diese Arbeit |
| --- | --- |
| Allgemeingueltigkeit | Der Bedarf tritt nicht nur in A oder nur in B auf, sondern ist fuer Dynamic-Functional-MLDS allgemein nuetzlich. |
| Kompaktheit | Die Anpassung laesst sich als kleines optionales Attribut oder kleine optionale Beziehung modellieren. |
| EAST-ADL-Nahe | Die Anpassung staerkt Requirements-, Use-Case-, Trace- oder Verhaltenssemantik, ohne technische Implementierung einzufuehren. |
| Wiederverwendbarkeit | Die Anpassung ist nicht an Vivian, Kaffeemaschine, VR-Engine, Tool, Adapter oder eine einzelne Domaene gebunden. |
| Rueckwaertskompatibilitaet | Bestehende A- und B-Instanzen bleiben ohne Pflichtmigration gueltig. |
| Invariantenvertraeglichkeit | Actor/Agent-Trennung, Scenario/Runtime-Trennung und die verbotene `ScenarioStep -> RuntimeAction`-Abkuerzung bleiben erhalten. |

Diese Kriterien verhindern, dass jede nuetzliche Spezialsemantik sofort zur Kernklasse wird. Eine hohe fachliche Wichtigkeit reicht nicht aus; ein Konzept muss auch kernreif sein.

### Herleitung aus A und B

Die gemeinsame Struktur aus A und B ist die Trace-Kette:

`Requirement -> UseCase -> Scenario -> ScenarioStep -> CapabilityUse -> Capability -> Effect -> RuntimeBinding -> RuntimeAction -> ValidationCase`

Beide Beispiele bestaetigen diese Kette. A zeigt sie fuer dynamisches Agentenverhalten in einer Szene. B zeigt sie fuer assistierte Interaktionsobjektbedienung mit Vivian. Die Unterschiede liegen nicht in der Grundstruktur, sondern in den Spezialisierungen:

| Befund | A | B | Konsequenz |
| --- | --- | --- | --- |
| Identifizierbare Entities brauchen grobe Lesbarkeit | Agent, Zone, Boundary, Signal, Szenenzustand | Vivian, Kaffeemaschine, Tasse, BrewingRequest | optionales `Entity.kind` ist kernnah. |
| Effects brauchen beobachtbaren Nachweis | Rolle angenommen, Agent bewegt sich, Zielzustand erreicht | Guidance ausgegeben, Start freigegeben, Maschine brueht | optionale Kante `Effect.evidencedBy -> StateAssertion` ist kernnah. |
| Raumsemantik ist wichtig, aber detailreich | `inside`, `near`, `reachable`, `movingTo` | nur indirekt bei Tassenbereich/Bedienzone | optionales `SpatialSemanticsModule`, kein Kern. |
| Zustandsautomaten waeren nuetzlich | Agentenrolle und Aktivitaet | Maschinen- und Request-Lifecycle | optionales `StateTransitionModule`, kein Kern. |
| Bedienobjekte sind stark B-getrieben | nur vorbereitet | Starttaste, Tassenbereich, Programmauswahl | optionales `InteractionObjectModule`, kein Kern. |
| Vivian-Dialog ist stark B-getrieben | Feedback/Instruction nur am Rand | Guidance, Rueckfrage, Fehlererklaerung | optionales `AssistantInteractionModule`, kein Kern. |
| Runtime-Orchestrierung ist technisch | VR-RuntimeActions | Vivian-, VR-, CoffeeMachine- und Trace-RuntimeActions | optionales Runtime-Modul, keine direkte Step-Kante. |

Die Entscheidung ist daher aus den Beispielen abgeleitet: Nur die beiden gemeinsamen, kleinen Trace- und Entity-Praezisierungen werden Kern. Die eigentlichen A- und B-Spezialisierungen bleiben Module.

### Kernanpassungen

Es werden genau zwei minimale Kernanpassungen beschlossen.

| Nr. | Kernanpassung | Kardinalitaet | Begruendung |
| --- | --- | --- | --- |
| `KERN-01` | `Entity.kind: EntityKind [0..1]` | optionales Attribut | A und B nutzen verschiedenartige Entities; eine grobe Typisierung erleichtert Validierung und Generatoren, ohne neue Klassenhierarchie einzufuehren. |
| `KERN-02` | `Effect.evidencedBy -> StateAssertion [0..*]` | optionale nicht-kompositive Referenz | Effects in A und B werden durch konkrete Zustandsaussagen beobachtbar; die Kante staerkt Traceability, ohne Effects zu Testorakeln zu machen. |

Fuer `Entity.kind` ist nur eine kleine, stabile Enumeration vorgesehen:

| Wert | Bedeutung | A/B-Beispiel |
| --- | --- | --- |
| `agent` | aktive systemische Entity | `AgentBody`, `VivianAssistant` |
| `asset` | physisches oder digitales Objekt | `InteractionAsset`, `CoffeeMachine`, `Cup` |
| `zone` | raeumlicher oder semantischer Bereich | `TriggerZone`, `TargetZone`, `CoffeeMachine.cupArea` falls instanziiert |
| `signal` | Signal-, Marker- oder Feedback-Entity | `FeedbackSignal`, `readyFeedback` |
| `stateObject` | fachliches Informations-, Request- oder Statusobjekt | `SceneStateFlag`, `BrewingRequest` |

Diese Werte duerfen nicht zu domaenenspezifischen Typen wie `coffeeMachine`, `startButton`, `ttsVoice` oder `unityController` anwachsen. Solche Spezifika gehoeren in Ergaenzungsmodule oder Instanzdaten.

`Effect.evidencedBy` bleibt eine Referenz, keine Komposition. Ein Effect besitzt die StateAssertion nicht. Eine StateAssertion darf von mehreren Effects oder ValidationCases genutzt werden. Nicht jeder Effect muss sofort Evidence-Links besitzen.

### Ergaenzungsmodule

Die folgenden Bedarfe werden als optionale Ergaenzungsmodule eingeordnet. Ein Kernmodell ohne diese Module bleibt gueltig.

| Modul | Prioritaet | Primaerer Zweck | Andockpunkte |
| --- | --- | --- | --- |
| `InteractionObjectModule` | hoch | Bedienbare Objekte, Bedienpunkte, Affordances, Interaktionszonen | `Entity`, `Actor`, `Event`, `Condition`, `StateAssertion`, `Capability` |
| `AssistantInteractionModule` | hoch | Vivian-Dialog, GuidanceContent, Dialogakte, Antwortoptionen | `Agent`, `Capability`, `ScenarioStep`, `RuntimeBinding` |
| `DecisionRuleModule` | hoch | Readiness-, Diagnose- und Korrekturregeln | `Capability`, `Condition`, `StateAssertion`, `Effect`, `ValidationCase` |
| `StateTransitionModule` | hoch | formale States, StateDimensions und Transitionen | `Entity`, `Agent`, `Event`, `Condition`, `StateAssertion`, `Effect` |
| `SpatialSemanticsModule` | mittel | Raumrelationen, Regionen, Frames und Constraints | `Entity`, `Condition`, `StateAssertion`, `Event` |
| `EventDetailModule` | mittel | Eventquelle, Ziel, Payload, Kanal und Korrelation | `Event`, `Actor`, `Entity`, `ScenarioStep`, `RuntimeAction` |
| `RuntimeExecutionModule` | mittel | Reihenfolge, Abhaengigkeiten und Fehlerbehandlung innerhalb einer RuntimeBinding | `RuntimeBinding`, `RuntimeAction`, `ValidationCase` |
| `ValidationAssertionModule` | mittel | formale Testorakel, Negation, Temporalitaet und zusammengesetzte Outcomes | `ValidationCase`, `StateAssertion`, `Event`, `Effect`, `Condition` |
| `RuntimeProfileModule` | mittel | Plattform-, Adapter-, Schema- und Profilinformationen | `RuntimeBinding`, `RuntimeAction`, `Condition`, `ValidationCase` |

Diese Module duerfen die Kernkette nicht ersetzen. Insbesondere gilt:

- kein Modul fuehrt eine direkte `ScenarioStep -> RuntimeAction`-Kante ein,
- `Affordance` darf keine `RuntimeAction` direkt referenzieren,
- Dialogakte duerfen `Capability` verfeinern, aber nicht ersetzen,
- Runtime-Reihenfolge bleibt unter `RuntimeBinding`,
- technische Endpoints, Topics und Schemas bleiben auf `RuntimeAction`- oder Runtime-Modul-Ebene.

### Zurueckgestellte Bedarfe

Einige B-Gaps werden fuer die aktuelle Baseline nicht weitergefuehrt, obwohl sie bei erweitertem Scope relevant werden koennen.

| Bedarf | Entscheidung fuer die aktuelle Arbeit | Begruendung |
| --- | --- | --- |
| `ScenarioVariationModule` | kein unmittelbarer Modellbedarf | `Scenario.kind` und `StepRelation.kind` reichen fuer Main, Alternative und Exception aus. |
| `SafetyArgumentModule` | kein unmittelbarer Modellbedarf | Sicherer Nicht-Start ist als Condition, StateAssertion und ValidationCase abbildbar; ein SafetyCase waere ein eigener Scope. |
| `RecoveryPolicyModule` | kein unmittelbarer Modellbedarf | Abbruch, Timeout und Recovery koennen zunaechst als weitere Scenarios modelliert werden. |

Diese Entscheidung bedeutet nicht, dass die Themen unwichtig sind. Sie bedeutet nur, dass sie fuer die aktuelle A/B-Baseline keine Kernanpassung und kein sofort auszuarbeitendes Modul erzwingen.

### Invarianten und Kompatibilitaet

Die Modellentscheidung erhaelt die zentralen Invarianten:

| Invariante | Wirkung der Entscheidung |
| --- | --- |
| Genau ein Main Scenario pro UseCase | unveraendert; A und B behalten je genau ein `main` Scenario. |
| Include ist verpflichtend, Extend ist optional/bedingt | unveraendert; Alternativen und Exceptions werden nicht als Include/Extend missbraucht. |
| `Satisfy` referenziert Requirement oder UseCase, nicht beides | unveraendert; die XOR-Regel bleibt bestehen. |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | unveraendert; Runtime-Orchestrierung bleibt unter `RuntimeBinding`. |
| Actor/Agent-Trennung | unveraendert; `Entity.kind` ersetzt keinen Actor und macht Vivian nicht automatisch zur externen Rolle. |
| Capability bleibt fachlich | unveraendert; technische Details bleiben in RuntimeBinding/RuntimeAction oder Runtime-Modulen. |

Die Entscheidung ist rueckwaertskompatibel:

- `Entity.kind` ist optional; Entity-Instanzen ohne Typisierung bleiben gueltig.
- `Effect.evidencedBy` ist optional; Effects ohne Evidence-Link bleiben gueltig.
- StateAssertions werden nicht von Effects besessen oder exklusiv gebunden.
- Alle Ergaenzungsmodule sind zuschaltbar; kein bestehender UseCase muss Modulinstanzen besitzen.
- A- und B-ScenarioSteps, RuntimeBindings, RuntimeActions und ValidationCases bleiben unveraendert gueltig.

### Gesamtentscheidung

Das Metamodell bleibt kompakt und EAST-ADL-nah. Der Kern wird nur um zwei optionale Praezisierungen erweitert: grobe Entity-Typisierung und optionale Effect-Evidence-Traceability. Die eigentlichen Fachspezialisierungen werden ueber optionale Module eingehangen.

Damit ist die Entscheidung nicht willkuerlich, sondern folgt direkt aus den Beispielen: A und B teilen dieselbe Kernkette, aber sie treiben unterschiedliche Detailsemantiken. Der Kern traegt die gemeinsame Struktur; die Module tragen die spezialisierten Praezisierungen.

## Abnahmekontrolle 12.8

| Kriterium aus Task 12.8 | Erfuellung |
| --- | --- |
| Abschnitt `Modellentscheidung` vorhanden | Der Abschnitt ist als `## Modellentscheidung` angelegt. |
| Entscheidung aus Beispielen hergeleitet | Die Herleitung vergleicht A- und B-Befunde und begruendet daraus Kern und Module. |
| Kernanpassungen benannt | `Entity.kind [0..1]` und `Effect.evidencedBy -> StateAssertion [0..*]` sind explizit genannt. |
| Ergaenzungsmodule benannt | Neun optionale Module mit Prioritaet, Zweck und Andockpunkten sind aufgefuehrt. |
| Zurueckgestellte Bedarfe benannt | ScenarioVariation, SafetyArgument und RecoveryPolicy werden fuer die aktuelle Baseline nicht weitergefuehrt. |
| Invarianten geprueft | Main-Scenario, Include/Extend, Satisfy-XOR, Actor/Agent-Trennung und keine Runtime-Kurzschaltung bleiben erhalten. |
| Rueckwaertskompatibilitaet erklaert | Beide Kernanpassungen und alle Module sind optional; bestehende A/B-Instanzen bleiben gueltig. |

## Finaler Beispieltrace

Der finale Beispieltrace nutzt `B-REQ-011 Start nur bei Freigabe`. Diese Anforderung ist geeignet, weil sie die zentrale fachliche Aussage des Vivian-Kaffeemaschinenbeispiels pruefbar macht: Der Bruehstart darf erst erfolgen, wenn die Bereitschaftspruefung bestanden ist, die Startpermission erlaubt ist und die Benutzerbestaetigung vorliegt.

Die vollstaendige Trace-Kette lautet:

`B-REQ-011 -> UC-B-01 -> SC-B-01-MAIN -> B-MAIN-G08 -> B-MAIN-S15 -> B-CU-007 -> CAP-B-START-BREWING -> B-EFF-BREWING-START-ISSUED -> B-RB-COFFEE-START-BREWING -> B-RA-CM-REQUEST-BREWING-START / B-RA-CM-SYNC-BREWING-STATE / B-RA-TRACE-SYNC-START-OUTCOME -> SA-B-BREWING-START-ISSUED / SA-B-CM-BREWING -> B-VC-005-CONFIRMATION-AND-START`

| Trace-Ebene | Instanz | Funktion im Nachweis |
| --- | --- | --- |
| Requirement | `B-REQ-011 Start nur bei Freigabe` | Fordert, dass der fachliche Bruehstart nur nach bestandener Bereitschaftspruefung, erlaubter Startpermission und Benutzerbestaetigung ausgeloest wird. |
| UseCase | `UC-B-01` | Kapselt den assistierten Bedienfall der Kaffeemaschine mit Vivian. |
| Scenario | `SC-B-01-MAIN` | Beschreibt den erfolgreichen Hauptablauf der assistierten Kaffeezubereitung. |
| Guard | `B-MAIN-G08` | Formalisiert die Freigabebedingung: `BrewingRequest.confirmed = true and CoffeeMachine.startPermission = allowed and ReadinessCheck.result = passed and BrewingRequest.state != cancelled`. |
| ScenarioStep | `B-MAIN-S15` | Beschreibt ausschliesslich die fachliche Systemreaktion: Das System startet den Bruehvorgang fachlich. |
| CapabilityUse | `B-CU-007` | Verbindet den fachlichen Schritt mit der genutzten Faehigkeit und ihren Parametern `targetObject=ENT-B-02 CoffeeMachine`, `request=ENT-B-04 BrewingRequest`, `program=coffee`. |
| Capability | `CAP-B-START-BREWING` | Beschreibt die fachliche Faehigkeit der Kaffeemaschine, den Bruehvorgang unter den Freigabebedingungen zu starten. |
| Effect | `B-EFF-BREWING-START-ISSUED` | Erwartete fachliche Wirkung: Der Bruehstart ist ausgeloest und fuehrt in einen beobachtbaren Bruehvorgang. |
| RuntimeBinding | `B-RB-COFFEE-START-BREWING` | Ordnet die fachliche Capability der technischen Laufzeitbindung fuer Kaffeemaschinenadapter, VR-Interaktion und Trace-Synchronisation zu. |
| RuntimeActions | `B-RA-CM-REQUEST-BREWING-START`; `B-RA-CM-SYNC-BREWING-STATE`; `B-RA-TRACE-SYNC-START-OUTCOME` | Enthalten die konkreten technischen Endpoints, Topics, Schemas und Synchronisationsschritte. |
| Evidence | `SA-B-BREWING-START-ISSUED`; `SA-B-CM-BREWING` | Macht die Wirkung beobachtbar: der Request steht auf `startIssued`, die Kaffeemaschine auf `lifecycleState = brewing`. |
| ValidationCase | `B-VC-005-CONFIRMATION-AND-START` | Prueft die Kette fuer `B-REQ-010`, `B-REQ-011`, `B-REQ-012` und `B-REQ-017`; ein Start ohne `B-MAIN-G08` ist nicht erlaubt. |

Der Trace zeigt damit nicht nur, dass der Start technisch ausfuehrbar ist, sondern warum er fachlich erlaubt ist. Der Guard `B-MAIN-G08` liegt vor dem fachlichen Startschritt. Die Capability beschreibt die erlaubte Leistung. Die RuntimeBinding uebersetzt diese Leistung erst danach in konkrete RuntimeActions. Der ValidationCase prueft schliesslich, ob die erwarteten StateAssertions eintreten und ob der Start ohne Freigabe blockiert bleibt.

### Keine direkte Runtime-Abkuerzung

Die Kette enthaelt bewusst keine direkte `ScenarioStep -> RuntimeAction`-Beziehung:

| Pruefpunkt | Ergebnis |
| --- | --- |
| `B-MAIN-S15` referenziert RuntimeActions nicht direkt | Der Schritt ist fachlich und wird ueber `B-CU-007` angebunden. |
| `B-CU-007` referenziert genau eine fachliche Capability | Die Capability ist `CAP-B-START-BREWING`; technische Endpoints stehen hier nicht. |
| `CAP-B-START-BREWING` beschreibt Preconditions und Effect | Die Capability bleibt fachlich und enthaelt keine API- oder Topic-Details. |
| `B-RB-COFFEE-START-BREWING` besitzt die technischen RuntimeActions | Erst diese Binding-Ebene ordnet `B-RA-CM-REQUEST-BREWING-START`, `B-RA-CM-SYNC-BREWING-STATE` und `B-RA-TRACE-SYNC-START-OUTCOME` zu. |
| `B-VC-005-CONFIRMATION-AND-START` prueft die Ausfuehrung | Der ValidationCase darf RuntimeBindings und erwartete Outcomes pruefen, ersetzt aber nicht die fachliche Trace-Kette. |

Damit bleibt die zentrale Modellregel erhalten: Ein ScenarioStep beschreibt, was im Szenario fachlich geschieht. Eine RuntimeAction beschreibt, wie eine konkrete Laufzeitumgebung dies technisch ausfuehrt. Beide Ebenen werden nur ueber `CapabilityUse`, `Capability` und `RuntimeBinding` gekoppelt.

## Abnahmekontrolle 12.9

| Kriterium aus Task 12.9 | Erfuellung |
| --- | --- |
| Trace-Kette vom Requirement bis ValidationCase vorhanden | Die Kette beginnt bei `B-REQ-011` und endet bei `B-VC-005-CONFIRMATION-AND-START`. |
| Guard/Freigabe ist enthalten | `B-MAIN-G08` ist explizit in der Kette und in der Tabelle beschrieben. |
| Fachlicher Schritt ist enthalten | `B-MAIN-S15` beschreibt den fachlichen Bruehstart ohne technische Endpoint-Details. |
| CapabilityUse und Capability sind getrennt | `B-CU-007` bindet den Schritt an `CAP-B-START-BREWING`; die Capability bleibt fachlich. |
| RuntimeBinding und RuntimeActions sind korrekt eingeordnet | `B-RB-COFFEE-START-BREWING` traegt die drei RuntimeActions; keine RuntimeAction haengt direkt am ScenarioStep. |
| Beobachtbare Evidenz ist enthalten | `SA-B-BREWING-START-ISSUED` und `SA-B-CM-BREWING` machen den fachlichen Effect pruefbar. |
| Keine verbotene direkte `ScenarioStep -> RuntimeAction`-Abkuerzung | Die Negativpruefung zeigt explizit, dass `B-MAIN-S15` nur ueber `B-CU-007`, `CAP-B-START-BREWING` und `B-RB-COFFEE-START-BREWING` zur Runtime-Ebene fuehrt. |
