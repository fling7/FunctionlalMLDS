# Ausfuehrbare Taskliste: Beispielszenarien und Metamodell-Abbildung

Stand: 2026-07-07

Ziel: Die beiden bekannten Anwendungsfaelle so ausarbeiten, dass fuer jeden Schritt klar ist, was zu tun ist, welches Ergebnis entsteht und wann der Schritt als erledigt gilt.

Nicht-Ziel dieses Dokuments: Die Beispielszenarien bereits inhaltlich ausformulieren oder das Metamodell bereits aendern.

## 0. Sicherung des aktuellen Stands

- [x] 0.1 Aktuelle Metamodell-Artefakte identifizieren.
  - Ergebnis: Liste der relevanten Dateien.
  - Abnahme: `SVG`, `PNG`, `Mermaid`, `Spezifikation` und `Generator` sind enthalten.

- [x] 0.2 Aktuellen Stand in einen timestamped Archivordner kopieren.
  - Ergebnis: Archivordner unter `archive/metamodel_snapshot_20260707_151224`.
  - Abnahme: Alle relevanten Dateien liegen im Archiv.

- [x] 0.3 ZIP-Archiv des Stands erstellen.
  - Ergebnis: `archive/metamodel_snapshot_20260707_151224.zip`.
  - Abnahme: ZIP-Datei existiert und enthaelt den Archivordner.

- [x] 0.4 Pruefsummenmanifest erzeugen.
  - Ergebnis: `manifest.sha256.csv`.
  - Abnahme: Fuer jede gesicherte Datei existiert ein SHA256-Hash.

## 1. Arbeitsbasis kontrollieren

- [x] 1.1 Aktuelle Spezifikation vollstaendig lesen.
  - Ergebnis: Notizen zu allen Metamodell-Elementen.
  - Abnahme: Jedes Element aus der Spezifikation ist in einer Arbeitsnotiz kurz beschrieben.

- [x] 1.2 Aktuelles Diagramm gegen die Spezifikation abgleichen.
  - Ergebnis: Liste `Diagrammbeziehung -> Spezifikationsstelle`.
  - Abnahme: Jede sichtbare Beziehung im Diagramm ist in der Spezifikation auffindbar.

- [x] 1.3 Alle Kardinalitaeten aus Diagramm und Spezifikation extrahieren.
  - Ergebnis: Kardinalitaetstabelle.
  - Abnahme: Keine Kante aus dem Diagramm fehlt in der Tabelle.

- [x] 1.4 Bestehende Invarianten extrahieren.
  - Ergebnis: Liste der Modellregeln, z. B. keine direkte `ScenarioStep -> RuntimeAction`-Kante.
  - Abnahme: Jede Regel hat eine kurze Begruendung.

- [x] 1.5 Begriffsliste fuer die Ausarbeitung anlegen.
  - Ergebnis: Glossar mit `Actor`, `Agent`, `Entity`, `ScenarioStep`, `CapabilityUse`, `Capability`, `RuntimeBinding`, `RuntimeAction`, `ValidationCase`.
  - Abnahme: Jeder Begriff ist mit einem Satz und einem Beispielplatzhalter beschrieben.

## 2. Anwendungsfall A abgrenzen: dynamisches Modellieren von Agenten in einer Szene

- [x] 2.1 Zweck des Anwendungsfalls A in einem Satz formulieren.
  - Ergebnis: Ein Satz, der beschreibt, was das dynamische Agentenmodellieren leisten soll.
  - Abnahme: Der Satz enthaelt Szene, Agent, dynamische Aenderung und Zielzustand.

- [x] 2.2 Systemgrenze fuer Anwendungsfall A festlegen.
  - Ergebnis: Liste `im Scope` und `out of Scope`.
  - Abnahme: Agentenverhalten, Szenenzustand und Runtime-Ausfuehrung sind eindeutig einsortiert.

- [x] 2.3 Externe Rollen fuer Anwendungsfall A bestimmen.
  - Ergebnis: Kandidaten fuer `Actor`.
  - Abnahme: Jede Rolle ist als externe Rolle und nicht als physische Instanz beschrieben.

- [x] 2.4 Ausfuehrende oder beobachtete Entitaeten bestimmen.
  - Ergebnis: Kandidaten fuer `Entity` und `Agent`.
  - Abnahme: Jede Entitaet ist typisiert als user, system, environment oder asset.

