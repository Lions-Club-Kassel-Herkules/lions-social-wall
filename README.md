# Lions Social Wall – Einrichtungsanleitung

Instagram-Wall für **kassel-herkules.lions.de**: Die neuesten Beiträge eures Instagram-Kontos erscheinen als Raster im Format 4:5 mit Likes, Aufrufen und Datum. Antippen öffnet eine Großansicht im Glas-Look mit Button zu Instagram. Karussells blenden automatisch weiter, Reels zeigen ihr Titelbild. Weil lions.de nur ein iframe erlaubt, passt sich die Wall in eine feste Höhe ein und blättert mit „Ältere / Neuere“ bzw. per Wischen.

Die Einrichtung dauert einmalig etwa 1–2 Stunden, Danach läuft alles von selbst.

---

## So funktioniert es

```
Instagram ──(stündlich: Beiträge, Likes, Aufrufe)──▶ GitHub-Repository
                                                     • Tresor: alle Zugangsdaten
                                                     • Motor: Abruf + Veröffentlichung
                                    ──(nur öffentliche Dateien)──▶ GitHub Pages (Wall-Seite)
                                                                   ──(iframe)──▶ kassel-herkules.lions.de
```

**Wo liegt was?**

| Was | Wo | Wer kann es sehen? |
|---|---|---|
| Instagram-Passwort | nur bei Instagram | niemand sonst |
| Instagram-Token (nur Leserechte) | GitHub-Tresor `IG_TOKEN` | niemand, auch ihr nicht (Secrets sind nach dem Speichern nicht mehr lesbar) |
| Tresor-Schlüssel (darf nur den Tresor dieses Repos aktualisieren) | GitHub-Tresor | niemand |
| Programmcode | Repository (vorerst öffentlich) | alle (enthält nichts Geheimes) |
| Bilder, Zahlen, Wall-Seite | GitHub Pages | öffentlich (wie auf eurem Profil) |
| Einbettungs-Code | lions.de | öffentlich, enthält nichts Geheimes |

**Kosten:** keine. Solange das Repository **öffentlich** ist, sind GitHub Pages und die Abläufe kostenlos. Sichtbar ist dann nur der Programmcode, die Zugangsdaten bleiben im Tresor. Sobald GitHub for Nonprofits euch den Team-Tarif freischaltet, könnt ihr das Repository auf **privat** umstellen (*Settings → General → Danger Zone → Change visibility*). Der Team-Tarif enthält 3.000 Actions-Minuten pro Monat, der stündliche Abruf braucht etwa 720–1.000.

**Aktiv halten:** Öffentliche Repositories pausieren Zeitpläne nach 60 Tagen ohne Änderung. Der wöchentliche Ablauf *Instagram-Token erneuern* speichert deshalb bei Bedarf automatisch eine leere Änderung, damit die Wall nie einschläft.

---

## Schritt 1 – Vorbereitung

Ihr braucht:

- **Instagram-Konto des Clubs** als professionelles Konto ✔ habt ihr
- **Club-E-Mail-Adresse** aus eurem Google Workspace, z. B. `social@…`
- **Nachweis der Gemeinnützigkeit**, z. B. den Freistellungsbescheid des Fördervereins, für GitHub for Nonprofits
- **Facebook-Konto** einer Person aus dem Vorstand für das Meta-Entwicklerportal (Schritt 5)
- **Zwei-Faktor-Anmeldung** überall einschalten: Instagram, GitHub, Meta

---

## Schritt 2 – GitHub einrichten

1. Auf **github.com** ein Konto mit der Club-Adresse anlegen und die Zwei-Faktor-Anmeldung einschalten.
2. Oben rechts **+ → New organization → Free** wählen und z. B. `lions-kassel-herkules` nennen. Später einen zweiten Owner aus dem Vorstand hinzufügen.
3. *Optional, jederzeit nachholbar:* **GitHub for Nonprofits** beantragen (nonprofits.github.com → „Join GitHub for Nonprofits“ → Organisation auswählen → Nachweis hochladen → „Continue with Team“). Danach kann das Repository privat werden.
4. In der Organisation **New repository** wählen, Name `lions-social-wall`, **Public** einstellen und **Create repository** klicken. Der Name ist Teil der späteren Adresse.
5. Den Inhalt dieses Pakets hochladen: **Add file → Upload files** wählen und alle Dateien und Ordner hineinziehen, auch den versteckten Ordner `.github`. Dann **Commit changes** klicken.
   *Tipp:* Versteckte Dateien zeigt der Mac mit `⌘ + ⇧ + .` an, Windows unter „Ansicht → Ausgeblendete Elemente“. Alternativ geht der Upload mit **GitHub Desktop**.
6. Kontrolle: Unter **Actions** sollten vier Abläufe erscheinen: *Wall aktualisieren*, *Instagram-Token erneuern*, *Instagram verbinden* und *Einrichtung prüfen*.

