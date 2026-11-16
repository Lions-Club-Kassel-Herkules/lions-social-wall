#!/usr/bin/env python3
"""
Verlängert den Instagram-Token um weitere 60 Tage.

Der neue Token wird NUR in die als Argument übergebene Datei geschrieben
(Rechte 600) und sofort für die GitHub-Protokolle maskiert.
Aufruf: python3 scripts/refresh_token.py /pfad/zur/datei
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = os.environ.get("IG_API_BASE", "https://graph.instagram.com").rstrip("/")


def main():
    token = os.environ.get("IG_TOKEN", "").strip()
    if not token or len(sys.argv) != 2:
        print("Fehler: IG_TOKEN fehlt oder Zieldatei nicht angegeben.")
        return 2
    print(f"::add-mask::{token}")
    url = f"{API_BASE}/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": token})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300].replace(token, "***")
        print(f"Fehler beim Erneuern (HTTP {e.code}): {body}")
        return 1
    except Exception as e:
        print(f"Fehler beim Erneuern: {str(e).replace(token, '***')}")
        return 1

    new = (data.get("access_token") or "").strip()
    if not new:
        print("Fehler: Instagram hat keinen neuen Token geliefert.")
        return 1
    print(f"::add-mask::{new}")
    fd = os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(new)
    days = int(data.get("expires_in", 0)) // 86400
    print(f"Token erneuert. Gültig für weitere {days} Tage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