- [x] 2.5 Relevante Szenenobjekte als fachliche Gegenstaende erfassen.
  - Ergebnis: Objektliste mit Name, Zustand und Relevanz.
  - Abnahme: Jedes Objekt hat mindestens einen beobachtbaren Zustand oder eine Interaktion.

- [x] 2.6 Dynamische Aenderungen der Szene erfassen.
  - Ergebnis: Liste von Ereignissen, Zustandswechseln und Bedingungen.
  - Abnahme: Jede Aenderung laesst sich vorlaeufig Event, Condition oder StateAssertion zuordnen.

- [x] 2.7 Hauptziel des Anwendungsfalls A festlegen.
  - Ergebnis: Kandidat fuer `UseCase.goal` beziehungsweise `Scenario.goal`.
  - Abnahme: Erfolg ist als beobachtbarer Zielzustand formulierbar.

- [x] 2.8 Startzustand und Vorbedingungen sammeln.
  - Ergebnis: Liste von Preconditions.
  - Abnahme: Jede Vorbedingung ist als pruefbare Aussage formuliert.

- [x] 2.9 Endzustand und Nachbedingungen sammeln.
  - Ergebnis: Liste von Postconditions.
  - Abnahme: Jede Nachbedingung ist als `StateAssertion` formulierbar.

- [x] 2.10 Relevante Fehler- und Alternativfaelle fuer A sammeln.
  - Ergebnis: Liste von Alternativen und Exceptions.
  - Abnahme: Jeder Fall hat Ausloeser, Bedingung und erwartete Reaktion.

## 3. Beispielszenarien fuer Anwendungsfall A ausarbeiten

- [x] 3.1 Einen Main-Use-Case fuer A benennen.
  - Ergebnis: stabiler Use-Case-Identifier und sprechender Name.
  - Abnahme: Name beschreibt fachlich die Nutzung, nicht die technische Umsetzung.

- [x] 3.2 Hauptszenario A in nummerierte Schritte zerlegen.
  - Ergebnis: Sequenz von `ScenarioStep`-Kandidaten.
  - Abnahme: Jeder Schritt hat genau eine fachliche Aussage.

- [x] 3.3 Fuer jeden Schritt A die Schrittart bestimmen.
  - Ergebnis: `actorIntent`, `systemResponse` oder `environmentObservation`.
  - Abnahme: Jede Zuordnung ist begruendet.

- [x] 3.4 Fuer jeden Schritt A die ausloesenden Events bestimmen.
  - Ergebnis: Eventliste pro Schritt.
  - Abnahme: Jeder Event hat Art und Ausdruck.

- [x] 3.5 Fuer jeden Schritt A die Guard Conditions bestimmen.
  - Ergebnis: Conditionliste pro Schritt.
  - Abnahme: Guards sind optional und nur dort gesetzt, wo sie Ablaufentscheidungen beeinflussen.

- [x] 3.6 Fuer jeden Schritt A erwartete Zustandsaussagen bestimmen.
  - Ergebnis: StateAssertions pro Schritt.
  - Abnahme: Jede StateAssertion hat Subjekt und erwarteten Zustand.

- [x] 3.7 StepRelations fuer das Hauptszenario A definieren.
  - Ergebnis: source step, target step, relation kind.
  - Abnahme: Jeder Schritt ausser dem letzten hat mindestens eine ausgehende Sequenzrelation oder begruendete Ausnahme.

- [x] 3.8 Alternatives Szenario A formulieren.
  - Ergebnis: `Scenario.kind = alternative`.
  - Abnahme: Alternative hat klaren Einstiegspunkt, Bedingung und Rueckfuehrung oder eigenen Abschluss.

- [x] 3.9 Exception-Szenario A formulieren.
  - Ergebnis: `Scenario.kind = exception`.
  - Abnahme: Exception hat Fehlerausloeser, Systemreaktion und sicheren Endzustand.

- [x] 3.10 Parallele oder nebenlaeufige Agentenablaeufe pruefen.
  - Ergebnis: Entscheidung, ob `ParallelGroup` benoetigt wird.
  - Abnahme: Falls ja, sind mindestens zwei Mitgliedsschritte angegeben.

## 4. Anwendungsfall A auf das bestehende Metamodell abbilden

