# Anwendungsfall B: Fachliche Einordnung der Kaffeemaschine

Stand: 2026-07-07

Task: 6.4 `Kaffeemaschine fachlich einordnen`

## Entscheidung

Die Kaffeemaschine wird im Basismodell von Anwendungsfall B als `Entity` modelliert.

Fachlich ist sie ein bedienbares virtuelles Asset beziehungsweise Interaktionsobjekt mit pruefbaren Zustaenden, bedienrelevanten Bedingungen und objektgebundenen Capabilities. Sie wird nicht als `Actor` und nicht als `Agent` modelliert. Sie wird auch nicht auf ein technisches Runtime-Ziel reduziert.

Ein spaeteres Interaktionsobjekt-Ergaenzungsmodell ist wahrscheinlich sinnvoll, aber fuer Task 6.4 noch nicht Teil des Kerns. Bis dahin wird die Kaffeemaschine ueber `Entity`, `StateAssertion`, `Condition`, `Capability`, `Effect`, `RuntimeBinding` und `RuntimeAction` abgebildet.

## Einordnung der Optionen

| Option | Entscheidung fuer B | Begruendung |
| --- | --- | --- |
| `Entity` | Ja, Baseline | Die Kaffeemaschine ist ein identifizierbares fachliches Objekt in der Szene, ueber das Zustandsaussagen, Bedingungen und Effekte formuliert werden. |
| Asset | Ja, als semantische Rolle der Entity | Die Kaffeemaschine ist ein virtuelles Szenenobjekt. Falls `Entity.kind` spaeter eingefuehrt wird, waere eine stabile Typisierung wie `asset` oder `interactionObject` naheliegend. |
| Interaktionsobjekt-Erweiterung | Noch nicht im Kern, aber Kandidat | Bedienpunkte, Affordances, erlaubte Manipulationen und objektseitige Constraints sind fuer B wahrscheinlich relevant, gehoeren aber eher in ein optionales Modul als in den kompakten Kern. |
| Runtime-Ziel | Nein als fachliche Einordnung | Die Kaffeemaschine kann in technischen RuntimeActions adressiert werden, aber diese technische Zieladressierung ersetzt nicht das fachliche Objektmodell. |
| `Actor` | Nein | Die Kaffeemaschine ist keine externe Rolle, die eine Absicht gegenueber dem System formuliert. |
| `Agent` | Nein im Basismodell | Die Kaffeemaschine assistiert nicht eigenstaendig wie Vivian. Sie reagiert als bedienbares Objekt und besitzt Zustaende und Capabilities. |

## Trennung von Objektzustand und technischer Ansteuerung

| Aspekt | Fachliche Modellierung | Nicht hier modellieren |
| --- | --- | --- |
| Objektidentitaet | `ENT-B-02 CoffeeMachine` als `Entity` | Unity-GameObject-ID, Prefab-Pfad, MQTT-Topic oder Controllerinstanz |
| Objektzustand | `StateAssertion.subjectRef = CoffeeMachine`, z. B. `state = ready`, `state = brewing`, `state = error` | Interne Controller-Variable, Animation State Machine oder Hardware-Firmware |
| Bedienvoraussetzung | `Condition.expression`, z. B. `waterLevel = sufficient`, `cupPresent = true`, `powerState = on` | Sensor-API, Raycast-Hitbox oder elektrischer Schaltkreis |
| Fachliche Faehigkeit | `Capability`, z. B. `CheckMachineReady`, `StartBrewing`, `StopBrewing`, `ShowBrewingProgress` | Endpoint, Toolname, API-Methode oder Skriptfunktion |
| Beobachtbarer Effekt | `Effect`, z. B. `CoffeeMachine state becomes brewing`, `progress indicator visible` | Shader, Partikeleffekt, Audiofile oder exakte Animation |
| Technische Ansteuerung | Erst unter `RuntimeBinding -> RuntimeAction` | Niemals direkt im `ScenarioStep`, in `Entity` oder in `Capability` |

## Baseline-Modellierung

| Modellaspekt | Baseline fuer die Kaffeemaschine | Konsequenz |
| --- | --- | --- |
| Identifizierbares Subjekt | `Entity`: `CoffeeMachine` | Kann in `StateAssertion.subjectRef`, `Condition.expression` und Validierungsfaellen referenziert werden. |
| Semantische Kategorie | Bedienbares Asset/Interaktionsobjekt | Bis zu einer Kernanpassung nur als dokumentierte Typkonvention; spaeter moeglich als `Entity.kind`. |
| Zustaende | Pruefbare Objektzustaende | Beispiele: `ready`, `notReady`, `brewing`, `finished`, `error`, `awaitingCup`. |
| Bedingungen | Bedienrelevante Preconditions und Guards | Beispiele: `waterLevel = sufficient`, `cupPresent = true`, `machineAvailable = true`. |
| Capabilities | Objektgebundene fachliche Faehigkeiten | Die Entity kann Capabilities bereitstellen, ohne technische Details zu enthalten. |
| Runtime-Bezug | Nur ueber Capabilities und RuntimeBindings | Technische Controller-Aufrufe sind RuntimeActions, nicht Eigenschaften der Entity. |

