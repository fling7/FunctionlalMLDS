# Kriterien 11.2: Wann ist ein Ergaenzungsmodell gerechtfertigt?

Stand: 2026-07-07

Task: 11.2 `Kriterien fuer Ergaenzungsmodell festlegen`

Zweck: Diese Kriterien legen fest, wann ein identifizierter Modellierungsbedarf nicht in den Kern gehoert, aber trotzdem als optionales, formal beschreibbares Ergaenzungsmodell ausgearbeitet werden sollte.

Bezugsdateien:

- `core_adaptation_criteria.md`
- `common_concepts_A_B.md`
- `differences_A_B.md`
- `state_assertion_object_state_decision.md`
- `capability_runtime_vivian_action_decision.md`
- `spatial_relationship_decision.md`
- `interaction_object_affordance_decision.md`
- `agent_goal_role_runtime_profile_decision.md`

## Grundregel

Ein Ergaenzungsmodell ist gerechtfertigt, wenn ein Bedarf fuer automatische Pruefung, Generierung, Validierung oder Runtime-Anbindung fachlich relevant ist, aber den Kern wegen Domaenenspezifik, optionaler Nutzung, Detailtiefe oder technischer Naehe unnoetig belasten wuerde.

Das Ergaenzungsmodell muss an bestehende Kernklassen andocken und darf die Kernkette nicht ersetzen:

`Requirement -> UseCase -> Scenario -> ScenarioStep -> Event/Condition/StateAssertion -> CapabilityUse -> Capability -> Effect -> RuntimeBinding -> RuntimeAction -> ValidationCase`

Der Kern muss ohne das Ergaenzungsmodell gueltig bleiben. Das Modul erhoeht Praezision, aber es darf keine Pflicht fuer jedes Modell werden.

## Pflichtkriterien fuer ein Ergaenzungsmodell

Alle Pflichtkriterien muessen fuer ein echtes Ergaenzungsmodell erfuellt sein.

| ID | Pflichtkriterium | Prueffrage | Nachweis |
| --- | --- | --- | --- |
| E1 | Domaenenspezifik oder Detailtiefe | Ist der Bedarf fuer bestimmte Domaenen, Beispiele, Runtimes oder Praezisionsstufen besonders relevant, aber nicht allgemein genug fuer den Kern? | A-getriebene Spatial Semantics, B-getriebene Affordances oder Vivian-Dialog. |
| E2 | Optionale Nutzung | Kann ein gueltiges Kernmodell ohne dieses Modul existieren? | A- und B-Baseline bleiben mit Kernklassen abbildbar. |
| E3 | Geringe Belastung des Kerns | Entlastet das Modul den Kern, statt ihn mit Spezialklassen zu ueberladen? | Keine neue Pflichtklasse im Kern; Modul ist zuschaltbar. |
| E4 | Klare Anschlussstelle | Referenziert das Modul bestehende Kernklassen mit eindeutiger Richtung und Kardinalitaet? | Andockpunkte wie `Entity`, `Agent`, `Event`, `Condition`, `StateAssertion`, `Capability`, `RuntimeBinding`. |
| E5 | Maschinenlesbarer Mehrwert | Liefert das Modul mehr als nur bessere Dokumentation? | Es ermoeglicht Pruefung, Generierung, Konsistenzanalyse oder gezielte Runtime-Auswahl. |
| E6 | Invariantenvertraeglichkeit | Bleiben Actor/Agent-Trennung, fachlich/technisch-Trennung und Scenario/Runtime-Trennung erhalten? | Keine direkte `ScenarioStep -> RuntimeAction`- oder `Affordance -> RuntimeAction`-Kurzschlusskante. |
| E7 | Abgrenzbare Semantik | Hat das Modul einen klaren fachlichen Gegenstand und wiederholt keine Kernklasse unter anderem Namen? | `InteractionObject` beschreibt Bedienbarkeit, nicht allgemeine Identitaet wie `Entity`. |
| E8 | Rueckwaertskompatibilitaet | Koennen bestehende Instanzen ohne Modul weiter verstanden werden? | Expressions und StateAssertions bleiben gueltig, werden nur optional strukturiert. |

## Harte Ausschlusskriterien