- [x] 4.1 Requirements fuer A anlegen.
  - Ergebnis: Liste von Requirement-Instanzen.
  - Abnahme: Jedes Requirement hat Text und eindeutige ID.

- [x] 4.2 UseCase-Instanz fuer A anlegen.
  - Ergebnis: UseCase mit Text und Ziel.
  - Abnahme: UseCase beschreibt Nutzung des Systems und nicht nur eine technische Aktion.

- [x] 4.3 Actor-Instanzen fuer A anlegen.
  - Ergebnis: Actorliste.
  - Abnahme: Jeder Actor interagiert mit dem UseCase oder ist begruendet ausgeschlossen.

- [x] 4.4 Satisfy-Beziehungen fuer A pruefen.
  - Ergebnis: Zuordnung Requirement/UseCase zu erfuellenden Elementen.
  - Abnahme: XOR-Regel wird eingehalten: eine Satisfy-Instanz referenziert Requirement oder UseCase, nicht beides.

- [x] 4.5 Scenario-Instanzen fuer A anlegen.
  - Ergebnis: main, alternative und exception Scenarios.
  - Abnahme: Genau ein main Scenario pro UseCase.

- [x] 4.6 ScenarioStep-Instanzen fuer A anlegen.
  - Ergebnis: Schrittliste mit Nummern, Text, Art und optional performedBy.
  - Abnahme: Schrittfolge ist eindeutig sortiert.

- [x] 4.7 Event-Instanzen fuer A anlegen.
  - Ergebnis: Eventliste.
  - Abnahme: Jeder Event ist mindestens einem Schritt zugeordnet oder als ungenutzt markiert.

- [x] 4.8 Condition-Instanzen fuer A anlegen.
  - Ergebnis: Preconditions, Guards, Postconditions.
  - Abnahme: Jede Condition hat Ausdruck und Typ.

- [x] 4.9 StateAssertion-Instanzen fuer A anlegen.
  - Ergebnis: erwartete Zustandsaussagen.
  - Abnahme: Jede Aussage referenziert ein identifizierbares Subjekt.

- [x] 4.10 CapabilityUse-Instanzen fuer A anlegen.
  - Ergebnis: benoetigte fachliche Faehigkeiten je Schritt.
  - Abnahme: Kein ScenarioStep zeigt direkt auf RuntimeAction.

- [x] 4.11 Capability-Instanzen fuer A anlegen.
  - Ergebnis: fachliche Faehigkeiten mit Intent, Preconditions und promised Effects.
  - Abnahme: Keine Capability enthaelt technische Endpoint-, Tool- oder Topic-Daten.

- [x] 4.12 Effect-Instanzen fuer A anlegen.
  - Ergebnis: versprochene beobachtbare Effekte.
  - Abnahme: Jede Capability hat mindestens einen Effect.

- [x] 4.13 RuntimeBinding-Instanzen fuer A anlegen.
  - Ergebnis: technische Bindungen je Capability.
  - Abnahme: Jede RuntimeBinding referenziert genau eine Capability.

- [x] 4.14 RuntimeAction-Instanzen fuer A anlegen.
  - Ergebnis: technische Aktionen.
  - Abnahme: Jede RuntimeBinding besitzt mindestens eine RuntimeAction.

- [x] 4.15 ValidationCase-Instanzen fuer A anlegen.
  - Ergebnis: abstrakte und/oder konkrete Testfaelle.
  - Abnahme: Jeder ValidationCase hat Stimulus und erwartetes Outcome.

- [x] 4.16 Kardinalitaeten fuer A pruefen.
  - Ergebnis: Checkliste pro Beziehung.
  - Abnahme: Keine Kardinalitaetsverletzung bleibt offen.

- [x] 4.17 Invarianten fuer A pruefen.
  - Ergebnis: Liste bestanden/nicht bestanden.
  - Abnahme: Insbesondere keine direkte Schritt-zu-RuntimeAction-Abbildung.

## 5. Modellierbarkeitspruefung fuer Anwendungsfall A

- [x] 5.1 Alle Elemente markieren, die direkt modellierbar sind.
  - Ergebnis: Tabelle `Element -> Metamodellklasse`.
  - Abnahme: Jede direkte Abbildung nennt die konkrete Klasse und Beziehung.

