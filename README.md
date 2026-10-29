# RECA MAXMOBIL – interner Online-Pilot

**Nur anonymisierte Testdaten. Nicht für echte Kundenaufträge freigegeben.**

Dieser Stand schützt den Zugang zur Webseite serverseitig mit einem Bereichspasswort je Rolle. Die bestehende Browser-App arbeitet **weiterhin nur lokal im Speicher des jeweiligen Browsers**: PDF-Inhalte, Einträge und Nachrichten werden nicht zwischen Geräten synchronisiert und verschwinden beim Neuladen. Geteilte Passwörter erlauben keine personenscharfe Nachvollziehbarkeit. Das ist kein Produktivsystem.

## Veröffentlichung über GitHub + Render

1. ZIP entpacken. Ein **privates** GitHub-Repository anlegen und die vier Dateien (`index.html`, `server.py`, `render.yaml`, `.gitignore`, `README.md`) in dessen Stammverzeichnis hochladen. Keine echten PDFs, Passwörter oder `.env` ins Repository aufnehmen.
2. Bei [Render](https://dashboard.render.com/) anmelden. `New` → `Blueprint` wählen, GitHub verbinden und das Repository auswählen. Render liest `render.yaml`.
3. Für `PASS_EINBAUPARTNER`, `PASS_AUSSENDIENST` und `PASS_INNENDIENST` jeweils **unterschiedliche, lange Passwörter (mindestens 16 Zeichen)** in Render hinterlegen. `SESSION_SECRET` erzeugt Render automatisch. Geheime Werte gehören nur in die Render-Umgebungsvariablen.
4. Deployment abschließen, die von Render angezeigte HTTPS-Adresse auf dem Smartphone öffnen und einen der drei Bereiche anmelden. Für PDF-Auslesen ist eine Verbindung zum externen PDF-Bibliotheks-CDN nötig.
5. Falls Render den Blueprint nicht anbietet: `New` → `Web Service`, Repository auswählen; Runtime Python; Build Command `echo ready`; Start Command `python3 server.py`; Environment wie oben setzen; Health Check `/health`.

Für lokale Prüfung können die vier Variablen temporär in der **eigenen Shell** gesetzt werden; danach `COOKIE_SECURE=0 PORT=10000 python3 server.py` und `http://localhost:10000` öffnen. Diese Ausnahme gilt nur lokal ohne HTTPS.

## Grenzen dieses Piloten

- Keine Benutzerkonten pro Person, keine dauerhafte Speicherung, keine echte Zusammenarbeit zwischen Geräten, kein revisionssicheres Abnahmeprotokoll.
- Passwortschutz sitzt am Server; die Anwendung selbst ist die bisherige Browser-Demo mit Beispieldaten. Jemand mit dem Bereichspasswort kann den Demo-Inhalt sehen und bearbeiten, aber Änderungen gehen bei Neuladen verloren.
- Eine veröffentlichte Render-URL ist im Internet erreichbar. **Keine Kunden-PDFs, Fahrzeugfotos, Unterschriften oder echten personenbezogenen Daten hochladen.** Für Echtdaten werden persönliche Konten, Berechtigungen auf Auftrags-/Mandantenebene, persistente Datenbank und geschützter Dateispeicher, Audit-Protokoll, Löschkonzept und Datenschutzprüfung benötigt.
