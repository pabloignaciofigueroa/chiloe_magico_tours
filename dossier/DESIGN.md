# DESIGN.md · Dossier de decisiones de diseño (Bergerac)

Reglas visuales y de texto del dossier que acompaña una web regalo. Caso de referencia: **Turismo Chiloé Mágico** (oct 2026), generador en `dossier/build_dossier.py`.

El dossier es un **brochure que enamora**, no un informe de agencia. Lo lee la marca, no un diseñador.

---

## 1. Formato

- Láminas horizontales de **13 × 8,5 in**, en PDF para imprimir y HTML autocontenido de respaldo.
- **Unas 14 láminas.** Las secciones del sitio se agrupan; no va una lámina por sección.
- Peso objetivo: PDF ≤ 5 MB.

## 2. Estructura base (14 láminas)

| # | Lámina | Composición |
|---|---|---|
| 01 | Portada | Foto icónica a doble página completa. Solo el logo (ver §4). |
| 02 | Carta | Foto con esquinas redondeadas a la izquierda. A la derecha, la carta en texto grande y el sello rojo debajo (ver §6). |
| 03 | De dónde viene todo | Fotos suyas como polaroids desordenadas, más 4 cifras gigantes (posts, reseñas, piezas gráficas, fotos). |
| 04 | La marca | Un título de su propia pieza en tamaño cartel, más la paleta en franjas verticales a sangre. Tres bloques: letra, color y la regla del color de acción. |
| 05 | Recorrido | El sitio en 4 actos (llegar, elegir, confiar, reservar), con capturas inclinadas y medallones numerados. |
| 06–12 | Secciones agrupadas | Portada del sitio, el «momento» memorable, la oferta, la ficha, las personas, otras formas de buscar y el cierre o contacto. |
| 13 | Detalles | Cinco celulares sobre círculos de color y cuatro bloques cortos. |
| 14 | Cierre | Foto a sangre y una tarjeta clara con «Hacerlo suyo», los próximos pasos y la firma Bergerac. |

## 3. Composición: nada de plantilla

- **Prohibida la fórmula fija** (oscuro a la izquierda y ficha a la derecha en cada lámina). Es el error que se cometió con Floresta y con la primera versión de Chiloé Mágico.
- **Cada lámina tiene su propio fondo**, con los colores de la marca alternados: claro, rojo, verde, azul, oscuro, gris claro…
- **Se usa la gramática gráfica de la marca:**
  - medallones circulares (las paradas rotuladas de sus afiches);
  - banda de color;
  - el ícono de su pie (la gaviota);
  - polaroids;
  - cápsulas de color con nombres o datos.
- **Capturas dentro de marcos:**
  - navegador con esquinas redondeadas y sombra;
  - celular con borde negro;
  - levemente inclinados (−3° a +3°) y superpuestos.
- **Fotos a sangre** cuando la imagen manda: portada, el «momento» del sitio y el cierre.
- **Tarjetas flotantes** claras, con esquinas redondeadas y sombra, para el texto sobre una foto.
- **Más imagen que texto:** cada lámina tiene a lo sumo un título, uno o dos párrafos cortos, una cita y una cifra.
- **Revisar los adornos que contrastan mal.** Por ejemplo, la ola azul sobre fondo claro se eliminó porque se veía como un arco feo. Las olas, solo en tono sobre tono.

## 4. Portada

- **Foto:** la foto icónica ocupa la doble página completa.
- **Logo:** siempre **arriba a la izquierda**.
  - Va sobre una **masa blanca rectangular** que sale por el borde izquierdo, con esquinas redondeadas solo a la derecha.
  - Lleva aire suficiente a la derecha del logo.
  - Logo y masa van al **75 % de opacidad**.
  - Tamaño: logo de unas 1,9 in de ancho.
- **Nada más:** sin título, sin fecha, sin coordenadas, sin otras masas.

## 5. Tipografía

- **Títulos y medallones:** solo en la letra display de la marca (en Chiloé Mágico, Anton), en mayúsculas.
- **Palabra de enlace** («con», «ya», «y»): en la misma letra y tamaño que el título, distinguida solo por el color. **Nunca una sans pequeña entre títulos.**
- **Texto corrido:** en la letra de texto de la marca (en Chiloé Mágico, Montserrat).
  - Párrafos de 9,5 a 10,5 pt.
  - La carta, en unos 13 pt.
- **Rótulos pequeños (kicker):** en mayúsculas espaciadas, en un color de acento.

## 6. Sello de la carta

- Sello de certificación en el rojo de la marca, de unas 2,2 in, girado unos −8°.
- Lleva doble anillo blanco y texto circular: «PARA [MARCA] ★ HECHO EN CASTRO ★ [MES AÑO] ★».
- Al centro, «UN REGALO» en letra display grande.
- Va a la derecha, centrado bajo el texto de la carta.

## 7. Texto

- **Las decisiones vienen del origen, no de la construcción.** Cada decisión parte de algo de la marca o de sus clientes:
  - «Viene de sus afiches…»
  - «Su logo ya tenía la isla…»
  - ««Escríbenos», dice su bio…»
  - «Sus viajeros hablan, sobre todo, de las personas…»
- **Se evita:**
  - «lo que hicimos», «decidimos», «se calculó», «se aligeraron»;
  - «el único momento de efecto»;
  - cualquier frase que ponga al estudio como protagonista.
- **Excepción:** la frase de cierre de la carta («Ojalá lo disfruten tanto como nosotros disfrutamos haciéndolo»).
- **Sin repeticiones entre láminas:**
  - ningún título ni rótulo se repite;
  - el título de una lámina no repite el texto que ya muestra su captura;
  - antes de entregar se hace un barrido automático de frases de 4 palabras repetidas, que debe dar 0.
- **Se habla de «ustedes».**
  - Sin tecnicismos (ver la tabla de reemplazos de la skill).
  - Sin superlativos.
  - Toda cifra sale de los archivos.
  - Las citas van literales y con su fuente.
- **Lo no publicado se dice:** «por confirmar con la agencia».

## 8. Control antes de entregar

1. **Desbordes:** ningún bloque de texto se sale de la lámina.
2. **Revisión visual:** mirar cada lámina renderizada, buscando choques, superposiciones con texto y capturas a medio cargar.
3. **Cotejo independiente:** un agente que no escribió el dossier revisa citas, fechas, cifras y nombres contra las fuentes.
4. **Repeticiones:** el barrido de 4-gramas debe dar 0.