- [x] 5.2 Alle Elemente markieren, die nur indirekt oder unsauber modellierbar sind.
  - Ergebnis: Tabelle `Element -> Problem`.
  - Abnahme: Problem ist konkret benannt, z. B. fehlende Raumstruktur, fehlende Lebenszyklussemantik, fehlende Interaktionsobjektstruktur.

- [x] 5.3 Alle nicht modellierbaren Elemente markieren.
  - Ergebnis: Liste harter Luecken.
  - Abnahme: Fuer jede Luecke ist erklaert, warum keine vorhandene Klasse passt.

- [x] 5.4 Fuer jede Luecke Entscheidung vorbereiten: Kernanpassung oder Ergaenzungsmodell.
  - Ergebnis: Entscheidungsmatrix.
  - Abnahme: Jede Entscheidung nennt Kriterium, Risiko und Auswirkung auf bestehendes Modell.

## 6. Anwendungsfall B abgrenzen: Interaktionsobjekte mit Vivian, Beispiel Kaffeemaschine

- [x] 6.1 Zweck des Anwendungsfalls B in einem Satz formulieren.
  - Ergebnis: Ein Satz zu Vivian, Interaktionsobjekt und Bedienziel.
  - Abnahme: Satz enthaelt Benutzerrolle, Objektinteraktion und erwarteten Systemeffekt.

- [x] 6.2 Systemgrenze fuer B festlegen.
  - Ergebnis: Liste `im Scope` und `out of Scope`.
  - Abnahme: Vivian, Kaffeemaschine, Benutzerinteraktion und Runtime-Ausfuehrung sind eindeutig einsortiert.

- [x] 6.3 Vivian fachlich einordnen.
  - Ergebnis: Entscheidung, ob Vivian als Actor, Agent, Entity oder Kombination modelliert wird.
  - Abnahme: Entscheidung ist mit Rolle versus ausfuehrender Instanz begruendet.

- [x] 6.4 Kaffeemaschine fachlich einordnen.
  - Ergebnis: Entscheidung, ob Kaffeemaschine als Entity, asset, Interaktionsobjekt-Erweiterung oder Runtime-Ziel modelliert wird.
  - Abnahme: Entscheidung trennt Objektzustand von technischer Ansteuerung.

- [x] 6.5 Bedienhandlungen sammeln.
  - Ergebnis: Liste moeglicher Benutzer- oder Vivian-Handlungen.
  - Abnahme: Jede Handlung hat Ausloeser, Ziel und erwarteten Effekt.

- [x] 6.6 Objektzustaende der Kaffeemaschine sammeln.
  - Ergebnis: Zustandsliste.
  - Abnahme: Jeder Zustand kann als StateAssertion formuliert werden.

- [x] 6.7 Vorbedingungen fuer Bedienung sammeln.
  - Ergebnis: Conditions, z. B. Verfuegbarkeit, Wasserstand, Tasse vorhanden.
  - Abnahme: Jede Bedingung ist pruefbar.

- [x] 6.8 Fehler- und Ausnahmefaelle sammeln.
  - Ergebnis: Liste von Exceptions.
  - Abnahme: Jeder Fehlerfall hat erkennbare Ursache und erwartete Reaktion.

## 7. Beispielszenarien fuer Anwendungsfall B ausarbeiten

- [x] 7.1 Main-Use-Case fuer B benennen.
  - Ergebnis: stabiler Use-Case-Identifier und sprechender Name.
  - Abnahme: Name beschreibt die fachliche Nutzung der Kaffeemaschine mit Vivian.

- [x] 7.2 Hauptszenario B in nummerierte Schritte zerlegen.
  - Ergebnis: Sequenz von ScenarioStep-Kandidaten.
  - Abnahme: Jeder Schritt beschreibt genau eine Benutzer-, Vivian-, System- oder Objektreaktion.

- [x] 7.3 Fuer jeden Schritt B die Schrittart bestimmen.
  - Ergebnis: actorIntent, systemResponse oder environmentObservation.
  - Abnahme: Vivian-Schritte sind konsistent als Rolle oder Agent behandelt.

- [x] 7.4 Events fuer B bestimmen.
  - Ergebnis: Eventliste.
  - Abnahme: Eingaben, Objektzustandswechsel und Systemsignale sind getrennt.