Wenn eines dieser Kriterien zutrifft, sollte kein Ergaenzungsmodell angelegt werden.

| Ausschluss | Bedeutung | Beispiel |
| --- | --- | --- |
| Reine Dokumentation | Es entsteht keine neue pruefbare Semantik. | Ein Glossar fuer schoenere Begriffe ohne Modellbeziehungen. |
| Einzelinstanz statt wiederkehrendem Bedarf | Der Bedarf betrifft nur einen einmaligen Sonderfall. | Ein spezieller Buttonname ohne wiederverwendbare Affordance-Struktur. |
| Kernverletzung | Das Modul umgeht bestehende Invarianten. | `ScenarioStep -> RuntimeAction` im Modul. |
| Kernersatz statt Kernandockung | Das Modul modelliert Requirement, UseCase oder Scenario neu statt sie zu referenzieren. | Eigenes Workflow-Modell, das `ScenarioStep` ersetzt. |
| Technische Implementierung ohne Modellsemantik | Der Bedarf ist reine Code-, API- oder Deployment-Konfiguration. | Ein konkreter Unity-Methodenname ohne fachliche Bindung. |
| Besserer Kernkandidat | Der Bedarf ist allgemein, kompakt, EAST-ADL-nah und wiederverwendbar. | Kleine optionale Trace-Kante, falls alle Kernkriterien erfuellt sind. |
| Unklare Kardinalitaet | Anschlussstellen, Besitz oder Multiplizitaeten lassen sich nicht eindeutig bestimmen. | Modulkonzept haengt zugleich beliebig an Step, Entity, Runtime und Validation ohne Regel. |

## Modulqualitaetskriterien

Diese Kriterien bewerten, ob ein vorgeschlagenes Ergaenzungsmodell wissenschaftlich sauber zugeschnitten ist.

| ID | Qualitaetskriterium | Leitfrage |
| --- | --- | --- |
| Q1 | Kleine Schnittstelle | Hat das Modul wenige, stabile Andockpunkte an den Kern? |
| Q2 | Hohe Kohesion | Beschreiben die Modulklassen wirklich denselben fachlichen Bereich? |
| Q3 | Lose Kopplung | Kann das Modul weggelassen werden, ohne den Kern zu brechen? |
| Q4 | Explizite Nicht-Ziele | Ist klar, was im Kern bleibt und was nicht Aufgabe des Moduls ist? |
| Q5 | Modulinteraktion geregelt | Ist festgelegt, wie das Modul mit anderen Modulen zusammenarbeitet? |
| Q6 | Validierbare Kardinalitaeten | Sind alle Beziehungen mit Multiplizitaet, Richtung und Besitzsemantik definiert? |
| Q7 | Graduelle Nutzbarkeit | Kann das Modul teilweise genutzt werden, ohne alle Spezialfaelle zu modellieren? |
| Q8 | Toolchain-Freundlichkeit | Laesst sich das Modul durch Generatoren, Validatoren oder Runtime-Adapter nutzen? |
| Q9 | Keine technische Verschmutzung fachlicher Klassen | Runtime-nahe Angaben bleiben unter `RuntimeBinding`, `RuntimeAction` oder Runtime-Ergaenzungen. |
| Q10 | Beispielnachweis | Gibt es mindestens ein klares A- oder B-Beispiel, das den Mehrwert zeigt? |

## Entscheidungsmuster

| Ergebnis | Regel |
| --- | --- |
| `Ergaenzungsmodell` | E1 bis E8 sind erfuellt, kein Ausschlusskriterium trifft zu, und die Modulqualitaet ist ausreichend. |
| `Ergaenzungsmodell mit reduziertem Zuschnitt` | Der Bedarf ist echt, aber der vorgeschlagene Modulumfang ist zu gross oder zu eng gekoppelt. |
| `kein Modellbedarf` | Die Baseline ist mit Kernklassen, Expressions, StateAssertions und Dokumentation ausreichend. |
| `Kernkandidat` | Der Bedarf erfuellt die Kernkriterien aus 11.1 besser als die Modulkriterien. |
| `zurueckstellen` | Der Bedarf ist plausibel, aber Beispiele, Kardinalitaeten oder Andockpunkte fehlen. |

