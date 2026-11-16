#!/usr/bin/env python3
"""
Lions Social Wall – Abrufskript

Holt die neuesten Beiträge des Instagram-Kontos, lädt die Bilder herunter,
verkleinert sie und schreibt build/feed.json sowie build/media/*.jpg.

Der Instagram-Token kommt ausschließlich aus der Umgebungsvariable IG_TOKEN
(in GitHub: Secret IG_TOKEN). Er wird nie ausgegeben oder in Dateien geschrieben.
"""
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
MEDIA = BUILD / "media"
CONFIG_FILE = ROOT / "config" / "wall-config.json"

API_BASE = os.environ.get("IG_API_BASE", "https://graph.instagram.com").rstrip("/")
API_VERSION = os.environ.get("IG_API_VERSION", "v25.0")
TOKEN = os.environ.get("IG_TOKEN", "").strip()

SIZES = {"s": 540, "l": 1080}          # Kachel / Großansicht (Breite in Pixel)
JPEG_QUALITY = 82
MEDIA_FIELDS = ("id,media_type,media_product_type,media_url,thumbnail_url,permalink,"
                "timestamp,like_count,caption,children{id,media_type,media_url,thumbnail_url}")


def log(msg):
    print(msg, flush=True)


def scrub(text):
    """Entfernt den Token aus Fehlermeldungen, falls er darin auftaucht."""
    text = str(text)
    if TOKEN:
        text = text.replace(TOKEN, "***")
    return re.sub(r"access_token=[^&\s\"']+", "access_token=***", text)


def http_get(url, binary=False, attempts=3):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "lions-social-wall/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                return data if binary else json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")[:500]
            except Exception:
                pass
            last = RuntimeError(f"HTTP {e.code}: {scrub(body)}")
            if e.code < 500 and e.code != 429:
                break
        except Exception as e:  # Netzwerkfehler, Zeitüberschreitung
            last = RuntimeError(scrub(e))
        time.sleep(2 * (i + 1))
    raise last


def api(path, **params):
    params["access_token"] = TOKEN
    url = f"{API_BASE}/{API_VERSION}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"
    return http_get(url)


def load_config():
    cfg = {"max_posts": 60, "hidden": []}
    if CONFIG_FILE.exists():
        cfg.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    cfg["max_posts"] = max(1, min(200, int(cfg.get("max_posts", 60))))
    cfg["hidden"] = {str(h).strip().rstrip("/") for h in cfg.get("hidden", []) if str(h).strip()}
    return cfg


def is_hidden(item, hidden):
    if not hidden:
        return False
    link = (item.get("permalink") or "").rstrip("/")
    short = link.rsplit("/", 1)[-1] if link else ""
    return item.get("id") in hidden or link in hidden or short in hidden


def fetch_media_list(max_posts, hidden):
    items, url = [], None
    page = api("me/media", fields=MEDIA_FIELDS, limit=min(50, max_posts + len(hidden)))
    while True:
        for it in page.get("data", []):
            if not is_hidden(it, hidden):
                items.append(it)
            if len(items) >= max_posts:
                return items
        url = (page.get("paging") or {}).get("next")
        if not url:
            return items
        page = http_get(url)


def fetch_views(media_id):
    """Aufrufe über die Statistik-Schnittstelle. Gibt None zurück, wenn nicht verfügbar."""
    try:
        res = api(f"{media_id}/insights", metric="views")
    except Exception as e:
        log(f"  Hinweis: keine Aufrufe für {media_id} ({str(e)[:120]})")
        return None
    for m in res.get("data", []):
        if m.get("name") == "views":
            if "total_value" in m:
                return int(m["total_value"].get("value", 0))
            vals = m.get("values") or []
            if vals:
                return int(vals[0].get("value", 0))
    return None


def safe_name(media_id):
    return re.sub(r"[^0-9A-Za-z_-]", "", str(media_id))[:64] or "x"