- [x] 7.5 Conditions fuer B bestimmen.
  - Ergebnis: Guard-, Pre- und Postconditions.
  - Abnahme: Jede Ablaufentscheidung hat genau die noetigen Conditions.

- [x] 7.6 StateAssertions fuer B bestimmen.
  - Ergebnis: Objekt- und Systemzustandsaussagen.
  - Abnahme: Kaffeemaschinenzustand, Vivian-Rueckmeldung und Benutzerfeedback sind trennbar.

- [x] 7.7 StepRelations fuer B definieren.
  - Ergebnis: source step, target step, relation kind.
  - Abnahme: Hauptablauf, Alternative und Exception sind als Graph nachvollziehbar.

- [x] 7.8 Include/Extend fuer B pruefen.
  - Ergebnis: Entscheidung, ob wiederverwendbare Pflichtablaeufe als Include oder optionale Zusatzablaeufe als Extend modelliert werden.
  - Abnahme: EAST-ADL-Semantik wird eingehalten: Include verpflichtend, Extend optional/bedingt.

- [x] 7.9 Alternatives Szenario B formulieren.
  - Ergebnis: Scenario.kind = alternative.
  - Abnahme: Alternative ist nicht bloss Fehlerfall, sondern valider anderer Pfad.

- [x] 7.10 Exception-Szenario B formulieren.
  - Ergebnis: Scenario.kind = exception.
  - Abnahme: Exception endet in sicherem oder erklaerbarem Zustand.

## 8. Anwendungsfall B auf das bestehende Metamodell abbilden

- [x] 8.1 Requirements fuer B anlegen.
  - Ergebnis: Requirementliste.
  - Abnahme: Anforderungen sind pruefbar formuliert.

- [x] 8.2 UseCase-Instanz fuer B anlegen.
  - Ergebnis: UseCase mit Ziel und Text.
  - Abnahme: UseCase beschreibt Bedienung und nicht bloss API-Aufruf.

- [x] 8.3 Actor- und Agent-Zuordnung fuer Vivian und Benutzer anlegen.
  - Ergebnis: Actor-/Agent-Mapping.
  - Abnahme: Rollen und ausfuehrende Instanzen sind getrennt.

- [x] 8.4 Kaffeemaschine als fachliche Entitaet modellieren.
  - Ergebnis: Entity-Kandidat mit Art asset/system.
  - Abnahme: Objektzustand ist nicht mit RuntimeAction verwechselt.

- [x] 8.5 Scenarios fuer B anlegen.
  - Ergebnis: main, alternative und exception.
  - Abnahme: Genau ein main Scenario.

- [x] 8.6 ScenarioSteps fuer B anlegen.
  - Ergebnis: nummerierte Schrittliste.
  - Abnahme: Jeder Schritt ist einer Rolle, einem Event oder einer Faehigkeit zuordenbar.

- [x] 8.7 Events, Conditions und StateAssertions fuer B anlegen.
  - Ergebnis: Ablaufbedingungen und erwartete Zustaende.
  - Abnahme: Jede Entscheidung und jeder Zielzustand ist modelliert.

- [x] 8.8 CapabilityUse je systemischem Schritt B anlegen.
  - Ergebnis: benoetigte Faehigkeiten.
  - Abnahme: Keine direkte RuntimeAction vom Schritt aus.

- [x] 8.9 Capabilities fuer Kaffeemaschinenbedienung anlegen.
  - Ergebnis: fachliche Faehigkeiten.
  - Abnahme: Jede Capability hat Intent, Preconditions und Effect.

- [x] 8.10 RuntimeBindings fuer Vivian-/VR-/Toolchain-Ausfuehrung anlegen.
  - Ergebnis: technische Bindungen.
  - Abnahme: Jede Bindung referenziert genau eine fachliche Capability.

- [x] 8.11 RuntimeActions fuer technische Ausfuehrung anlegen.
  - Ergebnis: Endpoint-, Tool- oder Topic-Aktionen.
  - Abnahme: Jede technische Aktion liegt unter RuntimeBinding.

- [x] 8.12 ValidationCases fuer B anlegen.
  - Ergebnis: Tests fuer Haupt-, Alternativ- und Fehlerablaeufe.
  - Abnahme: Jeder Test hat Stimulus und erwartetes Outcome.

