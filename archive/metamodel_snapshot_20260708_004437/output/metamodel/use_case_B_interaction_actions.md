# Anwendungsfall B: Bedienhandlungen

Stand: 2026-07-07

Task: 6.5 `Bedienhandlungen sammeln`

## Zweck

Diese Datei sammelt moegliche Benutzer- und Vivian-Handlungen fuer die assistierte Bedienung einer virtuellen Kaffeemaschine. Sie beschreibt noch kein fertiges Szenario und noch keine vollstaendige Schrittfolge. Ziel ist ein belastbarer Handlungskatalog, aus dem spaeter ScenarioSteps, Events, Conditions, StateAssertions, CapabilityUses und Effects abgeleitet werden koennen.

Technische Controller-Aufrufe, APIs, Tools oder Topics werden hier nicht verwendet. Solche Details gehoeren spaeter ausschliesslich unter `RuntimeBinding -> RuntimeAction`.

## Handlungskatalog

| ID | Handelndes Subjekt | Handlung | Ausloeser | Fachliches Ziel | Erwarteter Effekt | Modellhinweis |
| --- | --- | --- | --- | --- | --- | --- |
| B-ACT-001 | `Visitor` als `Actor` | Vivian um Bedienhilfe bitten | Benutzer aeussert Hilfewunsch oder aktiviert Hilfe | Assistierte Bedienung starten | `VivianAssistant.mode = guiding`; erste Bedienanleitung ist sichtbar oder hoerbar | Spaeter `ScenarioStep.kind = actorIntent`; Event `helpRequested` |
| B-ACT-002 | `Visitor` als `Actor` | Tasse an der Kaffeemaschine platzieren oder Platzierung bestaetigen | Benutzer setzt Tasse virtuell ab oder bestaetigt vorhandene Tasse | Vorbedingung fuer sicheren Bruehstart erfuellen | `Cup.state = placed`; `CoffeeMachine.cupPresent = true` | ActorIntent; kann in Preconditions/StateAssertions eingehen |
| B-ACT-003 | `Visitor` als `Actor` | Getraenk oder Programm auswaehlen | Benutzer waehlt Kaffeeprogramm am Bedienfeld | Bruehoption festlegen | `CoffeeMachine.selectedProgram = coffee`; Auswahl ist sichtbar bestaetigt | ActorIntent; benoetigt eventuell spaeter Interaction-Affordance |
| B-ACT-004 | `Visitor` als `Actor` | Starttaste druecken | Benutzer betaetigt Startbedienelement | Bruehvorgang anfordern | `BrewingRequest.state = requested`; Bereitschaftspruefung wird fachlich faellig | ActorIntent; kein Controller-Aufruf im Schritt |
| B-ACT-005 | `Visitor` als `Actor` | Vivian-Bestaetigungsfrage bestaetigen | Vivian fragt nach expliziter Freigabe | Assistierte Ausfuehrung autorisieren | `BrewingRequest.confirmed = true`; Vivian bestaetigt Freigabe | ActorIntent; wichtig fuer assistiertes Starten durch Vivian |
| B-ACT-006 | `Visitor` als `Actor` | Bedienvorgang abbrechen | Benutzer waehlt Abbruch oder widerspricht Vivian | Start oder laufenden Vorgang stoppen beziehungsweise nicht fortsetzen | `BrewingRequest.state = cancelled`; `CoffeeMachine.state` bleibt sicher oder wird sicher beendet | ActorIntent; Kandidat fuer alternative/exception path |
| B-ACT-007 | `Visitor` als `Actor` | Fehlende Voraussetzung korrigieren | Vivian oder System meldet fehlende Tasse, Wasser oder Auswahl | Bedienbereitschaft herstellen | Betroffene Condition wird wahr, z. B. `cupPresent = true` oder `waterLevel = sufficient` | ActorIntent; Korrekturhandlung vor Rueckkehr in Hauptablauf |
| B-ACT-008 | `Visitor` als `Actor` | Fertigmeldung quittieren | Kaffeemaschine oder Vivian meldet Abschluss | Ablauf fachlich abschliessen | `UserAcknowledgement.state = received`; `CoffeeMachine.state = finished` bleibt beobachtbar | ActorIntent oder optionaler Abschlussstep |
| B-ACT-009 | `VivianAssistant` als `Agent` | Bedienabsicht bestaetigen | Benutzer bittet um Hilfe, waehlt Programm oder drueckt Start | Gemeinsames Verstaendnis der beabsichtigten Aktion herstellen | `VivianAssistant.feedbackState = intentConfirmed`; Benutzer erhaelt klare Rueckmeldung | SystemResponse mit `CapabilityUse(CAP-B-VIVIAN-CONFIRM-ACTION)` |
| B-ACT-010 | `VivianAssistant` als `Agent` | Naechsten Bedienhinweis geben | Assistierter Modus ist aktiv und naechster Bedienpunkt ist offen | Benutzer zur korrekten Handlung fuehren | `VivianAssistant.mode = guiding`; relevanter Bedienhinweis ist sichtbar oder hoerbar | SystemResponse mit Guidance-Capability |
| B-ACT-011 | `VivianAssistant` als `Agent` | Bereitschaftspruefung anfordern | Startwunsch oder bestaetigte Bedienabsicht liegt vor | Sicherstellen, dass Startbedingungen erfuellt sind | `ReadinessCheck.state = pending` oder `checked`; Ergebnis wird als Condition nutzbar | SystemResponse mit CapabilityUse; technische Pruefung erst RuntimeBinding |
| B-ACT-012 | `VivianAssistant` als `Agent` | Fehlende Voraussetzung erklaeren | Bereitschaftspruefung schlaegt fehl | Benutzer erhaelt konkrete Korrekturanweisung | `VivianAssistant.feedbackState = errorExplained`; betroffene Condition ist benannt | SystemResponse; Kandidat fuer exception/alternative path |
| B-ACT-013 | `VivianAssistant` als `Agent` | Startfreigabe geben | Alle Preconditions sind erfuellt | Benutzer weiss, dass Bruehstart zulaessig ist | `CoffeeMachine.readyFeedback = visible`; `VivianAssistant.feedbackState = readyConfirmed` | SystemResponse; kann vor Start oder nach Pruefung stehen |
| B-ACT-014 | `VivianAssistant` als `Agent` | Bruehvorgang assistiert starten | Benutzer hat Start gewuenscht und bestaetigt; Maschine ist bereit | Fachlichen Bruehstart ausloesen | `CoffeeMachine.state = brewing`; `BrewingProgress.visible = true` | SystemResponse mit `CapabilityUse(CAP-B-START-BREWING)`; RuntimeAction erst spaeter |
| B-ACT-015 | `VivianAssistant` als `Agent` | Bruehfortschritt melden | Bruehvorgang laeuft | Benutzer ueber laufenden Zustand informieren | `VivianAssistant.feedbackState = progressReported`; Fortschritt ist wahrnehmbar | Optionaler SystemResponse-Schritt |
| B-ACT-016 | `VivianAssistant` als `Agent` | Abschluss melden | Kaffeemaschine erreicht fertigen Zustand | Benutzer erhaelt Abschlussrueckmeldung | `CoffeeMachine.state = finished`; `VivianAssistant.feedbackState = completionReported` | SystemResponse; Abschluss fuer main scenario |

