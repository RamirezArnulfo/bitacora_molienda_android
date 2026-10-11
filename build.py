"""Builds the installable PWA into docs/ (GitHub Pages) from src/app.html."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
DIST = ROOT / "docs"
DIST.mkdir(exist_ok=True)
VERSION = "1"

app = (ROOT / "src" / "app.html").read_text(encoding="utf-8")
title_end = app.index("</title>") + len("</title>")
head_extra, body = app[:title_end], app[title_end:]
style_start, style_end = body.index("<link rel=\"preconnect\""), body.index("</style>") + len("</style>")
head_assets, body = body[style_start:style_end], body[:style_start] + body[style_end:]

index = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#18201a">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
{head_extra}
{head_assets}
<style>:root{{padding-top:env(safe-area-inset-top,0px)}} body{{margin:0}} [hidden]{{display:none!important}}</style>
</head>
<body>
{body.strip()}
<script>
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(function () {{}});
</script>
</body>
</html>
"""
(DIST / "index.html").write_text(index, encoding="utf-8")

manifest = {
    "name": "Bitácora de Molienda",
    "short_name": "Molienda",
    "lang": "es",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#eef0ec",
    "theme_color": "#18201a",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
(DIST / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

sw = f"""const CACHE = "molienda-v{VERSION}";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png"];
self.addEventListener("install", e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); }});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
}});
self.addEventListener("fetch", e => {{
  if (e.request.method !== "GET") return;
  // Red primero (para recibir actualizaciones); sin internet usa la copia guardada.
  e.respondWith(
    fetch(e.request).then(res => {{
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {{}});
      return res;
    }}).catch(() => caches.match(e.request).then(hit => hit || caches.match("index.html")))
  );
}});
"""
(DIST / "sw.js").write_text(sw, encoding="utf-8")


def icon(size, maskable=False):
    s = 4  # supersample
    W = size * s
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = (24, 32, 26, 255)
    if maskable:
        d.rectangle([0, 0, W, W], fill=bg)
        scale = 0.62
    else:
        d.rounded_rectangle([0, 0, W - 1, W - 1], radius=int(W * 0.22), fill=bg)
        scale = 0.8
    c, R = W / 2, W * scale / 2
    # three peppercorns
    for dx, dy, r, col in [(-0.38, 0.22, 0.42, (143, 194, 136, 255)), (0.36, 0.26, 0.38, (228, 238, 224, 255)), (0.0, -0.36, 0.44, (47, 93, 58, 255))]:
        x, y, rr = c + dx * R, c + dy * R, r * R
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col, outline=bg, width=int(W * 0.02))
        hr = rr * 0.22
        d.ellipse([x - rr * 0.35 - hr, y - rr * 0.35 - hr, x - rr * 0.35 + hr, y - rr * 0.35 + hr], fill=(255, 255, 255, 70))
    return img.resize((size, size), Image.LANCZOS)


icon(192).save(DIST / "icon-192.png")
icon(512).save(DIST / "icon-512.png")
icon(512, maskable=True).save(DIST / "icon-maskable-512.png")
print("ok", sorted(p.name for p in DIST.iterdir()))