- [x] 8.13 Kardinalitaeten und Invarianten fuer B pruefen.
  - Ergebnis: bestanden/nicht bestanden.
  - Abnahme: Keine offene Verletzung ohne begruendete Modellentscheidung.

## 9. Modellierbarkeitspruefung fuer Anwendungsfall B

- [x] 9.1 Direkt modellierbare B-Elemente markieren.
  - Ergebnis: Mappingtabelle.
  - Abnahme: Jede Zeile nennt Metamodellklasse und Beziehung.

- [x] 9.2 Unscharf modellierbare B-Elemente markieren.
  - Ergebnis: Problemtabelle.
  - Abnahme: Vivian-spezifische und Interaktionsobjekt-spezifische Unklarheiten sind getrennt.

- [x] 9.3 Nicht modellierbare B-Elemente markieren.
  - Ergebnis: Lueckenliste.
  - Abnahme: Jede Luecke nennt, warum bestehende Klassen nicht ausreichen.

- [x] 9.4 Entscheidung Kernanpassung oder Ergaenzungsmodell fuer B vorbereiten.
  - Ergebnis: Entscheidungsmatrix.
  - Abnahme: Jede Entscheidung hat fachliche Begruendung und Auswirkung.

## 10. Gemeinsame Analyse beider Anwendungsfaelle

- [x] 10.1 Gemeinsamkeiten von A und B extrahieren.
  - Ergebnis: Liste gemeinsamer Konzepte.
  - Abnahme: Nur Konzepte aufnehmen, die in beiden Beispielen relevant sind.

- [x] 10.2 Unterschiede von A und B extrahieren.
  - Ergebnis: Liste unterschiedlicher Modellierungsbedarfe.
  - Abnahme: Agentendynamik und Interaktionsobjektlogik sind getrennt bewertet.

- [x] 10.3 Pruefen, ob `Entity`/`Agent` fuer Szenenobjekte ausreicht.
  - Ergebnis: Entscheidung.
  - Abnahme: Begruendung nennt Objektzustand, Interaktion und Runtime-Anbindung.

- [x] 10.4 Pruefen, ob `StateAssertion` fuer Objektzustaende ausreicht.
  - Ergebnis: Entscheidung.
  - Abnahme: Begruendung nennt statische Zustaende, Zustandsautomaten und Uebergaenge.

- [x] 10.5 Pruefen, ob `Capability`/`RuntimeBinding` fuer Vivian-Aktionen ausreicht.
  - Ergebnis: Entscheidung.
  - Abnahme: Begruendung trennt fachliche Faehigkeit, Dialogverhalten und technische Aktion.

- [x] 10.6 Pruefen, ob raeumliche Beziehungen explizit benoetigt werden.
  - Ergebnis: Entscheidung.
  - Abnahme: Falls noetig, sind Beispiele fuer Position, Naehe, Sichtbarkeit oder Erreichbarkeit genannt.

- [x] 10.7 Pruefen, ob Interaktionsobjekte eigene Affordances brauchen.
  - Ergebnis: Entscheidung.
  - Abnahme: Falls noetig, ist klar, warum `Capability` allein nicht ausreicht.

- [x] 10.8 Pruefen, ob Agenten eigene Ziele, Rollenwechsel oder Laufzeitprofile brauchen.
  - Ergebnis: Entscheidung.
  - Abnahme: Falls noetig, ist klar, warum `Agent` plus `Capability` nicht ausreicht.

## 11. Entscheidung: Kernmetamodell anpassen oder Ergaenzungsmodell einhaengen

- [x] 11.1 Kriterien fuer Kernanpassung festlegen.
  - Ergebnis: Kriterienliste.
  - Abnahme: Kriterien enthalten Allgemeingueltigkeit, Kompaktheit, EAST-ADL-Nahe und Wiederverwendbarkeit.

- [x] 11.2 Kriterien fuer Ergaenzungsmodell festlegen.
  - Ergebnis: Kriterienliste.
  - Abnahme: Kriterien enthalten Domaenenspezifik, optionale Nutzung und geringe Belastung des Kerns.

- [x] 11.3 Jede identifizierte Luecke anhand der Kriterien bewerten.
  - Ergebnis: Bewertungstabelle.
  - Abnahme: Jede Luecke hat Entscheidung `Kern`, `Ergaenzung` oder `kein Modellbedarf`.

