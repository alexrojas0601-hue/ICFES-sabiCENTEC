/* SABI PREICFES CENTEC · service worker: todo funciona sin internet tras la primera visita */
const VERSION = "preicfes-v3.0.0";
const CORE = ["./","index.html","manifest.webmanifest","assets/sabi.jpg","assets/sabi-face.jpg","assets/icon-192.png","assets/icon-512.png",
  "banco/indice.json","banco/9.json","banco/10.json","banco/11.json"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  // red primero (contenido fresco cuando hay internet), caché como respaldo sin conexión
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok) { const cp = r.clone(); caches.open(VERSION).then(c => c.put(e.request, cp)); }
    return r;
  }).catch(() => caches.match(e.request, {ignoreSearch: true}).then(r => r || caches.match("index.html"))));
});
