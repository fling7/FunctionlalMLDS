# Research Questions for the FunctionalMLDS Case Study

## Ziel der Case Study

Die Case Study untersucht, ob das FunctionalMLDS-Metamodell eine bestehende MLDS-basierte Raumgenerierung so erweitert, dass interaktive Agenten nicht nur erzeugt, sondern auch nachvollziehbar spezifiziert, validiert und zur Laufzeit geprueft werden koennen. Der Untersuchungsgegenstand ist eine modulare Pipeline von MLDS-Dateien ueber FunctionalMLDS-Instanzen bis zu einem Interactive-Agents-Projekt mit Backend- und Runtime-Checks.

## RQ1: Tracebare Modellierbarkeit

**RQ1. In welchem Umfang kann FunctionalMLDS die Transformation von MLDS-Rauminformationen zu interaktiven Agenten tracebar modellieren?**

Motivation:
Direkte MLDS-zu-Agenten-Generierung erzeugt zwar lauffaehige Artefakte, aber ohne explizite Kette zwischen Szenenobjekten, Agentenrollen, Wissen, Capabilities, Runtime-Bindings und Validierungsereignissen. FunctionalMLDS soll diese Kette als pruefbare Modellstruktur bereitstellen.

Operationalisierung:
- Objektgruppen muessen auf Agentenrollen und Wissensbereiche abbildbar sein.
- Requirements muessen Validierungsfaelle oder Runtime-Checks besitzen.
- RuntimeActions muessen, soweit zur Laufzeit beobachtbar, auf RuntimeLogEvents abbildbar sein.
- Die FunctionalMLDS-Instanz muss Schema- und Invariantenpruefungen bestehen.

Primaere Evidenz:
- `average_trace_coverage = 0.847222`
- `average_requirement_to_validation_coverage = 1.0`
- `average_object_group_coverage = 1.0`
- `functionalmlds_invariants`: 3/3 Cases erfolgreich
- `schema_validation`: 3/3 Cases erfolgreich

Interpretation:
RQ1 gilt als unterstuetzt, wenn die Pipeline fuer alle Cases gueltige FunctionalMLDS-Instanzen erzeugt und die zentralen Trace-Ketten ohne manuelle Nachmodellierung messbar sind. Die niedrigere RuntimeAction-to-Log-Coverage ist kein Gegenbeleg, sondern markiert die bewusst engere Grenze runtime-beobachtbarer Aktionen.

## RQ2: Pruefbarkeit gegenueber direkter Generierung

**RQ2. Erhoeht FunctionalMLDS die Pruefbarkeit einer MLDS-zu-Agenten-Pipeline gegenueber direkter Artefaktgenerierung ohne explizite Metamodellinstanz?**

Motivation:
Ein wissenschaftlich relevantes Modell muss nicht nur Artefakte erzeugen, sondern Fehlerstellen lokalisierbar machen. FunctionalMLDS fuehrt dafuer Validierungsstufen, Repair-Loops, Traceability-Metriken und Runtime-orientierte Testartefakte ein.

Operationalisierung:
- Jede Pipeline-Stufe erzeugt validierbare Ein- und Ausgabehashes im Stage Manifest.
- Fehler werden pro Stage gemessen, nicht nur als globaler Pipelineabbruch.
- Handoff-Entscheidungen und Chat-Antworten werden durch automatisch generierte Testfragen geprueft.
- Reparaturversuche bleiben nachvollziehbar und auf einzelne Stufen begrenzt.

Primaere Evidenz:
- `average_stage_completion_ratio = 1.0`
- `total_chat_tests = 66`, `successful_chat_tests = 66`
- `total_handoff_decision_tests = 66`
- `average_handoff_accuracy = 1.0`
- `average_answer_grounding_ratio = 1.0`
- Stage-Fehler im finalen Aggregate Report: 0
- Repair-/Generierungsprotokoll nachvollziehbar: 8 erfolgreiche LLM-Erstgenerierungen, 0 LLM-Reparaturversuche, 1 deterministische Recovery, 3 akzeptierte Traceability-Warnungen

Interpretation:
RQ2 gilt als unterstuetzt, wenn die Treatment-Pipeline nicht nur lauffaehige Agenten erzeugt, sondern fuer jede relevante Modellschicht konkrete Validierungsartefakte liefert. Die spaetere Baseline muss zeigen, welche dieser Pruefpunkte bei direkter Generierung fehlen oder nur implizit vorhanden sind.

## RQ3: Domaenenuebergreifende Anwendbarkeit

**RQ3. Bleibt die FunctionalMLDS-basierte Pipeline ueber unterschiedliche MLDS-Domaenen hinweg ohne domaenenspezifischen Pipeline-Code anwendbar?**

Motivation:
Das Metamodell soll nicht nur fuer einen einzelnen Demonstrator funktionieren. Es muss fuer unterschiedliche Rauminhalte dieselbe Abstraktionslogik nutzen: Szenenobjekte, Agentenrollen, Wissensbereiche, Interaktionen, Runtime-Bindings und Validierung.

Operationalisierung:
- Mindestens drei unterschiedliche MLDS-Domaenen werden mit derselben Pipeline verarbeitet.
- Alle Cases nutzen dasselbe Stage-Set.
- Domaenenspezifische Begriffe liegen in MLDS-Daten, Konfigurationsdateien oder Prompts, nicht im Python-Pipeline-Code.
- Runtime-Verhalten bleibt ueber alle Domaenen erfolgreich.

Primaere Evidenz:
- Cases: 3
- Domaenen: 3
- Generalizability Score: 1.0
- `domain_terms_externalized`: 25 Python-Dateien gescannt, 0 Treffer
- `same_pipeline_stages`: bestanden
- `runtime_behavior_cross_domain`: bestanden

Interpretation:
RQ3 gilt als unterstuetzt, wenn neue MLDS-Dateien ueber CLI-Inputs oder Konfiguration eingespeist werden koennen und die Pipeline keine fest verdrahteten Annahmen ueber Food/Brand, Education oder Career-Fair-Szenen enthaelt.

## Erwarteter Beitrag

Die drei Forschungsfragen bilden zusammen den wissenschaftlichen Kern der Case Study:
- RQ1 bewertet die Modellierbarkeit und Traceability des Metamodells.
- RQ2 bewertet die methodische Pruefbarkeit und Reparierbarkeit der Pipeline.
- RQ3 bewertet die Generalisierbarkeit ueber unterschiedliche MLDS-Domaenen.

Damit zeigt die Case Study nicht nur, dass ein Interactive-Agents-Projekt erzeugt werden kann, sondern dass FunctionalMLDS als explizite Zwischenrepraesentation wissenschaftlich auswertbare Evidenz produziert.
