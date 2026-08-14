# Käsesteinpilz · Interaktionsstudie

Die Anwendung verbindet den Unity-WebXR-Messestand mit einem vierstufigen Fragebogen. Antworten werden nach jeder Änderung zentral in SQLite gespeichert; unvollständige und abgeschlossene Teilnahmen sind über eine serverseitig PIN-geschützte Auswertungsseite einsehbar und als CSV oder JSON exportierbar.

## Lokaler Start

1. `.env.example` nach `.env` kopieren und `SURVEY_ADMIN_PIN` durch eine private PIN ersetzen.
2. `npm run dev` starten.
3. Teilnehmeransicht unter `https://localhost:3000`, Auswertung unter `https://localhost:3000/admin.html` öffnen.

Die PIN wird nie an den Browser-Build ausgeliefert. Datenbankdateien liegen in `data/` und werden nicht versioniert.

## Produktiver Start

`npm run build` erzeugt die Webseiten. `npm run preview` stellt anschließend Webseite, Unity-Build und API gemeinsam per HTTPS bereit. Vor einer öffentlichen Studie müssen ein vertrauenswürdiges TLS-Zertifikat, eine lange private PIN und eine regelmäßige Sicherung der SQLite-Datei eingerichtet sein.

Der große Unity-Build unter `BuildOutput/Build/` wird beim lokalen Build automatisch nach `dist/` übernommen, ist aber bewusst nicht in Git versioniert. Für ein Deployment auf einem anderen Rechner muss dieser Ordner daher separat mit übertragen oder aus dem Unity-Projekt neu exportiert werden.
