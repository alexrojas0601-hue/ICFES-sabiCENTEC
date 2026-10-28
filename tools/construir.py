#!/usr/bin/env python3
"""Construye el banco de SABI PREICFES CENTEC (preicfes.sabicentec.com).
Uso (desde la raíz del repo):  python3 tools/construir.py

Fuentes:
  banco_raw/base/<grado>-<area>.json   banco validado heredado de saber.sabicentec.com
  banco_raw/nuevo/*.json               lotes nuevos (formato v3: área "lectura", nivel 1–4,
                                       tabla.columnas, grafica.series[].datos = [[x, y], …])
  banco_raw/*.json                     cualquier lote futuro ya en formato del motor
Salida:
  banco/<grado>-<area>.json, banco/indice.json, sw.js, manifest.json
Solo publica ítems que pasan el Dot Auditor estructural (validar_banco.py); el resto queda en el informe."""
import collections, glob, json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from validar_banco import validate

COMP = {"Identificar y entender contenidos locales": "Identificar y entender los contenidos locales de un texto",
        "Comprender cómo se articulan las partes de un texto": "Comprender cómo se articulan las partes de un texto para darle un sentido global",
        "Reflexionar y evaluar": "Reflexionar a partir de un texto y evaluar su contenido",
        "Reflexionar a partir de un texto y evaluar su contenido": "Reflexionar a partir de un texto y evaluar su contenido"}
NIVEL = {1: "Mínimo", 2: "Mínimo", 3: "Satisfactorio", 4: "Avanzado"}  # niveles ICFES 1–4 → 3 niveles del motor


def num(v):
    if isinstance(v, (int, float)): return v
    s = str(v).strip().replace("−", "-").replace("%", "").replace("$", "").replace(" ", "")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", s): s = s.replace(".", "")
    s = s.replace(",", ".")
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?", s) else None


def norm_grafica(g):
    """Formato v3 → formato del motor. Devuelve None si no se puede convertir sin perder datos."""
    if not isinstance(g, dict): return None
    if "etiquetas" in g or (g.get("tipo") == "puntos" and all("puntos" in s for s in g.get("series", []))):
        return g
    t, series = g.get("tipo"), g.get("series") or []
    out = {k: g[k] for k in ("tipo", "titulo", "ejeX", "ejeY") if g.get(k)}
    if t == "puntos":
        out["series"] = []
        for s in series:
            pts = [[num(x), num(y)] for x, y in s.get("datos", [])]
            if not pts or any(v is None for p in pts for v in p): return None
            out["series"].append({"nombre": s.get("nombre", ""), "puntos": pts})
        return out
    labels = [str(x) for x, _ in series[0].get("datos", [])] if series else []
    out["etiquetas"], out["series"] = labels, []
    for s in series:
        d = dict((str(x), num(y)) for x, y in s.get("datos", []))
        if set(d) != set(labels) or any(v is None for v in d.values()):
            if t == "lineas":  # ejes X numéricos distintos por serie → dispersión con líneas
                g2 = dict(g, tipo="puntos"); r = norm_grafica(g2)
                if r: r["unir"] = True
                return r
            return None
        out["series"].append({"nombre": s.get("nombre", ""), "datos": [d[l] for l in labels]})
    return out


def norm_v3(q, pref=""):
    q = dict(q)
    if pref and not q["id"].startswith(pref): q["id"] = pref + q["id"]
    if q.get("area") == "lectura": q["area"] = "lenguaje"
    q["competencia"] = COMP.get(q.get("competencia"), q.get("competencia"))
    if isinstance(q.get("nivel"), int): q["nivel"] = NIVEL.get(q["nivel"], "Satisfactorio")
    if q["area"] == "ingles" and q.get("mcer") == "A":
        q["mcer"] = "A1"
    t = q.get("tabla")
    if isinstance(t, dict) and "columnas" in t and "cols" not in t:
        t = dict(t); t["cols"] = t.pop("columnas"); q["tabla"] = t
    if "grafica" in q:
        g = norm_grafica(q["grafica"])
        if g is None: q["grafica"] = "INVALIDA"
        else: q["grafica"] = g
    q.pop("contenido", None)
    return q