Ein Modul muss also nicht "klein genug fuer den Kern" sein. Es muss klar genug sein, um den Kern kontrolliert zu erweitern, ohne ihn zu veraendern.

## Typische Modulkategorien

| Modulkategorie | Wann geeignet? | Typische Andockpunkte |
| --- | --- | --- |
| Fachlich-strukturelles Modul | Wenn eine fachliche Semantik maschinenlesbar werden soll, aber nicht fuer alle Modelle gilt. | `Entity`, `Agent`, `Event`, `Condition`, `StateAssertion`, `Capability` |
| Dialog-/Assistenzmodul | Wenn Inhalte, Dialogakte, Antwortoptionen oder Strategien formal werden. | `Agent`, `Capability`, `ScenarioStep`, `RuntimeBinding` |
| Spatial-/Interaktionsmodul | Wenn Raeume, Zonen, Bedienpunkte oder Affordances formal werden. | `Entity`, `Event`, `Condition`, `StateAssertion` |
| Runtime-Ergaenzung | Wenn Profil, Reihenfolge, Retry, Adapter oder Schemaauswahl formal werden. | `RuntimeBinding`, `RuntimeAction`, optional `ValidationCase` |
| Validation-/Assertion-Modul | Wenn Teststimuli und erwartete Outcomes maschinenlesbar verknuepft werden. | `ValidationCase`, `Event`, `StateAssertion`, `RuntimeBinding` |
| Safety-/Argumentationsmodul | Wenn Safety-Argumente, Hazards, Mitigations oder Nachweisstrukturen explizit werden. | `Requirement`, `Satisfy`, `ValidationCase`, `StateAssertion` |

## Anwendung auf bekannte Kandidaten als Plausibilitaetscheck

Diese Tabelle ist noch nicht die vollstaendige Bewertung aus Task 11.3. Sie prueft nur, ob die Modulkriterien erwartbar wirken.

| Kandidat | Erwartete Einordnung | Warum Modul statt Kern? | Primaere Anschlussstellen |
| --- | --- | --- | --- |
| `SpatialSemanticsModule` | Ergaenzungsmodell | Raumgeometrie, Toleranzen, Sichtbarkeit und Erreichbarkeit sind detailreich und vor allem A-getrieben. | `Entity`, `Condition`, `StateAssertion`, `Event` |
| `InteractionObjectModule` | Ergaenzungsmodell | Bedienpunkte und Affordances sind in B zentral, aber nicht fuer jedes Modell notwendig. | `Entity`, `Event`, `Condition`, `StateAssertion`, `Capability` |
| `AssistantInteractionModule` | Ergaenzungsmodell | Vivian-Dialog und GuidanceContent sind B-spezifisch und optional. | `Agent`, `Capability`, `ScenarioStep`, `RuntimeBinding` |
| `StateTransitionModule` | Ergaenzungsmodell | Formale Automaten sind hilfreich, aber die Baseline kann Zustaende mit `StateAssertion` ausdruecken. | `StateAssertion`, `Condition`, `Event`, `Effect` |
| `EventDetailModule` | Ergaenzungsmodell | Quelle, Ziel, Payload und Kanal sind maschinenlesbar nuetzlich, aber nicht immer notwendig. | `Event`, `Entity`, `Actor`, `ScenarioStep` |
| `DecisionRuleModule` | Ergaenzungsmodell | Readiness, Diagnose und Auswahlregeln sind fachlich wichtig, aber nicht allgemeiner Kern. | `Condition`, `Capability`, `StateAssertion`, `ValidationCase` |
| `AgentBehaviorModule` | Ergaenzungsmodell | Interne Ziele, Policies und Rollenautomaten gelten nur bei erweitertem Autonomie-Scope. | `Agent`, `Capability`, `StateAssertion`, `Condition` |
| `RuntimeProfileModule` | Ergaenzungsmodell | Plattform-, Adapter- und Modellprofile sind technisch und sollen den fachlichen Kern nicht belasten. | `RuntimeBinding`, `RuntimeAction` |
| `RuntimeExecutionModule` | Ergaenzungsmodell | Reihenfolge, Retry, Transaktion und Fehlerbehandlung liegen unter Runtime-Anbindung. | `RuntimeBinding`, `RuntimeAction`, `ValidationCase` |
| `ValidationAssertionModule` | Ergaenzungsmodell | Komplexe Testorakel sind wichtig fuer Automatisierung, aber nicht fuer jedes Use-Case-Modell. | `ValidationCase`, `StateAssertion`, `Event` |