## Minimaler Hauptpfad-Kandidat

Aus dem Katalog ergibt sich als spaeterer Main-Scenario-Kandidat eine kompakte Sequenz:

| Reihenfolge | Handlung | Grund |
| ---: | --- | --- |
| 1 | B-ACT-001 | Benutzer fordert assistierte Bedienung an. |
| 2 | B-ACT-010 | Vivian fuehrt zum relevanten Bedienpunkt. |
| 3 | B-ACT-002 | Tasse wird platziert oder bestaetigt. |
| 4 | B-ACT-003 | Programm wird gewaehlt. |
| 5 | B-ACT-004 | Start wird angefordert. |
| 6 | B-ACT-011 | Vivian/System prueft Bereitschaft. |
| 7 | B-ACT-013 | Startfreigabe wird rueckgemeldet. |
| 8 | B-ACT-005 | Benutzer bestaetigt assistierten Start. |
| 9 | B-ACT-014 | Vivian/System startet fachlich den Bruehvorgang. |
| 10 | B-ACT-016 | Abschluss wird gemeldet. |

Diese Sequenz ist nur ein Kandidat. Die eigentlichen ScenarioSteps werden erst in Task 7.2 definiert.

## Alternative und Fehlerkandidaten

| Handlung | Moeglicher Pfad | Begruendung |
| --- | --- | --- |
| B-ACT-006 | Alternative oder Exception | Benutzer bricht ab; der Ablauf endet kontrolliert oder kehrt in einen sicheren Zustand zurueck. |
| B-ACT-007 | Alternative | Fehlende Voraussetzung wird korrigiert und der Hauptablauf kann fortgesetzt werden. |
| B-ACT-012 | Exception oder Alternative | Vivian erklaert, warum der Bruehstart nicht erlaubt ist. |
| B-ACT-015 | Optionaler Alternativ-/Erweiterungsschritt | Fortschrittsmeldung ist nuetzlich, aber nicht zwingend fuer den Bruehstart selbst. |

