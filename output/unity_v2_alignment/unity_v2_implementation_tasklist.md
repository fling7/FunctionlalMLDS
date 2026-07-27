# Dynamic Functional MLDS V2 – Unity-/Backend-Implementierung

Stand: 2026-07-14  
Status: **Abgeschlossen und vollständig verifiziert**

## Ziel und verbindliche Leitplanken

Die bestehende Unity-/Backend-Anwendung wird auf das normative Metamodell
`2.0.0-model` ausgerichtet. Der bisherige v0.5-Vertrag bleibt als explizite
Kompatibilitätsfassung reproduzierbar und ausführbar.

Verbindlich sind dabei:

- kein direkter Laufzeitpfad `ScenarioStep -> RuntimeAction`;
- Ausführung ausschließlich über
  `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`;
- explizite Provider- und Target-Semantik für ausführbare V2-CapabilityUses;
- generische Assertions, strukturierte AssertionResults sowie getrennte
  V&V-Subjects und RuntimeValidationTargets;
- `StepRelation` als alleinige Quelle der Kontrollflusssemantik;
- verlustfreie Weiterverwendung aller bestehenden v0.5-Projekte;
- keine stillschweigende oder mehrdeutige Datenmigration.

## A. Bestandsaufnahme und Soll-Abgleich

- [x] **UV2-01 – Unity-Oberfläche inventarisieren.** Alle C#-DTOs, Loader,
  Runtime-Logger, Wizard- und Editor-Smoke-Pfade identifizieren.
- [x] **UV2-02 – Backend-Oberfläche inventarisieren.** Setup-, Chat-, Handoff-,
  Projekt-, Trace- und Runtime-Logging-Pfade gegen V2 prüfen.
- [x] **UV2-03 – Pipeline und Schemas inventarisieren.** Erzeuger, Validatoren,
  Materialisierung, JSON-Schemas und Traceability-Metriken erfassen.
- [x] **UV2-04 – Metamodell-zu-Implementierungsmatrix erstellen.** Jede für die
  ausführbare Anwendung relevante V2-Klasse, Beziehung und Invariante einem
  Implementierungs- und Testnachweis zuordnen.
- [x] **UV2-05 – Änderungsgrenze dokumentieren.** EAST-ADL-Spezifikation,
  Authoring-Modell, Runtime-Projektion und Unity-DTOs sauber trennen.

## B. v0.5-Archiv und Rückwärtskompatibilität

- [x] **UV2-06 – Aktuellen Implementierungsstand sichern.** Backend-, Unity-,
  Pipeline-, Schema- und Testquellen vor der V2-Anpassung archivieren.
- [x] **UV2-07 – v0.5-Modellvertrag sichern.** Generator, Schema, Invarianten,
  reale Instanzen und Trace-Maps in die Archivfassung aufnehmen.
- [x] **UV2-08 – Git-Ausgangszustände sichern.** Basis-Revisionen, geänderte und
  unversionierte Dateien der beiden eingebetteten Repositories dokumentieren.
- [x] **UV2-09 – Archiv manifestieren.** SHA-256-Manifest, Dateiliste,
  Wiederherstellungsanleitung und maschinenlesbare Metadaten erzeugen.
- [x] **UV2-10 – Archiv verifizieren.** Alle Manifest-Hashes sowie einen isolierten
  v0.5-Validator-/Backend-Smoke-Lauf gegen die Archivfassung prüfen.

## C. Versionierter Modell- und Serialisierungsvertrag

- [x] **UV2-11 – Dualen Artefaktvertrag definieren.** v0.5-Legacy-Dokument und
  normative V2-Instanz besitzen eindeutige Dateinamen, Versionen und Rollen.
- [x] **UV2-12 – V2-Projektion produktionsfähig machen.** Die bestehende
  verlustfreie Projektion als deterministischen Pipeline-Schritt integrieren.
- [x] **UV2-13 – Ausführbares V2-Profil ergänzen.** Provider, Targets,
  performedBy/providedCapability und Runtime-Kontext ohne Mehrdeutigkeit setzen.
