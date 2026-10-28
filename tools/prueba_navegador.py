import json, subprocess, sys, time, glob, os
from playwright.sync_api import sync_playwright

REPO = "/home/claude/icfes-sabicentec"
OUT = os.environ.get("OUT", "/tmp")
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8765", "-d", REPO], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
        for nombre, vp in [("pc", {"width": 1280, "height": 900}), ("cel", {"width": 390, "height": 844})]:
            pg = b.new_page(viewport=vp)
            pg.on("pageerror", lambda e: errs.append(f"{nombre} pageerror: {e}"))
            pg.on("console", lambda m: m.type == "error" and "sabi-puerta" not in m.text and "net::" not in m.text and errs.append(f"{nombre} console: {m.text}"))
            pg.goto("http://localhost:8765/")
            pg.wait_for_function("document.querySelector('#nBank') && /\\d/.test(document.querySelector('#nBank').textContent)")
            print(nombre, "banco:", pg.inner_text("#nBank"))
            pg.screenshot(path=f"{OUT}/{nombre}-inicio.png", full_page=True)
            pg.fill("#inName", "Prueba Auditor")
            pg.select_option("#inGrade", "11")
            pg.select_option("#inSize", "0.2")
            pg.click("button[type=submit]")
            pg.wait_for_selector(".stem", timeout=20000)
            n = len(pg.query_selector_all(".dots button"))
            print(nombre, "simulacro con", n, "preguntas")
            for k in range(n):
                pg.click(".opts .opt >> nth=%d" % (k % 3))
                if k < n-1: pg.click("#next")
            pg.click("#finish")
            if pg.query_selector("#finish"): pg.click("#finish")
            pg.wait_for_selector("#goRuta")
            ov = pg.evaluate("document.documentElement.scrollWidth>window.innerWidth+2")
            if ov: errs.append(f"{nombre}: desborde horizontal en resultados")
            pg.screenshot(path=f"{OUT}/{nombre}-resultados.png", full_page=True)
            pg.click("#goRuta"); time.sleep(0.6)
            pg.screenshot(path=f"{OUT}/{nombre}-ruta.png", full_page=True)
            txt = pg.inner_text("#app") if pg.query_selector("#app") else pg.inner_text("body")
            pg.click(".erritem >> nth=0"); time.sleep(0.4)
            pasos=[]
            for _ in range(6):
                t = pg.inner_text("body"); pasos.append(t[:0])
                nxt = pg.query_selector("button.primary:visible")
                if not nxt: break
                nxt.click(); time.sleep(0.3)
            pg.screenshot(path=f"{OUT}/{nombre}-paso.png", full_page=True)
            print(nombre, "ruta abre detalle:", "error revela" in pg.inner_text("body") or "gemelo" in pg.inner_text("body").lower())
            pg.close()
        # render de todos los ítems con recursos visuales
        pg = b.new_page(viewport={"width": 1000, "height": 800})
        pg.on("pageerror", lambda e: errs.append(f"visual pageerror: {e}"))
        pg.goto("http://localhost:8765/"); pg.wait_for_function("typeof window.SABI_RENDER==='function'")
        items = [q for f in glob.glob(f"{REPO}/banco/*-*.json") for q in json.load(open(f)) if q.get("tabla") or q.get("grafica") or q.get("figura")]
        bad = pg.evaluate("""(items)=>{const bad=[];const d=document.createElement('div');document.body.appendChild(d);
          for(const q of items){try{d.innerHTML=window.SABI_RENDER(q);const svg=d.querySelector('svg');
            if((q.grafica||q.figura)&&!svg)bad.push(q.id+': sin svg');
            if(d.innerHTML.includes('NaN')||d.innerHTML.includes('undefined'))bad.push(q.id+': NaN/undefined');}catch(e){bad.push(q.id+': '+e.message)}}
          return bad}""", items)
        print("ítems visuales renderizados:", len(items), "fallas:", len(bad), bad[:15])
        for tipo in ["torta", "puntos", "figura"]:
            q = next(q for q in items if (q.get("grafica") or {}).get("tipo") == tipo or (tipo == "figura" and q.get("figura")))
            pg.evaluate("(q)=>{document.body.innerHTML='<main class=page style=max-width:640px;padding:20px>'+window.SABI_RENDER(q)+'</main>'}", q)
            pg.screenshot(path=f"{OUT}/visual-{tipo}.png")
        b.close()
finally:
    srv.terminate()
print("ERRORES:", errs if errs else "ninguno")