## Schnittstellenregeln fuer jedes Ergaenzungsmodell

| Regel | Bedeutung |
| --- | --- |
| S1 | Jede Modulklasse muss mindestens einen klaren Bezug zu einer Kernklasse besitzen. |
| S2 | Eine Modulklasse darf keine Kernklasse ersetzen, sondern nur verfeinern oder referenzieren. |
| S3 | Jede Modulbeziehung braucht Multiplizitaet, Richtung und Besitzsemantik. |
| S4 | Technische Ausfuehrung darf nur ueber `RuntimeBinding` und `RuntimeAction` konkret werden. |
| S5 | Fachliche Bedienung, Dialog, Raum oder Policy duerfen nicht direkt an technische Endpoints gebunden werden. |
| S6 | Das Kernmodell muss ohne das Modul gueltig bleiben. |
| S7 | Modulinstanzen muessen aus bestehenden Kerninstanzen ableitbar oder mit ihnen verknuepfbar sein. |
| S8 | Modulregeln muessen als Validator- oder Review-Regeln formulierbar sein. |

## Mindestdokumentation je Ergaenzungsmodell

Falls spaeter ein Ergaenzungsmodell spezifiziert wird, muss es mindestens folgende Informationen enthalten:

| Pflichtangabe | Inhalt |
| --- | --- |
| Modulname und Scope | Welche Semantik das Modul abdeckt und wann es benutzt wird. |
| Nicht-Ziele | Was explizit im Kern oder in anderen Modulen bleibt. |
| Anschlussstellen | Bestehende Kernklassen, an die das Modul andockt. |
| Klassen und Attribute | Neue Modulklassen mit kurzer Definition. |
| Beziehungen und Kardinalitaeten | Quelle, Ziel, Richtung, Multiplizitaet und Komposition/Assoziation. |
| Modul-Invarianten | Regeln, die Fehlmodellierung verhindern. |
| Modulabhaengigkeiten | Welche anderen optionalen Module benutzt oder referenziert werden duerfen. |
| Beispielinstanzen | Mindestens ein A- oder B-Beispiel. |
| Validierungsregeln | Wie ein Modellpruefer die Modulinstanzen kontrollieren kann. |
| Migrationsregel | Wie vorhandene Kernmodelle ohne Modul gueltig bleiben. |

## Abnahmekontrolle

| Kriterium aus Task 11.2 | Erfuellung |
| --- | --- |
| Kriterienliste vorhanden | Pflicht-, Ausschluss-, Qualitaets- und Schnittstellenkriterien sind definiert. |
| Domaenenspezifik enthalten | E1 fordert Domaenenspezifik oder Detailtiefe als Modulgrund. |
| Optionale Nutzung enthalten | E2 und S6 fordern, dass der Kern ohne Modul gueltig bleibt. |
| Geringe Belastung des Kerns enthalten | E3 fordert Kernentlastung und keine neue Pflichtklasse. |
| Anschlussstellen geregelt | E4 und S1 bis S3 verlangen klare Andockpunkte und Kardinalitaeten. |
| Entscheidungsregel vorhanden | Abschnitt `Entscheidungsmuster` unterscheidet Ergaenzungsmodell, Kernkandidat, kein Modellbedarf und zurueckstellen. |
| Vorbereitung fuer 11.3 vorhanden | Bekannte Kandidaten sind als Plausibilitaetscheck gegen die Kriterien gespiegelt. |

## Konsequenz fuer Task 11.3

Task 11.3 kann nun jede identifizierte Luecke gegen zwei Kriterienmengen pruefen:

- `core_adaptation_criteria.md` fuer die Entscheidung `Kern`,
- diese Datei fuer die Entscheidung `Ergaenzung`,
- und `kein Modellbedarf`, wenn weder Kern noch Ergaenzungsmodell notwendig ist.