def ensure_image(media_id, src_url):
    """Lädt ein Bild einmalig und erzeugt zwei Größen. Vorhandene Dateien werden wiederverwendet."""
    name = safe_name(media_id)
    out = {k: MEDIA / f"{name}_{k}.jpg" for k in SIZES}
    meta_file = MEDIA / f"{name}.json"
    if all(p.exists() for p in out.values()) and meta_file.exists():
        meta = json.loads(meta_file.read_text())
        return {"s": f"media/{out['s'].name}", "l": f"media/{out['l'].name}", "w": meta["w"], "h": meta["h"]}, out, meta_file
    if not src_url or not src_url.startswith("https://"):
        return None, {}, None
    raw = http_get(src_url, binary=True)
    with Image.open(io.BytesIO(raw)) as im:
        im = im.convert("RGB")
        w, h = im.size
        for key, width in SIZES.items():
            target = im if w <= width else im.resize((width, round(h * width / w)), Image.LANCZOS)
            target.save(out[key], "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        lw, lh = (w, h) if w <= SIZES["l"] else (SIZES["l"], round(h * SIZES["l"] / w))
    meta_file.write_text(json.dumps({"w": lw, "h": lh}))
    return {"s": f"media/{out['s'].name}", "l": f"media/{out['l'].name}", "w": lw, "h": lh}, out, meta_file


def alt_text(caption):
    """Kurzer Alternativtext für Screenreader (wird nicht sichtbar angezeigt)."""
    if not caption:
        return ""
    t = re.sub(r"#\w+", "", caption)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 160:
        t = t[:160].rsplit(" ", 1)[0] + " …"
    return t


def build_post(item, keep):
    mtype = item.get("media_type")
    if mtype == "CAROUSEL_ALBUM":
        ptype = "carousel"
        sources = [(c.get("id"), c.get("thumbnail_url") if c.get("media_type") == "VIDEO" else c.get("media_url"))
                   for c in (item.get("children") or {}).get("data", [])]
    elif mtype == "VIDEO":
        ptype = "reel"
        sources = [(item["id"], item.get("thumbnail_url"))]
    else:
        ptype = "image"
        sources = [(item["id"], item.get("media_url"))]

    images = []
    for mid, url in sources:
        try:
            info, files, meta = ensure_image(mid, url)
        except Exception as e:
            log(f"  Bild {mid} übersprungen: {scrub(e)[:160]}")
            continue
        if info:
            images.append(info)
            keep.update(str(p) for p in files.values())
            keep.add(str(meta))
    if not images:
        return None
    if ptype == "carousel" and len(images) == 1:
        ptype = "image"

    post = {
        "id": item["id"],
        "type": ptype,
        "permalink": item.get("permalink") or "https://www.instagram.com/",
        "date": item.get("timestamp"),
        "alt": alt_text(item.get("caption")),
        "images": images,
    }
    if isinstance(item.get("like_count"), int):
        post["likes"] = item["like_count"]
    views = fetch_views(item["id"])
    if views is not None:
        post["views"] = views
    return post


def main():
    if not TOKEN:
        log("Fehler: Der Instagram-Token fehlt (Secret IG_TOKEN).")
        return 2
    MEDIA.mkdir(parents=True, exist_ok=True)
    cfg = load_config()

    try:
        items = fetch_media_list(cfg["max_posts"], cfg["hidden"])
    except Exception as e:
        log(f"Fehler beim Abruf der Beiträge: {scrub(e)}")
        return 1
    log(f"{len(items)} Beiträge gefunden.")

    keep, posts = set(), []
    for it in items:
        p = build_post(it, keep)
        if p:
            posts.append(p)

    if not posts:
        log("Fehler: Keine darstellbaren Beiträge. Die bisherige Wall bleibt unverändert.")
        return 1

    # Nicht mehr benötigte Bilder entfernen
    removed = 0
    for f in MEDIA.iterdir():
        if str(f) not in keep:
            f.unlink()
            removed += 1

    feed = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "posts": posts}
    tmp = BUILD / "feed.json.tmp"
    tmp.write_text(json.dumps(feed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    tmp.replace(BUILD / "feed.json")
    log(f"Fertig: {len(posts)} Beiträge, {sum(len(p['images']) for p in posts)} Bilder, {removed} alte Dateien entfernt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