- [x] 11.4 Minimale Kernanpassungen spezifizieren, falls erforderlich.
  - Ergebnis: Liste geplanter Kernaenderungen.
  - Abnahme: Jede Anpassung nennt neue/veraenderte Klasse, Beziehung, Kardinalitaet und Invariante.

- [x] 11.5 Ergaenzungsmodell spezifizieren, falls erforderlich.
  - Ergebnis: Entwurf mit Klassen, Beziehungen und Anschlussstellen.
  - Abnahme: Jede Anschlussstelle referenziert eine bestehende Klasse des Kernmetamodells.

- [x] 11.6 Rueckwaertskompatibilitaet pruefen.
  - Ergebnis: Liste betroffener bestehender Elemente.
  - Abnahme: Kein bestehender UseCase oder ScenarioStep wird ungueltig, ausser es wird explizit begruendet.

## 12. Schriftliche Ausarbeitung erstellen

- [x] 12.1 Problemstellung auf Deutsch formulieren.
  - Ergebnis: Abschnitt `Problem`.
  - Abnahme: Leser versteht, warum dynamische Szenen und Interaktionsobjekte modelliert werden muessen.

- [x] 12.2 Anwendungsfall A beschreiben.
  - Ergebnis: Abschnitt mit Ziel, Rollen, Hauptablauf, Alternative, Exception.
  - Abnahme: Beschreibung ist ohne Diagramm verstaendlich.

- [x] 12.3 Abbildung von A im Metamodell beschreiben.
  - Ergebnis: Abschnitt `Mapping A`.
  - Abnahme: Jede zentrale Metamodellklasse wird mindestens einmal konkret verwendet oder begruendet ausgelassen.

- [x] 12.4 Modellierbarkeitsbewertung A beschreiben.
  - Ergebnis: Abschnitt `Bewertung A`.
  - Abnahme: Direkte Abbildung, unscharfe Abbildung und Luecken sind getrennt.

- [x] 12.5 Anwendungsfall B beschreiben.
  - Ergebnis: Abschnitt mit Vivian, Kaffeemaschine, Hauptablauf, Alternative, Exception.
  - Abnahme: Beschreibung ist ohne Vorwissen zum Diagramm verstaendlich.

- [x] 12.6 Abbildung von B im Metamodell beschreiben.
  - Ergebnis: Abschnitt `Mapping B`.
  - Abnahme: Rollen, Objektzustand, Capability und RuntimeBinding sind klar getrennt.

- [x] 12.7 Modellierbarkeitsbewertung B beschreiben.
  - Ergebnis: Abschnitt `Bewertung B`.
  - Abnahme: Vivian-spezifische und Objekt-spezifische Punkte sind getrennt.

- [x] 12.8 Entscheidung zu Kernanpassung/Ergaenzungsmodell begruenden.
  - Ergebnis: Abschnitt `Modellentscheidung`.
  - Abnahme: Entscheidung ist aus den Beispielen hergeleitet und nicht willkuerlich.

- [x] 12.9 Finalen Beispielpfad als Trace formulieren.
  - Ergebnis: Trace-Kette vom Requirement bis ValidationCase.
  - Abnahme: Kette zeigt keine verbotene direkte `ScenarioStep -> RuntimeAction`-Abkuerzung.

## 13. Falls nach Freigabe Diagramm und Spezifikation angepasst werden

- [x] 13.1 Aenderungsumfang bestaetigen.
  - Ergebnis: Liste der freigegebenen Modellaenderungen.
  - Artefakt: `output/metamodel/change_scope_13_1.md`.
  - Abnahme: Es ist klar, ob nur Text oder auch Diagramm/Generator angepasst wird.

- [x] 13.2 Generator aktualisieren.
  - Ergebnis: aktualisierte Python-Datei.
  - Artefakt: `tools/generate_dynamic_functional_mlds.py`.
  - Verifikation: `py_compile` und In-Memory-Rendercheck fuer SVG, PNG, Mermaid und Spezifikation erfolgreich.
  - Abnahme: Generator erzeugt SVG, PNG, Mermaid und Spezifikation konsistent.

