# Brief para el equipo generador del banco SABI PREICFES CENTEC
Equipo simulado: docente experto ICFES del área + pedagogo especialista en DBA + Dot Auditor (verificador).

1. Lee COMPLETO /home/claude/icfes-sabicentec/tools/ESPECIFICACION_ITEMS.md y mira el formato en
   /home/claude/icfes-sabicentec/tools/ejemplos.json (no copies su contenido).
2. (Opcional, una vez) Para calibrar la FORMA real del ICFES puedes renderizar 1–2 páginas de tu área de los cuadernillos oficiales
   (pdftoppm -r 60 -png -f N -l N <pdf> /tmp/claude-0/x) y verlas con Read. NO copies ítems:
   /root/.claude/uploads/fa023b76-ba4d-5267-bfa1-a73d765078b7/df908c77-1_SESIO_N_ejemplo2_14042024.pdf (sesión 1: Matemáticas, Lectura, Sociales, Ciencias)
   /root/.claude/uploads/fa023b76-ba4d-5267-bfa1-a73d765078b7/e5dbd2fd-2_SESIO_N_ejemplo1_14042024.pdf (sesión 2: Matemáticas, Sociales, Ciencias, Inglés)
   /root/.claude/uploads/fa023b76-ba4d-5267-bfa1-a73d765078b7/5a1d7fec-P3_S2_CA.pdf (Saber 11 2025, sesión 2)
3. Genera tus ítems en lotes de 10 ítems. Cada lote es un archivo JSON (arreglo) llamado <BASE>.parteN.json en
   /home/claude/icfes-sabicentec/banco_raw/ (escríbelo con la herramienta Write; JSON válido, comillas dobles, sin comentarios).
4. Antes de escribir cada ítem: resuélvelo tú mismo y resuelve su gemela. En matemáticas y ciencias comprueba TODA cifra con python3.
   Si una opción incorrecta también podría defenderse, cámbiala. Cada distractor debe nacer de un error real y su campo `errores` debe explicarlo.
5. Tras cada lote corre: python3 /home/claude/icfes-sabicentec/tools/validar_banco.py <archivo> y corrige hasta 0 errores.
6. Al final une las partes en orden:
   python3 /home/claude/icfes-sabicentec/tools/unir.py /home/claude/icfes-sabicentec/banco_raw/<BASE>.json /home/claude/icfes-sabicentec/banco_raw/<BASE>.parte1.json ...
   y valida el archivo final (0 errores; claves A/B/C/D equilibradas; competencias repartidas; niveles según §4.7).
7. ids consecutivos con el prefijo asignado: <PREFIJO>001, <PREFIJO>002, …
8. Variedad: no repitas la misma situación ni la misma estructura de enunciado; usa tabla/grafica/figura donde el ICFES lo haría
   (al menos 25 % de los ítems de matemáticas, ciencias y sociales llevan tabla, gráfica o figura).
9. Respuesta final: UNA sola línea: "OK <BASE>.json <n> ítems" (o "FALLO <motivo>"). No resumas el contenido.