- [x] **UV2-14 – Assertion-Modell serialisieren.** Alle fünf Assertion-Arten,
  EAExpression, Severity und Effect.specifiedBy abbilden.
- [x] **UV2-15 – V&V-Laufzeitdaten serialisieren.** RuntimeValidationTarget,
  AssertionOutcome, AssertionResult und RuntimeActualOutcome abbilden.
- [x] **UV2-16 – Kontrollfluss serialisieren.** StepRelations, ParallelGroups,
  Guards und Branch-Wahrscheinlichkeiten nach den V2-Invarianten ausgeben.
- [x] **UV2-17 – V2-Schema und Validator bereitstellen.** Referenzabschluss,
  Kardinalitäten, Profile und verbotene technische Kurzschlüsse prüfen.

## D. Backend- und Pipeline-Integration

- [x] **UV2-18 – Pipeline dual ausgeben lassen.** Jeder erfolgreiche Lauf erzeugt
  v0.5 und V2 deterministisch aus demselben fachlichen Stand.
- [x] **UV2-19 – Projektmaterialisierung auf V2 umstellen.** V2 wird primärer
  Modellpfad; v0.5 bleibt als expliziter Legacy-Pfad erhalten.
- [x] **UV2-20 – Trace-Map versionieren.** CapabilityUse, Provider, Targets,
  Assertions, ValidationTargets und RuntimeActions direkt auflösbar machen.
- [x] **UV2-21 – Setup-Runtimekontext bereitstellen.** Unity erhält Modellversion,
  Profil, IDs und Aktions-/Assertionsbezüge vom Backend statt aus Hardcodes.
- [x] **UV2-22 – Runtime-Logging V2-konform erweitern.** CapabilityUse-ID,
  Provider/Targets, AssertionResult und RuntimeActualOutcome protokollieren.
- [x] **UV2-23 – Backend weiterhin v0.5-fähig halten.** Versionsdetektion und
  Normalisierung müssen alte Projekte ohne Migration laden können.

## E. Unity-Integration

- [x] **UV2-24 – V2-DTOs implementieren.** Runtime-relevante Modell-, Trace-,
  Assertion-, V&V- und Ergebnisstrukturen Unity-serialisierbar abbilden.
- [x] **UV2-25 – Versionsfähigen Runtime-Kontext laden.** Setup-Antworten für V2
  und v0.5 erkennen, normalisieren und referenziell prüfen.
- [x] **UV2-26 – Hardcodierte Trace-IDs entfernen.** Setup, Chat und Handoff
  verwenden ausschließlich die vom Backend gelieferte Trace-Map.
- [x] **UV2-27 – Provider und Targets an Runtime-Ereignisse binden.** Der konkrete
  ausführende Agent und die betroffenen Identifiables werden mitgeführt.
- [x] **UV2-28 – AssertionResults in Unity erzeugen.** Pass, Fail, Inconclusive
  und Error inklusive Beobachtung, Evidenz und Zeitstempel serialisieren.
- [x] **UV2-29 – Unity-Quellkopien synchronisieren.** Kanonische Unity-Skripte,
  Projekt-Assets und Paket-/Smoke-Quellen müssen byte- bzw. semantikgleich sein.

## F. Tests und Nichtregression

- [x] **UV2-30 – V2-Projektions-Unit-Tests ergänzen.** Positive und negative
  Fälle für Provider, Targets, Assertions, V&V und Kontrollfluss abdecken.
- [x] **UV2-31 – Sieben reale Fälle dual prüfen.** v0.5-Roundtrip und gültige
  ausführbare V2-Ausgabe für alle vorhandenen Instanzen nachweisen.
- [x] **UV2-32 – Backend-Smoke auf V2 erweitern.** Setup, Chat und Handoff müssen
  vollständigen V2-Runtimekontext und auflösbare Traces liefern.