> **Variablen und Secrets anlegen:** Repository → **Settings → Secrets and variables → Actions**. Dort gibt es zwei Reiter:
> **Secrets** sind geheim und nach dem Speichern nicht mehr lesbar. **Variables** sind nicht geheim.

---

## Schritt 3 – Tresor-Schlüssel erstellen

Damit GitHub den Instagram-Token selbst erneuern und im Tresor ablegen kann, braucht es einen Schlüssel, der **nur** den Tresor dieses einen Repositories beschreiben darf.

1. Profilbild → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
2. **Token name:** `Lions Wall Tresor`. Bei **Resource owner** eure Organisation wählen.
3. **Expiration:** so lang wie möglich und das Ablaufdatum in den Club-Kalender eintragen.
4. **Repository access → Only select repositories →** `lions-social-wall`
5. **Permissions → Repository permissions → Secrets: Read and write**. Sonst nichts.
6. Auf **Generate token** klicken, den Schlüssel kopieren und im Repository als **Secret** `TRESOR_SCHLUESSEL` speichern.

Falls die Organisation solche Schlüssel blockiert: Organisation → Settings → Personal access tokens → zulassen bzw. die Anfrage genehmigen.

---

## Schritt 4 – GitHub Pages einschalten

1. Repository → **Settings → Pages → Build and deployment → Source: „GitHub Actions“** wählen.
2. Die Wall wird später unter dieser Adresse erreichbar sein:
   `https://EURE-ORGANISATION.github.io/lions-social-wall/`
   Diese Adresse braucht ihr in Schritt 5, 6 und 8.

*Optional: eigene Adresse wie `wall.foerderverein-domain.de`.* Bei IONOS unter *Domains & SSL → DNS* einen **CNAME**-Eintrag `wall` → `EURE-ORGANISATION.github.io` anlegen. Dann in GitHub unter *Settings → Pages → Custom domain* die Adresse eintragen und **Enforce HTTPS** aktivieren. Nötig ist das nicht, denn im iframe sieht niemand die Adresse.

---

## Schritt 5 – Meta-App anlegen

*Die Menüs bei Meta ändern sich gelegentlich, die Begriffe bleiben aber ähnlich.*

1. Auf **developers.facebook.com** anmelden und, falls nötig, als Entwickler registrieren.
2. **Meine Apps → App erstellen**. Anwendungsfall: **„Nachrichten und Inhalte auf Instagram verwalten“** (engl. *Manage messaging & content on Instagram*). App-Name: `Lions Social Wall`.
3. Im Anwendungsfall unter **Berechtigungen** sicherstellen, dass `instagram_business_basic` und `instagram_business_manage_insights` vorhanden sind. Mehr braucht die Wall nicht.
4. **API-Einrichtung mit Instagram-Login → Instagram-Business-Login einrichten → Business-Login-Einstellungen:**
   - Bei **OAuth-Weiterleitungs-URIs** die Wall-Adresse aus Schritt 4 eintragen, z. B. `https://EURE-ORGANISATION.github.io/lions-social-wall/`, und speichern.
   - Dort stehen auch **Instagram-App-ID** und **Instagram-App-Geheimcode**. Wichtig: Das sind die Instagram-Werte, nicht die Facebook-App-ID.
5. In GitHub anlegen:
   - **Variable** `IG_APP_ID` = Instagram-App-ID
   - **Variable** `IG_REDIRECT_URI` = die Wall-Adresse, exakt wie bei Meta, mit `/` am Ende
   - **Secret** `IG_APP_SECRET` = Instagram-App-Geheimcode
6. Die App kann im Modus **„Entwicklung“** bleiben, denn sie greift nur auf euer eigenes Konto zu. Falls Meta beim Login meldet, das Konto sei nicht berechtigt: Unter **App-Rollen** das Instagram-Konto als **Instagram-Tester** hinzufügen und die Einladung in Instagram annehmen (*Einstellungen → Apps und Websites*).
7. Unter **App-Rollen** eine zweite Person aus dem Vorstand als Admin eintragen.

---

## Schritt 6 – Instagram verbinden

1. Diese Adresse anpassen, also `IG_APP_ID` und die Wall-Adresse (URL-kodiert) ersetzen, und im Browser öffnen:

   ```
   https://www.instagram.com/oauth/authorize?client_id=IG_APP_ID&redirect_uri=https%3A%2F%2FEURE-ORGANISATION.github.io%2Flions-social-wall%2F&response_type=code&scope=instagram_business_basic%2Cinstagram_business_manage_insights
   ```

   Die Adresse fragt genau **zwei Leserechte** an: Beiträge lesen und Aufrufe lesen. Schreibrechte werden nicht vergeben. Erteilt der Login trotzdem mehr, bricht die Einrichtung absichtlich ab.
