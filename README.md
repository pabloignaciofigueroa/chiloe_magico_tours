# Turismo Chiloé Mágico · web

Sitio de **Turismo Chiloé Mágico** (Castro, Chiloé): tours de día completo por el archipiélago.

**En línea:** https://chiloemagicotour.pages.dev

Hecho solo con el material público de la agencia: sus publicaciones y destacadas de Instagram (@chiloemagicotour), sus afiches de tours y las reseñas de Google. Cada texto lleva su fuente en `content/copy.md`.

## Estructura
- **Home** (`/`) y catálogo de 4 niveles: `/tours/` + 8 fichas, `/destinos/` + 5, `/experiencias/` + 5, `/paquetes/`, `/servicios/`, `/nosotros/`, `/guia/` + 5 artículos, `/preguntas-frecuentes/`, `/contacto/`.
- Español por defecto; botón ES · EN para la interfaz. Los textos de la marca y las reseñas quedan en su idioma original.

## Editar
1. Textos y datos: `content/site.py` (cada texto con su fuente). Imágenes: `content/media.json` + `tools/alt-en.json`.
2. Plantilla común: `src/layout.html`. Estilos: `css/main.css`. Interacción: `js/main.js`.
3. Regenerar y publicar:
   ```
   python3 tools/media.py     # solo si cambian fotos o videos
   python3 tools/build.py     # genera las páginas
   python3 tools/publish.py   # arma public/, lo único que se publica
   git push origin main
   ```
Cloudflare Pages publica la carpeta `public/` de la rama `main` (sin build).