## Modellierungsregeln fuer spaetere Schritte

| Regel | Konsequenz |
| --- | --- |
| Benutzerhandlungen sind primaer `actorIntent`. | Sie referenzieren spaeter `performedBy = ACT-B-01 Visitor`. |
| Vivian-Handlungen sind in der Baseline `systemResponse`. | Sie werden ueber `CapabilityUse -> Capability` modelliert, weil Vivian als `Agent`/`Entity` im Scope liegt. |
| Objektreaktionen werden nicht als eigenstaendige Akteure behandelt. | Effekte an der Kaffeemaschine erscheinen als `StateAssertion` oder `Effect`. |
| Technische Ausfuehrung wird nicht im Handlungskatalog genannt. | Controller, APIs, Topics und Schemas erscheinen erst in RuntimeAction-Artefakten. |
| Jede Handlung braucht pruefbaren Effekt. | Effekte muessen spaeter als StateAssertion, Effect oder ValidationCase-Outcome formulierbar sein. |

## Abnahmekontrolle

| Kriterium aus Task 6.5 | Erfuellung |
| --- | --- |
| Liste moeglicher Benutzerhandlungen vorhanden | B-ACT-001 bis B-ACT-008 beschreiben Benutzerhandlungen. |
| Liste moeglicher Vivian-Handlungen vorhanden | B-ACT-009 bis B-ACT-016 beschreiben Vivian-Handlungen. |
| Jede Handlung hat Ausloeser | Spalte `Ausloeser` ist fuer jede Handlung gefuellt. |
| Jede Handlung hat Ziel | Spalte `Fachliches Ziel` ist fuer jede Handlung gefuellt. |
| Jede Handlung hat erwarteten Effekt | Spalte `Erwarteter Effekt` ist fuer jede Handlung gefuellt. |
| Keine technische Direktkopplung | Kein Handlungseintrag enthaelt einen Controller-, API-, Tool- oder Topic-Aufruf als ScenarioStep-Inhalt. |

## Konsequenz fuer Task 6.6

Task 6.6 kann nun die Objektzustaende der Kaffeemaschine aus den erwarteten Effekten ableiten. Besonders relevant sind `ready`, `notReady`, `brewing`, `finished`, `error`, `cupPresent`, `selectedProgram` und `readyFeedback`.
