# Especificación de ítems — SABI PREICFES CENTEC (9°, 10° y 11°)

Todo ítem replica la FORMA del ICFES (marco de referencia y guías de orientación Saber 11):
contexto auténtico → enunciado que pregunta UNA cosa → 4 opciones (A–D) con UNA sola correcta
y tres distractores plausibles construidos a partir de errores reales del estudiante.

La filosofía CENTEC "El error no nos detiene, nos enseña, nos fortalece y nos hace crecer"
se materializa en el campo `errores`: cada distractor explica qué pensó el estudiante,
por qué falla, una pregunta guía socrática y la idea que debe aprender. Luego una `gemela`
(misma habilidad, otros datos) permite comprobar que aprendió.

## 1. Campos obligatorios

| campo | tipo | regla |
|---|---|---|
| id | string | prefijo asignado + consecutivo de 3 dígitos (P11-MAT-A001) |
| area | enum | matematicas · lectura · sociales · ciencias · ingles |
| grado | int | 9, 10 u 11 |
| prueba | string | "Saber 11 · Matemáticas", "Saber 11 · Lectura Crítica", "Saber 11 · Sociales y Ciudadanas", "Saber 11 · Ciencias Naturales", "Saber 11 · Inglés" |
| competencia | enum | ver §2 (texto EXACTO) |
| componente | enum | ver §2 (texto EXACTO) |
| nivel | int | 1, 2, 3 o 4 = nivel de desempeño ICFES que discrimina el ítem (1 bajo … 4 avanzado) |
| dba | string | "DBA (v.2) <Área> <grado>°: …" parafraseando el DBA del MEN del grado (para Inglés: "Currículo sugerido de Inglés MEN <grado>°: …") |
| lineamiento | string | Lineamiento curricular y/o Estándar Básico de Competencias (EBC) del grupo de grados correspondiente |
| afirmacion | string | afirmación del marco ICFES (qué sabe hacer el estudiante) |
| evidencia | string | evidencia observable que el ítem recoge |
| enunciado | string | la pregunta; termina en "?" o en ":" |
| opciones | objeto | {"A","B","C","D"} textos de longitud y estructura gramatical parecidas |
| correcta | "A"–"D" | — |
| errores | objeto | una entrada por CADA opción incorrecta (exactamente 3) con: `error` (nombre corto del error), `porque` (empieza "Elegiste X porque probablemente …"), `pregunta_guia` (pregunta socrática), `aprende` (idea clave correcta) |
| explicacion | string | resolución paso a paso ("Paso 1: … Paso 2: …") que justifica la correcta y descarta las demás |
| estrategia_icfes | string | cómo pregunta el ICFES esta habilidad y qué proceso seguir para resolver ítems de este tipo |
| tip | string | consejo breve de lectura/estrategia |
| truco | string | regla mnemotécnica o atajo válido |
| temas | string[] | 2–4 etiquetas de temas |
| gemela | objeto | {enunciado, opciones{A–D}, correcta, explicacion} y opcional `contexto`; mide la MISMA evidencia con datos/situación distintos; su clave debe ser distinta de la clave del ítem principal cuando sea posible |

## 2. Taxonomía oficial (usar el texto exacto)

**Matemáticas** — competencias: `Interpretación y representación` · `Formulación y ejecución` · `Argumentación`.
Componentes: `Estadística` · `Geometría` · `Álgebra y cálculo`. Campo extra obligatorio `contenido`: `genérico` (conocimiento que todo ciudadano usa) o `no genérico`.

**Lectura Crítica** — competencias: `Identificar y entender contenidos locales` · `Comprender cómo se articulan las partes de un texto` · `Reflexionar a partir de un texto y evaluar su contenido`.
Componentes (tipo de texto): `Continuo literario` · `Continuo informativo filosófico` · `Continuo informativo no filosófico` · `Discontinuo`.

**Sociales y Ciudadanas** — competencias: `Pensamiento social` · `Interpretación y análisis de perspectivas` · `Pensamiento reflexivo y sistémico`.
Componentes: `Relaciones histórico-culturales` · `Relaciones espacio-ambientales` · `Relaciones ético-políticas` · `Conocimientos ciudadanos (Constitución)`.

