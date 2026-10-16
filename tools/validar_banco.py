#!/usr/bin/env python3
"""Validador estructural del banco SABI PREICFES. Uso: python3 validar_banco.py archivo.json [...]"""
import json, re, sys
from collections import Counter

AREAS = {
    "matematicas": ("Saber 11 · Matemáticas",
        {"Interpretación y representación", "Formulación y ejecución", "Argumentación"},
        {"Estadística", "Geometría", "Álgebra y cálculo"}),
    "lectura": ("Saber 11 · Lectura Crítica",
        {"Identificar y entender contenidos locales", "Comprender cómo se articulan las partes de un texto",
         "Reflexionar a partir de un texto y evaluar su contenido"},
        {"Continuo literario", "Continuo informativo filosófico", "Continuo informativo no filosófico", "Discontinuo"}),
    "sociales": ("Saber 11 · Sociales y Ciudadanas",
        {"Pensamiento social", "Interpretación y análisis de perspectivas", "Pensamiento reflexivo y sistémico"},
        {"Relaciones histórico-culturales", "Relaciones espacio-ambientales", "Relaciones ético-políticas",
         "Conocimientos ciudadanos (Constitución)"}),
    "ciencias": ("Saber 11 · Ciencias Naturales",
        {"Uso comprensivo del conocimiento científico", "Explicación de fenómenos", "Indagación"},
        {"Biológico", "Químico", "Físico", "Ciencia, tecnología y sociedad"}),
    "ingles": ("Saber 11 · Inglés",
        {"Lingüística", "Pragmática", "Sociolingüística"},
        {"Parte 1 · Avisos", "Parte 2 · Vocabulario", "Parte 3 · Conversaciones", "Parte 4 · Gramática en texto",
         "Parte 5 · Comprensión literal", "Parte 6 · Comprensión inferencial", "Parte 7 · Gramática y léxico en texto"}),
}
REQ = ["id", "area", "grado", "prueba", "competencia", "componente", "nivel", "dba", "lineamiento", "afirmacion",
       "evidencia", "enunciado", "opciones", "correcta", "errores", "explicacion", "estrategia_icfes", "tip",
       "truco", "temas", "gemela"]
L = ["A", "B", "C", "D"]
BAD_SVG = re.compile(r"<script|\son\w+\s*=|href\s*=\s*['\"]?(http|//|javascript)|<image|<foreignObject", re.I)


def s(x):
    return isinstance(x, str) and x.strip() != ""


def opts_ok(o):
    return isinstance(o, dict) and sorted(o) == L and all(s(o[k]) for k in L)