- [x] **UV2-33 – v0.5-Backend-Smoke erhalten.** Ein isolierter Legacy-Modus muss
  dieselben bisherigen Endpunkte und Ereignisse weiter bedienen.
- [x] **UV2-34 – Unity-DTO-/Loader-Tests ergänzen.** JSON-Roundtrip,
  Versionsdetektion, Referenzabschluss und Pflichtfelder prüfen.
- [x] **UV2-35 – Unity-Editor-Smoke erweitern.** V2-Setup, Chat, Handoff und
  AssertionResult im tatsächlich verwendeten Unity-Projekt prüfen.
- [x] **UV2-36 – C#-Kompilation prüfen.** Alle geänderten Skripte gegen die
  vorhandene Unity-/C#-Toolchain kompilieren.
- [x] **UV2-37 – Runtime-Trace-Nichtregression prüfen.** Bestehende Logs bleiben
  lesbar; neue Logs erfüllen den V2-Vertrag ohne unaufgelöste Referenzen.
- [x] **UV2-38 – Determinismus und Hashschutz prüfen.** Wiederholte Generierung
  liefert bytegleiche Modell-, Schema- und Trace-Artefakte.

## G. Abschluss und Heartbeat

- [x] **UV2-39 – Nachweismatrix vervollständigen.** Jede Task verweist auf Code,
  Test und erzeugtes Evidenzartefakt.
- [x] **UV2-40 – Betriebs- und Migrationsanleitung schreiben.** V2-Standard,
  v0.5-Legacy-Modus und Archivwiederherstellung dokumentieren.
- [x] **UV2-41 – Gesamtabnahme ausführen.** Modell-, Pipeline-, Backend-, Unity-,
  Archiv- und Nichtregressionsprüfungen gemeinsam ausführen.
- [x] **UV2-42 – Arbeitsbaum kontrollieren.** Nutzeränderungen bewahren und alle
  im Auftrag erzeugten Dateien eindeutig ausweisen.
- [x] **UV2-43 – Taskliste vollständig schließen.** Keine offene oder nur
  behauptete Task; alle 43 fachlichen Tasks besitzen überprüfbare Evidenz.
- [x] **UV2-44 – Heartbeat einrichten.** Wiederkehrend prüfen, ob diese Taskliste
  vollständig abgeschlossen und die Abnahme weiterhin grün ist.

## Definition of Done

Der Auftrag ist erst abgeschlossen, wenn:

1. alle Checkboxen `UV2-01` bis `UV2-44` geschlossen sind;
2. V2 der primäre ausführbare Vertrag für neue Projekte ist;
3. vorhandene v0.5-Projekte unverändert weiterlaufen;
4. das v0.5-Archiv unabhängig verifizierbar ist;
5. alle Modellreferenzen in Unity- und Backend-Traces auflösbar sind;
6. Provider, Targets, Assertions, RuntimeValidationTargets und AssertionResults
   nicht nur dokumentiert, sondern in positiven und negativen Tests belegt sind;
7. die Gesamt-Abnahme ohne Fehler und ohne ungeklärte Warnungen endet.

## Abschlussnachweise

- Gesamtabnahme: `unity_v2_alignment_acceptance.json` und
  `unity_v2_alignment_acceptance.md`
- Implementierungsinventar und Änderungsgrenze: `implementation_inventory.md`
- Metamodell-/Code-/Test-Matrix: `implementation_matrix.md`
- Migration, Betrieb und Archivwiederherstellung:
  `migration_and_operations_guide.md`
- Arbeitsbaumaudit: `worktree_change_audit.md`
- Python-Gesamttests: `pytest_tools_full_final.log` und
  `pytest_backend_full_final.log`
- Unity: `unity_final_v2_compile.log`, `unity_final_v2_smoke.log`,
  `unity_final_native_v2_smoke.log`, `unity_final_real_instance_validation.log`
  und `unity_final_real_instance_smoke.log`
- Heartbeat: `unity-v2-tasklisten-heartbeat` (30-Minuten-Intervall; nach
  erfolgreichem Abschluss pausiert)
