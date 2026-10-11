# Bitácora de Molienda

App web instalable (PWA) para registrar la molienda diaria de pimienta en el celular
y pasar los datos al sistema de Trazabilidad / SISTEMA FENOLIC.

- `src/app.html` — código de la app (HTML + CSS + JS en un solo archivo).
- `build.py` — genera la versión instalable en `docs/` (requiere Python + Pillow).
- `docs/` — lo que publica GitHub Pages (rama main, carpeta /docs).

Para actualizar: edita `src/app.html`, corre `python build.py`, haz commit y push.

Los registros se guardan en el celular (localStorage). Respaldo desde Ajustes.
Cada registro tiene un `id` estable para sincronizarlo después con SISTEMA FENOLIC.