**Ciencias Naturales** — competencias: `Uso comprensivo del conocimiento científico` · `Explicación de fenómenos` · `Indagación`.
Componentes: `Biológico` · `Químico` · `Físico` · `Ciencia, tecnología y sociedad`.

**Inglés** — competencias: `Lingüística` · `Pragmática` · `Sociolingüística`.
Componente = parte de la prueba (campo extra obligatorio `parte`, entero 1–7):
1 `Parte 1 · Avisos` (¿dónde se ve el aviso?), 2 `Parte 2 · Vocabulario` (relacionar descripción-palabra),
3 `Parte 3 · Conversaciones` (respuesta adecuada en un diálogo), 4 `Parte 4 · Gramática en texto` (cloze),
5 `Parte 5 · Comprensión literal`, 6 `Parte 6 · Comprensión inferencial`, 7 `Parte 7 · Gramática y léxico en texto`.
Campo extra obligatorio `mcer`: `A-` · `A1` · `A2` · `B1` · `B+`. Contexto, enunciado y opciones en inglés; `errores`, `explicacion`, `tip`, `truco`, `estrategia_icfes` en español (pueden citar palabras en inglés).

## 3. Campos opcionales (recursos visuales — el ICFES usa tablas, gráficas y figuras)

- `contexto`: situación o texto base. En Lectura Crítica es obligatorio (texto de 120–350 palabras, ORIGINAL, de autoría propia; se puede declarar "Adaptado de una idea de …" solo si es dominio público).
- `grupo`: string compartido cuando varios ítems usan el mismo contexto (copia el contexto completo en cada ítem).
- `tabla`: {"titulo": str, "columnas": [str…], "filas": [[celda…]…]} (todas las filas con igual número de celdas que columnas).
- `grafica`: {"tipo": "barras"|"lineas"|"puntos"|"torta", "titulo": str, "ejeX": str, "ejeY": str, "series": [{"nombre": str, "datos": [[x, y], …]}]} (x puede ser texto o número; y numérico; en torta usar una serie con [etiqueta, valor]).
- `figura`: SVG en línea pequeño (< 4 KB), con viewBox, sin <script>, sin atributos on*, sin imágenes externas; trazos `currentColor` o colores sobrios; etiquetas legibles. Úsalo para geometría, plano cartesiano, circuitos, montajes de laboratorio, mapas esquemáticos.

## 4. Reglas de calidad (Dot Auditor)

1. Una sola respuesta defendible. Si un distractor también podría defenderse, se reescribe.
2. Todo cálculo se verifica (python3). Unidades y cifras coherentes. Moneda en pesos colombianos ($1.200 con punto de miles).
3. Distractores = errores típicos reales (no absurdos). Longitudes de opciones parecidas; nada de "todas las anteriores".
4. Contextos colombianos y del Valle del Cauca/Cali cuando aplique (barrios, Pacífico, caña, salsa, ríos Cauca/Pance, economía familiar, emprendimiento). En 15–20 % de los ítems de matemáticas y sociales, contextos de educación financiera (Modelo Sabic): ahorro, interés simple/compuesto, presupuesto, crédito, inflación.
5. Sin sesgos, sin estereotipos, lenguaje respetuoso; nombres diversos.
6. Equilibrio de claves: ninguna letra > 35 % en un archivo.
7. Distribución de niveles por archivo aprox.: nivel 1: 20 %, 2: 35 %, 3: 30 %, 4: 15 % (en 9° desplazar hacia 1–2, en 11° hacia 2–3).
8. Repartir las competencias del área de forma equilibrada.
9. No copiar ítems reales del ICFES ni textos con derechos de autor; crear originales con la misma forma.
10. Español colombiano correcto, tildes y signos de apertura (¿ ¡).

## 5. Progresión por grado
- 11°: nivel de la prueba Saber 11 real.
- 10°: misma forma Saber 11, contenidos de los DBA de 10° (funciones, trigonometría, química inorgánica, cinemática, filosofía/argumentación, Constitución, etc.).
- 9°: misma forma Saber 11, contenidos y DBA de 9° (álgebra, sistemas, semejanza, probabilidad básica, genética, enlaces, ondas, textos argumentativos, historia de Colombia s. XIX–XX), lenguaje un poco más accesible.
