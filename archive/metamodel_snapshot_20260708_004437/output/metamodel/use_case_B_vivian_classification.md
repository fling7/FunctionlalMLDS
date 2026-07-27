# Anwendungsfall B: Fachliche Einordnung von Vivian

Stand: 2026-07-07

Task: 6.3 `Vivian fachlich einordnen`

## Entscheidung

Vivian wird im Basismodell von Anwendungsfall B als `Agent` modelliert und ist dadurch zugleich eine spezialisierte `Entity`.

Vivian wird im Basismodell nicht als primaerer `Actor` modelliert, weil die aktuelle Systemgrenze Vivian als fachlich beteiligte Assistenz innerhalb der assistierten Objektinteraktion betrachtet. Ein `Actor` beschreibt im EAST-ADL-nahen Use-Case-Kern eine externe Rolle. Diese externe Rolle ist im Basisszenario vor allem die Benutzerrolle, nicht Vivian.

## Begruendung: Rolle versus ausfuehrende Instanz

| Frage | Entscheidung | Begruendung |
| --- | --- | --- |
| Ist Vivian eine externe Rolle? | Nein, nicht im Basismodell. | Vivian liegt gemaess Task 6.2 im Scope der fachlichen Assistenz. Eine externe Benutzerrolle bedient die Kaffeemaschine oder wird angeleitet. |
| Ist Vivian eine ausfuehrende oder beobachtete Instanz in der Szene? | Ja. | Vivian kann anleiten, rueckfragen, bestaetigen, Fehler erklaeren oder assistiert eine Bedienhandlung ausloesen. Das ist Verhalten einer modellierten Instanz. |
| Ist Vivian eine `Entity`? | Ja, ueber `Agent --|> Entity`. | Vivian ist fachlich identifizierbar, kann Zustaende besitzen und Capabilities bereitstellen. |
| Ist Vivian ein `Agent`? | Ja. | Vivian ist mehr als ein passives Objekt: Vivian kann assistieren, kommunizieren, reagieren und ggf. Rollen spielen. |
| Ist Vivian ein `Actor`? | Nur in einer alternativen Systemgrenze. | Wenn das System enger als reine Kaffeemaschinensteuerung definiert wuerde und Vivian als externer Assistenzdienst auftritt, koennte Vivian eine Actor-Rolle spielen. Diese Variante ist nicht die Baseline. |

## Baseline-Modellierung

| Modellaspekt | Baseline fuer Vivian | Konsequenz |
| --- | --- | --- |
| Identifizierbares Subjekt | `Agent`/`Entity`: `VivianAssistant` | Vivian kann in `StateAssertion.subjectRef` referenziert werden. |
| Externe Rolle | Kein eigener primaerer `Actor` fuer Vivian | `ScenarioStep.kind = actorIntent` wird im Regelfall von der Benutzerrolle ausgefuehrt. |
| Systemreaktion | Vivian-Schritte sind meist `ScenarioStep.kind = systemResponse` | Vivian-Verhalten wird ueber `CapabilityUse -> Capability` beschrieben. |
| Faehigkeiten | Vivian kann Capabilities bereitstellen | Beispiele: Anleitung geben, Rueckfrage stellen, Bedienhandlung bestaetigen, Fehlerhinweis geben. |
| Technische Umsetzung | Nicht in Vivian selbst | TTS, LLM, Avatar, Controller oder API liegen spaeter in `RuntimeBinding -> RuntimeAction`. |
| Zustandsaussagen | Vivian-Zustaende sind pruefbare StateAssertions | Beispiele: `VivianAssistant.mode = guiding`, `VivianAssistant.feedbackState = awaitingConfirmation`. |

## Zulassige Variantenregel

Vivian darf nur dann als `Actor` modelliert werden, wenn die Systemgrenze explizit so geaendert wird, dass Vivian ausserhalb des betrachteten Systems liegt und als externe Rolle mit diesem System interagiert.

Beispiel fuer eine solche alternative Grenze:

