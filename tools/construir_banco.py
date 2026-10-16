#!/usr/bin/env python3
"""Une los archivos finales de banco_raw/ (sin .parteN), valida y publica banco/<grado>.json + banco/indice.json.
Uso: python3 tools/construir_banco.py            (solo ítems sin errores)"""
import glob, json, os, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from validar_banco import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sorted(f for f in glob.glob(os.path.join(ROOT, "banco_raw", "*.json")) if not re.search(r"\.parte\d+\.json$", f))
by_grade, seen, bad = defaultdict(list), set(), 0
for f in files:
    data = json.load(open(f, encoding="utf-8"))
    for q in data:
        E, _ = validate([q], os.path.basename(f))
        if E or q.get("id") in seen:
            bad += 1
            continue
        seen.add(q["id"])
        by_grade[q["grado"]].append(q)
os.makedirs(os.path.join(ROOT, "banco"), exist_ok=True)
idx = {"version": __import__("datetime").date.today().isoformat(), "grados": {}}
for g in (9, 10, 11):
    items = by_grade.get(g, [])
    json.dump(items, open(os.path.join(ROOT, "banco", f"{g}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    idx["grados"][str(g)] = {
        "total": len(items),
        "areas": dict(Counter(q["area"] for q in items)),
        "competencias": dict(Counter(q["area"] + " · " + q["competencia"] for q in items)),
        "niveles": dict(Counter(str(q["nivel"]) for q in items)),
        "visuales": sum(1 for q in items if q.get("tabla") or q.get("grafica") or q.get("figura")),
    }
json.dump(idx, open(os.path.join(ROOT, "banco", "indice.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(v["total"] for v in idx["grados"].values())
print(f"{len(files)} archivos · {tot} ítems publicados · {bad} descartados")
for g, v in idx["grados"].items():
    print(f"  {g}°: {v['total']} {v['areas']} visuales={v['visuales']}")