## Beispielhafte spaetere Instanzen

| Instanzkandidat | Metamodelltyp | Zweck |
| --- | --- | --- |
| `ENT-B-02 CoffeeMachine` | `Entity` | Fachliches Interaktionsobjekt in der virtuellen Szene. |
| `ENT-B-03 Cup` | `Entity` | Relevantes Kontextobjekt fuer Preconditions, z. B. `cupPresent = true`. |
| `COND-B-MACHINE-READY` | `Condition` | Vorbedingung: Kaffeemaschine ist verfuegbar, eingeschaltet, mit Wasser versorgt und Tasse ist platziert. |
| `SA-B-MACHINE-BREWING` | `StateAssertion` | Erwarteter Zustand nach Start: `CoffeeMachine.state = brewing`. |
| `CAP-B-CHECK-MACHINE-READY` | `Capability` | Fachliche Faehigkeit, die Bedienbereitschaft zu pruefen. |
| `CAP-B-START-BREWING` | `Capability` | Fachliche Faehigkeit, den Bruehvorgang zu starten und Fortschritt sichtbar zu machen. |
| `EFF-B-BREWING-STARTED` | `Effect` | Beobachtbarer Effekt: Kaffeemaschine ist im Zustand `brewing`. |
| `RB-B-START-BREWING-VR` | `RuntimeBinding` | Technische Bindung der fachlichen StartBrewing-Capability. |
| `RA-B-COFFEE-START` | `RuntimeAction` | Konkreter Controller-/API-Aufruf, z. B. mit `machineId`, aber erst unter RuntimeBinding. |

## Interaktionsobjekt-Ergaenzung: Bedarf, aber noch keine Kernentscheidung

Fuer das aktuelle Basismodell reicht `Entity` aus, um die Kaffeemaschine als fachliches Objekt mit Zustaenden und Capabilities zu beschreiben. Nicht vollstaendig strukturiert sind damit jedoch:

- Bedienpunkte wie Starttaste, Abbruchknopf oder Auswahlfeld,
- Affordances wie `pressable`, `rotatable`, `selectable`,
- erlaubte Manipulationen und ihre Parameter,
- objektseitige Constraints wie nur eine aktive Auswahl gleichzeitig,
- feingranulare Rueckmeldungen je Bedienpunkt.

Diese Punkte bestaetigen den bereits in `A-GAP-07` markierten Kandidaten fuer ein optionales `Interaction Object/Affordance`-Ergaenzungsmodell. Sie erzwingen fuer 6.4 aber noch keine Kernanpassung.

## Grenzregeln

| Regel | Konsequenz |
| --- | --- |
| Die Kaffeemaschine ist kein `Actor`. | Benutzer- oder Vivian-Absichten werden nicht der Kaffeemaschine als Actor zugeschrieben. |
| Die Kaffeemaschine ist kein primaerer `Agent`. | Eigenstaendige Assistenz-, Dialog- oder Planungslogik liegt bei Vivian oder beim System, nicht bei der Maschine. |
| Die Kaffeemaschine ist nicht nur ein Runtime-Ziel. | Ihr fachlicher Zustand bleibt modellierbar und validierbar, auch wenn es noch keine technische Binding gibt. |
| `ScenarioStep` nennt keine technischen Controller-Aufrufe. | Ein Schritt sagt fachlich "System startet Bruehvorgang"; der Aufruf liegt spaeter in `RuntimeAction`. |
| `Capability` bleibt fachlich. | `StartBrewing` beschreibt Wirkung und Preconditions, nicht `CoffeeMachineController.startBrewing()`. |

## Abnahmekontrolle

| Kriterium aus Task 6.4 | Erfuellung |
| --- | --- |
| Entscheidung Entity/Asset/Interaktionsobjekt/Runtime-Ziel vorhanden | Ja: Baseline `Entity`, semantisch bedienbares Asset/Interaktionsobjekt, Interaktionsobjekt-Ergaenzung als Kandidat, kein Runtime-Ziel als fachliche Einordnung. |
| Objektzustand von technischer Ansteuerung getrennt | Ja: Objektzustaende liegen in `StateAssertion`/`Condition`; technische Steuerung liegt erst in `RuntimeBinding -> RuntimeAction`. |
| Kaffeemaschine nicht als Actor vermischt | Ja: Actor bleibt externe Rolle, z. B. Benutzer. |
| Kaffeemaschine nicht als Agent ueberinterpretiert | Ja: Sie reagiert als bedienbares Objekt; Assistenzlogik liegt bei Vivian oder System-Capabilities. |
| Anschluss an spaetere Modellierbarkeitspruefung vorbereitet | Ja: Affordances und Bedienpunkte sind als Kandidaten fuer ein Ergaenzungsmodell markiert. |

## Konsequenz fuer Task 6.5

Task 6.5 kann nun konkrete Bedienhandlungen sammeln. Jede Handlung muss ausloesendes Ereignis, fachliches Ziel und erwarteten Effekt nennen, ohne technische Controller-Aufrufe direkt in den ScenarioStep zu ziehen.
