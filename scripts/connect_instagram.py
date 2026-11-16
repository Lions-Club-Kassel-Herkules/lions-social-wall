#!/usr/bin/env python3
"""
Ersteinrichtung: tauscht den einmaligen Code aus dem Instagram-Login gegen einen
60-Tage-Token. Der Token wird NUR in die übergebene Datei geschrieben (Rechte 600)
und vom Workflow direkt in den GitHub-Tresor (Secret IG_TOKEN) übertragen.
Niemand bekommt ihn zu sehen.

Benötigte Umgebungsvariablen: IG_APP_ID, IG_APP_SECRET, IG_REDIRECT_URI, IG_CODE
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

OAUTH_BASE = os.environ.get("IG_OAUTH_BASE", "https://api.instagram.com").rstrip("/")
API_BASE = os.environ.get("IG_API_BASE", "https://graph.instagram.com").rstrip("/")
WRITE_PERMISSIONS = {"instagram_business_content_publish", "instagram_business_manage_messages",
                     "instagram_business_manage_comments"}


def request(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={"User-Agent": "lions-social-wall/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    env = {k: os.environ.get(k, "").strip() for k in ("IG_APP_ID", "IG_APP_SECRET", "IG_REDIRECT_URI", "IG_CODE")}
    missing = [k for k, v in env.items() if not v]
    if missing or len(sys.argv) != 2:
        print("Fehler: Es fehlt " + ", ".join(missing or ["die Zieldatei"]) + ". Siehe Anleitung, Schritt 6.")
        return 2
    code = env["IG_CODE"]
    if code.endswith("#_"):
        code = code[:-2]
    if "code=" in code:                       # ganze Adresse eingefügt? Code herauslösen
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get("code", [""])[0].rstrip("#_")
    for s in (env["IG_APP_SECRET"], env["IG_CODE"], code):
        print(f"::add-mask::{s}")

    def clean(text):
        text = str(text)
        for s in (env["IG_APP_SECRET"], env["IG_CODE"], code):
            text = text.replace(s, "***")
        return text

    try:
        short = request(f"{OAUTH_BASE}/oauth/access_token", {
            "client_id": env["IG_APP_ID"], "client_secret": env["IG_APP_SECRET"],
            "grant_type": "authorization_code", "redirect_uri": env["IG_REDIRECT_URI"], "code": code})
        if isinstance(short.get("data"), list) and short["data"]:
            short = short["data"][0]
        short_token = short["access_token"]
        print(f"::add-mask::{short_token}")
        perms = short.get("permissions") or []
        if isinstance(perms, str):
            perms = [p.strip() for p in perms.split(",")]
        print("Erteilte Berechtigungen:", ", ".join(perms) or "(keine Angabe)")
        extra = WRITE_PERMISSIONS.intersection(perms)
        if extra:
            print("Fehler: Der Login hat Schreibrechte erteilt (" + ", ".join(sorted(extra)) + "). "
                  "Bitte den Link aus der Anleitung mit genau zwei Berechtigungen verwenden.")
            return 1

        long = request(f"{API_BASE}/access_token?" + urllib.parse.urlencode({
            "grant_type": "ig_exchange_token", "client_secret": env["IG_APP_SECRET"], "access_token": short_token}))
        token = long["access_token"]
        print(f"::add-mask::{token}")

        me = request(f"{API_BASE}/me?" + urllib.parse.urlencode({"fields": "username,account_type", "access_token": token}))
    except urllib.error.HTTPError as e:
        print(f"Fehler (HTTP {e.code}): {clean(e.read().decode('utf-8', 'replace')[:300])}")
        print("Häufige Ursachen: Code älter als 1 Stunde oder schon benutzt, Weiterleitungsadresse weicht ab.")
        return 1
    except Exception as e:
        print(f"Fehler: {clean(e)}")
        return 1

    fd = os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(token)
    days = int(long.get("expires_in", 0)) // 86400
    print(f"Verbunden mit @{me.get('username')} ({me.get('account_type')}). Token gültig für {days} Tage "
          "und wird ab jetzt jeden Montag automatisch verlängert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