items, rep = [], collections.Counter()
for f in sorted(glob.glob(os.path.join(ROOT, "banco_raw", "base", "*.json"))):
    for q in json.load(open(f, encoding="utf-8")):
        items.append(q); rep["base"] += 1
for f in sorted(glob.glob(os.path.join(ROOT, "banco_raw", "nuevo", "*.json"))):
    for q in json.load(open(f, encoding="utf-8")):
        items.append(norm_v3(q, "C")); rep["nuevo"] += 1
for f in sorted(glob.glob(os.path.join(ROOT, "banco_raw", "*.json"))):
    if ".parte" in f: continue
    for q in json.load(open(f, encoding="utf-8")):
        items.append(norm_v3(q)); rep["lotes"] += 1

ok, seen, ids, descartes = [], set(), set(), []
for q in items:
    E, _ = validate([q], q.get("id", "?"))
    k = (re.sub(r"\s+", " ", q.get("enunciado", "").strip().lower()), q.get("contexto", "")[:60])
    if E: descartes.append((q.get("id"), E[0])); continue
    if k in seen or q["id"] in ids: descartes.append((q["id"], "duplicado")); continue
    seen.add(k); ids.add(q["id"]); ok.append(q)

# Contextos compartidos: el motor agrupa por contexto idéntico; se mantienen juntos y en orden.
groups = collections.defaultdict(list)
for q in ok: groups[f'{q["grado"]}-{q["area"]}'].append(q)
os.makedirs(os.path.join(ROOT, "banco"), exist_ok=True)
for f in glob.glob(os.path.join(ROOT, "banco", "*.json")): os.remove(f)
version = time.strftime("%Y%m%d%H%M")
for k, arr in groups.items():
    json.dump(arr, open(os.path.join(ROOT, "banco", k + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
idx = {"version": version, "total": len(ok), "files": {k: len(v) for k, v in sorted(groups.items())}}
json.dump(idx, open(os.path.join(ROOT, "banco", "indice.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Service worker: shell + banco completo en caché para uso sin internet.
sw = open(os.path.join(ROOT, "tools", "sw.plantilla.js"), encoding="utf-8").read().replace("__VERSION__", version)
open(os.path.join(ROOT, "sw.js"), "w", encoding="utf-8").write(sw)
json.dump({"name": "SABI PREICFES CENTEC", "short_name": "SABI PREICFES", "start_url": "./", "scope": "./",
           "display": "standalone", "background_color": "#ffffff", "theme_color": "#1A2D7A", "lang": "es-CO",
           "description": "Entrenamiento tipo Saber 11 con Ruta del Error · CENTEC Córdoba",
           "icons": [{"src": "assets/icono.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]},
          open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Informe del Dot Auditor estructural
vis = collections.Counter()
for q in ok:
    for c in ("tabla", "grafica", "figura"):
        if q.get(c): vis[c + (":" + q[c]["tipo"] if c == "grafica" else "")] += 1
lines = [f"# Informe de construcción del banco · versión {version}", "",
         f"- Ítems leídos: {sum(rep.values())} ({dict(rep)})", f"- Publicados: **{len(ok)}**",
         f"- Descartados: {len(descartes)}", f"- Recursos visuales: {dict(vis)}", "", "## Por archivo", ""]
lines += [f"- {k}: {v}" for k, v in idx["files"].items()]
lines += ["", "## Niveles", ""] + [f"- {k}: {v}" for k, v in collections.Counter(q["nivel"] for q in ok).items()]
lines += ["", "## Descartes (revisar)", ""] + [f"- {i}: {e}" for i, e in descartes] + ["",
          "Todo el banco está **en revisión docente**: el validador comprueba estructura; la exactitud la confirma el docente del área."]
open(os.path.join(ROOT, "docs", "INFORME-BANCO.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"Publicados {len(ok)} · descartados {len(descartes)} · versión {version}")
for i, e in descartes[:40]: print("  -", i, e)