2. Mit dem **Instagram-Konto des Clubs** anmelden und **Zulassen** tippen.
3. Ihr landet auf der Wall-Adresse mit `?code=…` dahinter. Falls Pages noch nicht läuft, erscheint dort eine Fehlerseite. Das ist egal, wichtig ist nur die Adresse. Die **ganze Adresse aus der Adresszeile kopieren**. Der Code gilt nur eine Stunde und nur einmal.
4. In GitHub: **Actions → Instagram verbinden → Run workflow**, die Adresse einfügen und starten.
5. Im Ergebnis steht: *„Verbunden mit @… Token gültig für 60 Tage …“*. Der Token liegt jetzt im Secret `IG_TOKEN`, ohne dass ihn jemand gesehen hat.
6. *Optional:* Das Secret `IG_APP_SECRET` jetzt löschen. Es wird nur gebraucht, falls Schritt 6 je wiederholt werden muss.

---

## Schritt 7 – Erster Lauf

1. **Actions → Wall aktualisieren → Run workflow**
2. Nach 1–2 Minuten die Wall-Adresse öffnen. Die Wall sollte erscheinen.
3. Ab jetzt aktualisiert sich die Wall **stündlich** und den Token verlängert GitHub **jeden Montag**.

---

## Schritt 8 – Auf lions.de einbinden

Das iframe aus **`embed/einbettung-lions-de.html`** im Redaktionssystem von lions.de als HTML-Element einfügen und `EURE-ORGANISATION` ersetzen:

```html
<iframe src="https://EURE-ORGANISATION.github.io/lions-social-wall/?modus=seiten"
        title="Instagram-Beiträge des Lions Club Kassel-Herkules"
        width="100%" height="1000" frameborder="0" scrolling="no" loading="lazy"></iframe>
```

- `?modus=seiten` sorgt dafür, dass die Wall genau in die Höhe passt und blättert.
- Bei `height="1000"` sind es auf dem Handy 4 Reihen à 2 und am PC 3 Reihen à 4. Jede andere Höhe funktioniert auch, die Wall rechnet selbst aus, wie viele Beiträge hineinpassen.

**Datenschutz:** Besucher laden die Wall von GitHub Pages. GitHub ist ein US-Anbieter, der dabei technisch bedingt die IP-Adresse der Besucher verarbeitet. Zu Instagram/Meta besteht erst Kontakt, wenn jemand auf „Auf Instagram ansehen“ tippt. Bitte die Datenschutzerklärung entsprechend ergänzen. Der Cookie-Banner von lions.de behandelt das iframe vermutlich als „Externe Inhalte“. Das ist keine Rechtsberatung.

**Hinweis:** Auf GitHub Pages lässt sich nicht technisch festlegen, dass nur lions.de die Wall einbetten darf. Da die Wall keine Eingaben oder Aktionen hat, ist das Missbrauchsrisiko praktisch null.

---

## Pflege

| Aufgabe | So geht's |
|---|---|
| Beitrag ausblenden | In `config/wall-config.json` den Link des Beitrags bei `"hidden"` eintragen, z. B. `["https://www.instagram.com/p/ABC123/"]`, und speichern (Commit). Die Wall aktualisiert sich sofort. |
| Anzahl der Beiträge | `"max_posts"` in `config/wall-config.json` (Standard 60) |
| Farben | oben in `wall/index.html` unter `:root` (Lions-Blau `#003087`) |
| Etwas klemmt | GitHub schickt bei Fehlern eine E-Mail. Die Wall zeigt so lange den letzten Stand. |
| Token abgelaufen (z. B. nach > 60 Tagen Ausfall) | Schritt 6 wiederholen (dafür `IG_APP_SECRET` ggf. neu anlegen) |
| Tresor-Schlüssel läuft ab | Schritt 3 wiederholen und `TRESOR_SCHLUESSEL` ersetzen |
| Ämterwechsel | neue Personen als Owner (GitHub) und Admin (Meta-App) eintragen, alte entfernen |
| **Notschalter** | Instagram → Einstellungen → **Apps und Websites → App entfernen**. Damit ist jeder Zugriff sofort weg. Zusätzlich das Secret `IG_TOKEN` löschen. |

---

## Inhalt des Pakets

```
wall/index.html                 Die Wall (läuft komplett ohne externe Dienste)
embed/einbettung-lions-de.html  iframe-Code für lions.de
config/wall-config.json         Anzahl und ausgeblendete Beiträge
scripts/fetch_feed.py           holt Beiträge, Likes, Aufrufe und Bilder
scripts/refresh_token.py        verlängert den Token
scripts/connect_instagram.py    Ersteinrichtung (Code → Token → Tresor)
.github/workflows/              die vier automatischen Abläufe
```