- [x] 13.3 Diagramm neu erzeugen.
  - Ergebnis: neues SVG und PNG.
  - Artefakte: `output/metamodel/dynamic_functional_mlds_metamodel.svg`, `output/metamodel/dynamic_functional_mlds_metamodel.png`, `output/metamodel/dynamic_functional_mlds_metamodel.mmd`, `output/metamodel/dynamic_functional_mlds_specification.md`.
  - Verifikation: Generatorlauf erfolgreich; PNG 2600x1650; `EntityKind` und `Effect.evidencedBy` in SVG/Mermaid/Spezifikation enthalten.
  - Abnahme: Renderprozess laeuft ohne Fehler.

- [x] 13.4 Kantenkreuzungen automatisch pruefen.
  - Ergebnis: Kreuzungsreport.
  - Artefakt: `output/metamodel/edge_crossing_report_13_4.md`.
  - Verifikation: 29 Kanten, 66 Segmente, `0` sichtbare Kantenkreuzungen.
  - Abnahme: `0` Kantenkreuzungen oder begruendete Ausnahme.

- [x] 13.5 Label-Overlaps automatisch pruefen.
  - Ergebnis: Overlap-Report.
  - Artefakt: `output/metamodel/label_overlap_report_13_5.md`.
  - Verifikation: 28 Edge-Labels, 24 Klassenboxen, `0` Label-Label-Overlaps, `0` Label-Klassen-Overlaps.
  - Abnahme: `0` Label-Label- und `0` Label-Klassen-Overlaps.

- [x] 13.6 Diagramm visuell pruefen.
  - Ergebnis: Sichtpruefung.
  - Artefakt: `output/metamodel/visual_inspection_report_13_6.md`.
  - Verifikation: PNG in voller Aufloesung geprueft; `Condition`-Box visuell korrigiert; danach `0` Kantenkreuzungen und `0` Label-Overlaps bestaetigt.
  - Abnahme: Keine abgeschnittenen oder unklar zugeordneten Labels.

- [x] 13.7 Spezifikation aktualisieren.
  - Ergebnis: deutsche Beschreibung mit Beispielen und Modellentscheidung.
  - Artefakte: `output/metamodel/dynamic_functional_mlds_specification.md`, `output/metamodel/specification_update_report_13_7.md`.
  - Verifikation: `KERN-01`, `KERN-01a`, `KERN-02`, Beispielpfade A/B, neue Kardinalitaeten und Invarianten enthalten.
  - Abnahme: Alle neuen oder geaenderten Klassen, Beziehungen, Kardinalitaeten und Invarianten sind beschrieben.

- [x] 13.8 Neuen Stand archivieren.
  - Ergebnis: neuer timestamped Snapshot.
  - Artefakte: `archive/metamodel_snapshot_20260708_004437`, `archive/metamodel_snapshot_20260708_004437.zip`, `output/metamodel/archive_report_13_8.md`.
  - Verifikation: Quelle und Snapshot abgeglichen; Manifest mit SHA-256-Hashes erzeugt; alter Snapshot `metamodel_snapshot_20260707_151224` bleibt unveraendert.
  - Abnahme: Alter Archivstand bleibt unveraendert erhalten.

## 14. Abschlusspruefung

- [ ] 14.1 Vollstaendigkeit gegen Aufgabenstellung pruefen.
  - Ergebnis: Checkliste `erfuellt/nicht erfuellt`.
  - Abnahme: Beide Anwendungsfaelle, beide Beispielsets, beide Mappings und Modellierbarkeitsentscheidung sind enthalten.

- [ ] 14.2 Fachliche Konsistenz pruefen.
  - Ergebnis: Reviewnotizen.
  - Abnahme: Keine Vermischung von Actor und Agent, fachlicher Capability und technischer RuntimeAction, Scenario und ValidationCase.

- [ ] 14.3 Kardinalitaeten final pruefen.
  - Ergebnis: Kardinalitaetsreport.
  - Abnahme: Jede Beziehung erfuellt die im Metamodell definierte Multiplizitaet.

- [ ] 14.4 Professoren-taugliche Argumentation pruefen.
  - Ergebnis: Liste moeglicher Rueckfragen und Antworten.
  - Abnahme: Include/Extend, ExtensionPoint, Satisfy, ScenarioStep, CapabilityUse und RuntimeBinding koennen sauber erklaert werden.

- [ ] 14.5 Finale Artefaktliste erstellen.
  - Ergebnis: Liste aller erzeugten Dateien.
  - Abnahme: Jede Datei hat Zweck und Pfad.