def validate(data, fname="?"):
    E, W = [], []
    if not isinstance(data, list):
        return [f"{fname}: el archivo debe ser un arreglo JSON"], W
    ids, keys, niv = Counter(), Counter(), Counter()
    for n, q in enumerate(data):
        w = f"{fname}#{n} {q.get('id', '?') if isinstance(q, dict) else '?'}"
        if not isinstance(q, dict):
            E.append(f"{w}: no es objeto"); continue
        for k in REQ:
            if k not in q:
                E.append(f"{w}: falta '{k}'")
        ids[q.get("id")] += 1
        a = q.get("area")
        if a not in AREAS:
            E.append(f"{w}: area inválida '{a}'"); continue
        prueba, comps, compos = AREAS[a]
        if q.get("prueba") != prueba: E.append(f"{w}: prueba debe ser '{prueba}'")
        if q.get("grado") not in (9, 10, 11): E.append(f"{w}: grado inválido")
        if q.get("competencia") not in comps: E.append(f"{w}: competencia no oficial '{q.get('competencia')}'")
        if q.get("componente") not in compos: E.append(f"{w}: componente no oficial '{q.get('componente')}'")
        if q.get("nivel") not in (1, 2, 3, 4): E.append(f"{w}: nivel inválido (1–4)")
        niv[q.get("nivel")] += 1
        if a == "matematicas" and q.get("contenido") not in ("genérico", "no genérico"):
            E.append(f"{w}: contenido debe ser 'genérico' o 'no genérico'")
        if a == "ingles":
            if q.get("mcer") not in ("A-", "A1", "A2", "B1", "B+"): E.append(f"{w}: mcer inválido")
            if q.get("parte") not in range(1, 8): E.append(f"{w}: parte inválida (1–7)")
            elif not str(q.get("componente", "")).startswith(f"Parte {q['parte']} "):
                E.append(f"{w}: parte y componente no coinciden")
        if a == "lectura" and not s(q.get("contexto")): E.append(f"{w}: lectura exige contexto")
        for k in ["dba", "lineamiento", "afirmacion", "evidencia", "enunciado", "explicacion", "estrategia_icfes", "tip", "truco"]:
            if k in q and not s(q[k]): E.append(f"{w}: '{k}' vacío")
        if s(q.get("dba")) and not re.match(r"^(DBA|Currículo sugerido)", q["dba"]):
            E.append(f"{w}: dba debe iniciar con 'DBA' o 'Currículo sugerido'")
        if not opts_ok(q.get("opciones")): E.append(f"{w}: opciones deben ser A–D no vacías")
        c = q.get("correcta")
        if c not in L: E.append(f"{w}: correcta inválida"); continue
        keys[c] += 1
        if opts_ok(q.get("opciones")):
            vals = [q["opciones"][k].strip().lower() for k in L]
            if len(set(vals)) < 4: E.append(f"{w}: opciones repetidas")
        er = q.get("errores")
        if not isinstance(er, dict) or sorted(er) != sorted(x for x in L if x != c):
            E.append(f"{w}: errores debe tener exactamente las 3 opciones incorrectas")
        else:
            for k, v in er.items():
                if not isinstance(v, dict) or not all(s(v.get(f)) for f in ("error", "porque", "pregunta_guia", "aprende")):
                    E.append(f"{w}: errores.{k} incompleto")
                elif not v["porque"].startswith(f"Elegiste {k}") and not v["porque"].startswith("Elegiste"):
                    W.append(f"{w}: errores.{k}.porque no inicia con 'Elegiste'")
        if not (isinstance(q.get("temas"), list) and 1 <= len(q["temas"]) <= 6 and all(s(t) for t in q["temas"])):
            E.append(f"{w}: temas debe ser lista de 1–6 strings")
        g = q.get("gemela")
        if not isinstance(g, dict) or not s(g.get("enunciado")) or not opts_ok(g.get("opciones")) \
                or g.get("correcta") not in L or not s(g.get("explicacion")):
            E.append(f"{w}: gemela incompleta")
        elif g.get("enunciado", "").strip() == q.get("enunciado", "").strip():
            E.append(f"{w}: gemela idéntica al ítem")
        t = q.get("tabla")
        if t is not None:
            if not (isinstance(t, dict) and isinstance(t.get("columnas"), list) and isinstance(t.get("filas"), list)
                    and t["filas"] and all(isinstance(r, list) and len(r) == len(t["columnas"]) for r in t["filas"])):
                E.append(f"{w}: tabla mal formada")
        gr = q.get("grafica")
        if gr is not None:
            ok = isinstance(gr, dict) and gr.get("tipo") in ("barras", "lineas", "puntos", "torta") \
                and isinstance(gr.get("series"), list) and gr["series"]
            if ok:
                for se in gr["series"]:
                    d = se.get("datos") if isinstance(se, dict) else None
                    if not (isinstance(d, list) and d and all(isinstance(p, list) and len(p) == 2
                                                               and isinstance(p[1], (int, float)) for p in d)):
                        ok = False
            if not ok: E.append(f"{w}: grafica mal formada")
        f = q.get("figura")
        if f is not None:
            if not (s(f) and f.strip().startswith("<svg") and "viewBox" in f and f.strip().endswith("</svg>")):
                E.append(f"{w}: figura debe ser <svg viewBox=…>…</svg>")
            elif BAD_SVG.search(f):
                E.append(f"{w}: figura con contenido no permitido")
            elif len(f) > 6000:
                W.append(f"{w}: figura muy pesada ({len(f)} bytes)")
    for i, c in ids.items():
        if c > 1: E.append(f"{fname}: id duplicado {i}")
    n = sum(keys.values())
    if n >= 12:
        for k, c in keys.items():
            if c / n > 0.40: W.append(f"{fname}: clave {k} concentra {c}/{n}")
    return E, W


if __name__ == "__main__":
    tot, bad = 0, 0
    for fn in sys.argv[1:]:
        try:
            data = json.load(open(fn, encoding="utf-8"))
        except Exception as ex:
            print(f"ERROR {fn}: JSON inválido: {ex}"); bad += 1; continue
        E, W = validate(data, fn)
        tot += len(data) if isinstance(data, list) else 0
        for e in E: print("ERROR", e)
        for x in W: print("AVISO", x)
        bad += len(E)
        print(f"{fn}: {len(data) if isinstance(data, list) else 0} ítems, {len(E)} errores, {len(W)} avisos")
    print(f"TOTAL {tot} ítems · {bad} errores")
    sys.exit(1 if bad else 0)