| Systemgrenze | Vivian-Einordnung |
| --- | --- |
| Betrachtetes System ist die gesamte assistierte VR-Interaktion inklusive Vivian | Vivian ist `Agent`/`Entity`, nicht primaerer `Actor`. |
| Betrachtetes System ist nur die Kaffeemaschinensteuerung, Vivian ist ein externer Assistenzdienst | Vivian kann als `Actor` `VivianAssistantRole` auftreten; eine konkrete Vivian-Instanz kann weiterhin als `Agent` diese Rolle spielen. |

Diese Variantenregel verhindert, dass Actor- und Agent-Ebene vermischt werden.

## Beispielhafte spaetere Instanzen

| Instanzkandidat | Metamodelltyp | Zweck |
| --- | --- | --- |
| `ACT-B-01 Visitor` | `Actor` | Externe Benutzerrolle, die eine Bedienabsicht aeussert oder eine Handlung ausfuehrt. |
| `ENT-B-01 VivianAssistant` | `Agent` und damit `Entity` | Modellierte Assistenzinstanz in der Szene. |
| `CAP-B-VIVIAN-GUIDE-USER` | `Capability` | Fachliche Faehigkeit, den Benutzer durch die Bedienung zu fuehren. |
| `CAP-B-VIVIAN-CONFIRM-ACTION` | `Capability` | Fachliche Faehigkeit, eine Bedienhandlung zu bestaetigen oder Rueckfrage zu stellen. |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | `Capability` | Fachliche Faehigkeit, einen Bedienfehler verstaendlich zu erklaeren. |
| `SA-B-VIVIAN-GUIDING` | `StateAssertion` | Erwarteter Vivian-Zustand, z. B. `VivianAssistant.mode = guiding`. |

## Konsequenz fuer ScenarioSteps

| Schritttyp | Beispiel | Modellierung |
| --- | --- | --- |
| Benutzer drueckt Starttaste | `Visitor presses start button` | `ScenarioStep.kind = actorIntent`, `performedBy = ACT-B-01 Visitor`. |
| Vivian bestaetigt die erkannte Absicht | `Vivian confirms brewing request` | `ScenarioStep.kind = systemResponse`, mit `CapabilityUse(CAP-B-VIVIAN-CONFIRM-ACTION)`. |
| Vivian erklaert einen Fehler | `Vivian explains missing cup` | `ScenarioStep.kind = systemResponse`, mit `CapabilityUse(CAP-B-VIVIAN-EXPLAIN-ERROR)`. |
| Vivian loest assistiert eine Aktion aus | `Vivian starts brewing after confirmation` | `ScenarioStep.kind = systemResponse`, mit CapabilityUse; technische Aktion erst unter `RuntimeBinding -> RuntimeAction`. |

## Abnahmekontrolle

| Kriterium aus Task 6.3 | Erfuellung |
| --- | --- |
| Entscheidung Actor/Agent/Entity/Kombination vorhanden | Ja: Baseline ist `Agent` plus `Entity`; kein primaerer `Actor`. |
| Rolle versus Instanz begruendet | Ja: `Actor` ist externe Rolle, Vivian ist innerhalb der aktuellen Systemgrenze eine modellierte Assistenzinstanz. |
| Alternative Actor-Variante eingeordnet | Ja: Actor nur bei engerer Systemgrenze, in der Vivian extern zum betrachteten System ist. |
| Konsequenz fuer ScenarioSteps beschrieben | Ja: Benutzerhandlungen als `actorIntent`, Vivian-Verhalten als `systemResponse` mit CapabilityUse. |
| Keine technische Umsetzung vermischt | Ja: LLM, TTS, Avatar, API und Controller bleiben Runtime-/Implementierungsdetails. |

## Konsequenz fuer Task 6.4

Task 6.4 muss nun die Kaffeemaschine fachlich einordnen. Dabei ist analog zu Vivian zu trennen zwischen der Kaffeemaschine als fachlichem Objekt mit Zustaenden, als moeglichem Interaktionsobjekt und als technischem Runtime-Ziel.
