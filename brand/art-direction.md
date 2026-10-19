# Dirección de arte (fase 8)

**Idea:** la web como uno de sus afiches de tour, pero con aire. Fondo niebla, títulos Anton en mayúsculas con una palabra en cursiva Sacramento de enlace ("TOUR LA COSTA *con* CURANTO EN HOYO"), medallones circulares con rótulo curvo (su gramática de afiche [DEST-H7]) y la banda roja con la gaviota al pie.

## Ritmo de la home
```
[ HERO 100svh  foto columpio Huillinco + logo adhesivo + "Nuestro archipiélago es mágico"      ]
[ barra de confianza: 4,9★ Google · 46 reseñas · Tours todos los días · máx. 16 por van          ]
[ ★ MOMENTO: la isla de su logo como ventana → video Puñihuil; al bajar, la isla crece hasta
  cubrir la pantalla (sección 220vh, hijo sticky 100svh; sin pin)                                  ]
[ TOURS destacados: 7 tarjetas tipo afiche (slider con swipe)                                      ]
[ EXPLORA POR DESTINO: 5 medallones con rótulo curvo                                               ]
[ EXPLORA POR EXPERIENCIA: 5 bandas tipográficas con imagen al pasar                               ]
[ PAQUETES varios días (2) + arma tu viaje                                                         ]
[ POR QUÉ NOSOTROS: vans (video), 16 pasajeros, guía propio, salida Plaza de Armas                 ]
[ TESTIMONIOS carrusel internacional                                                               ]
[ GUÍA DE CHILOÉ: 3 artículos                                                                      ]
[ SERVICIOS / CONTACTO + mapa                                                                      ]
[ PIE banda roja con gaviota                                                                        ]
```
## Movimiento
- Curva única `cubic-bezier(.16,1,.3,1)` (expo-out). Revelados de línea con máscara (`.line > span` translateY 105% → 0), parallax de medios con `inset` negativo (-8%), masas a distinta velocidad en las tarjetas.
- Lenis para el scroll suave; nunca `pin`. Sticky con `overflow: clip` en ancestros.
- `prefers-reduced-motion`: todo visible, sin parallax, la isla queda abierta, el carrusel con scroll nativo.
## Un solo momento memorable
La silueta de Chiloé del logo (trazada) como `mask-image` sobre el video de Puñihuil. Escala 0,55 → 9 al recorrer la sección; el título "¡NO DEJES QUE TE LO CUENTEN!" se abre por detrás.
