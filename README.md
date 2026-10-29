# RECA MAXMOBIL – kostenloser Online-Test

Dieses Paket enthält den aktuellen responsiven Pilot für Desktop und Smartphone.

## Wichtige Testgrenzen

- Nur anonymisierte Testaufträge verwenden. Keine echten Kunden-PDFs, Kennzeichen, Adressen, Fotos oder Unterschriften hochladen.
- Der aktuelle Pilot speichert Aufträge und Änderungen nur im Arbeitsspeicher des geöffneten Browsers. Es gibt keine dauerhafte Speicherung und keine Synchronisation zwischen Nutzern/Geräten. Beim Neuladen oder Schließen können Änderungen verloren gehen.
- Für gemeinsame produktive Nutzung mit Echtdaten sind mindestens individuelle Nutzerkonten, eine dauerhafte Datenbank und geschützter Dateispeicher erforderlich. Das ist in diesem Paket nicht enthalten.
- Render Free kann bei Inaktivität einschlafen. Der erste Aufruf danach kann verzögert sein. Der Gratis-Tarif hat Nutzungsgrenzen; prüfen Sie die Billing-Übersicht und setzen Sie, sofern verfügbar, eine Ausgabengrenze.
- Die Bereichspasswörter haben in diesem Testcode eine Mindestlänge von 4 Zeichen. Nur für einen anonymisierten, begrenzten Test einsetzen.

## Dateien im Repository ersetzen

1. Dieses ZIP lokal entpacken.
2. Die enthaltenen Dateien `index.html`, `server.py`, `render.yaml`, `.gitignore` und `README.md` im Stammverzeichnis des GitHub-Repositories ersetzen/aktualisieren. Keine Passwörter, `.env`-Dateien oder echten Aufträge hochladen.
3. In GitHub alle Änderungen auf `main` committen. Render sollte den verknüpften Webservice automatisch neu deployen. `plan: free` ist in `render.yaml` eingetragen.
4. In Render unter **Deploys** prüfen, dass der neue Deploy **Live** ist. Anschließend die Render-URL auf Desktop und Smartphone öffnen.
5. Die bestehenden Umgebungsvariablen in Render beibehalten: `SESSION_SECRET`, `PASS_EINBAUPARTNER`, `PASS_AUSSENDIENST`, `PASS_INNENDIENST`. Passwörter nicht im Repository ablegen.

## Lokaler Start (optional)

`SESSION_SECRET` muss mindestens 32 Zeichen haben. Jedes Bereichspasswort muss mindestens 4 Zeichen haben. Lokal mit Umgebungsvariablen starten: `COOKIE_SECURE=0 PORT=10000 python3 server.py`, anschließend `http://localhost:10000` öffnen.
