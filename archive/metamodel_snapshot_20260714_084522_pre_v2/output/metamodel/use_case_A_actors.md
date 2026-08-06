# Anwendungsfall A: Externe Rollen / Actor-Kandidaten

Stand: 2026-07-07

Task: 2.3 `Externe Rollen fuer Anwendungsfall A bestimmen`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Grundentscheidung

Ein `Actor` ist hier keine konkrete Person, kein Avatar, kein Agent und kein technisches System, sondern eine externe Rolle gegenueber dem modellierten System. Eine reale Person oder eine konkrete Agent-Entitaet kann spaeter eine oder mehrere dieser Rollen spielen; diese Zuordnung gehoert jedoch zu `Agent`, `Entity` oder spaeteren Instanzen und nicht zur Actor-Definition selbst.

## Actor-Kandidaten

| Actor-Kandidat | Externe Rolle | Warum Actor? | Warum keine physische Instanz? | Voraussichtliche Nutzung im spaeteren Szenario |
| --- | --- | --- | --- | --- |
| `ScenarioDesigner` | Rolle, die dynamisches Agentenverhalten, Zielzustand und relevante Bedingungen fuer eine Szene fachlich spezifiziert. | Diese Rolle interagiert mit dem System, indem sie vorgibt, welches Verhalten modelliert oder generiert werden soll. | Kann eine Person, ein Autorentool oder ein LLM-gestuetzter Workflow sein; die Rolle beschreibt nur die externe Intentionsquelle. | Liefert Anforderungen, UseCase-Text, Szenarioziel und initiale Modellierungsabsicht. |
| `SceneParticipant` | Rolle, die in der Szene Ereignisse ausloest oder durch ihr Verhalten Agentenreaktionen provoziert. | Diese Rolle steht ausserhalb der Agentenlogik und interagiert durch beobachtbare Handlungen mit der Szene. | Kann ein VR-Benutzer, ein Avatar, ein Testskript oder eine simulierte Eingabe sein; das konkrete Ausfuehrungsobjekt wird nicht als Actor modelliert. | Kann spaeter `ScenarioStep.kind = actorIntent` ausloesen, z. B. Betreten einer Zone oder Interaktion mit einem Objekt. |
| `SceneObserver` | Rolle, die Agentenverhalten und erreichten Szenenzustand beobachtet oder bewertet. | Diese Rolle ist extern, weil sie nicht zwingend Verhalten ausloest, sondern das Ergebnis aus Sicht der Umgebung wahrnimmt. | Kann ein Mensch, ein Monitoring-Werkzeug oder ein Validierungskontext sein; Actor beschreibt nur die Beobachterrolle. | Wird relevant fuer beobachtbare Effects, StateAssertions und ValidationCases. |
| `TrainingSupervisor` | Rolle, die im Trainings- oder Demonstrationskontext vorgibt, ob Agentenverhalten korrigiert, erklaert oder wiederholt werden soll. | Diese Rolle beeinflusst Ablaufentscheidungen auf fachlicher Ebene, ohne selbst der Agent zu sein. | Kann ein Trainer, Tutor, Autor oder automatisierter Supervisor sein; die konkrete Instanz bleibt offen. | Kann alternative oder exception-artige Pfade ausloesen, z. B. Wiederholung bei falschem Zielzustand. |
| `ExternalEventSource` | Rolle fuer externe Ereignisquellen, die nicht Teil des Agenten selbst sind, aber Agentenverhalten ausloesen. | EAST-ADL-Actor kann eine externe Rolle sein; hier steht die Rolle fuer nicht-agentische Ausloeser aus der Umgebung. | Kann Sensorik, Simulationszeit, Umgebungssignal oder Testharness sein; die physische Quelle wird spaeter als Entity/Event modelliert, nicht als Actor. | Liefert Events wie Zeitablauf, Raumtrigger, Umgebungsaenderung oder Signal. |

## Nicht als Actor zu modellieren

| Nicht-Actor | Warum nicht Actor? | Spaetere Modellierungsstelle |
| --- | --- | --- |
| Konkreter dynamischer Agent | Ein Agent ist eine ausfuehrende oder beobachtete Entitaet, keine externe UseCase-Rolle an sich. | `Agent` bzw. `Entity` in Task 2.4 |
| Konkretes Szenenobjekt | Ein Objekt interagiert nicht als externe Rolle, sondern besitzt Zustand, Funktion oder Beobachtbarkeit. | `Entity`, `StateAssertion`, ggf. spaeter Interaktionsobjekt-Erweiterung |
| Unity/WebXR/Runtime-Engine | Technische Ausfuehrungsplattform, keine fachliche externe Rolle. | `RuntimeBinding` und `RuntimeAction` in spaeteren Mapping-Tasks |
| Pathfinding-Algorithmus oder KI-Policy | Interne technische oder algorithmische Logik, keine externe Rolle. | Out of Scope oder technische Implementierungsdetails |
| ValidationCase selbst | Ein ValidationCase prueft Verhalten, ist aber keine externe Rolle, die mit dem UseCase interagiert. | `ValidationCase` |

## Abnahmekontrolle

| Kriterium aus Task 2.3 | Erfuellung |
| --- | --- |
| Kandidaten fuer `Actor` bestimmt | `ScenarioDesigner`, `SceneParticipant`, `SceneObserver`, `TrainingSupervisor`, `ExternalEventSource` |
| Jede Rolle als externe Rolle beschrieben | In der Spalte `Externe Rolle` fuer jeden Kandidaten explizit angegeben |
| Keine Rolle als physische Instanz beschrieben | In der Spalte `Warum keine physische Instanz?` fuer jeden Kandidaten explizit abgegrenzt |
| Trennung zu `Agent` und `Entity` gewahrt | Abschnitt `Nicht als Actor zu modellieren` grenzt Agenten, Szenenobjekte und Runtime ab |

## Offene Punkte fuer Task 2.4

Die folgenden Dinge sind absichtlich noch nicht entschieden:

- welche konkrete Agent-Entitaet existiert,
- welche Entity-Typen fuer Szene, Ziel, Objekt oder Umgebung benoetigt werden,
- ob `ExternalEventSource` spaeter als Actor beibehalten oder als Entity/Event-Paar praeziser modelliert wird,
- ob der dynamische Agent eine oder mehrere Actor-Rollen spielt.
