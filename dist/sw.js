/* Service worker de U24 FM26.
   Cachea la app completa en la instalación para que buscar funcione sin cobertura.
   Estrategia: cache-first para lo propio; la red solo se usa para actualizar. */

const CACHE = 'u24-fm26-v4';

/* Solo lo imprescindible para que la app funcione sin cobertura.
   index.html ya lleva dentro los datos, la tipografía y el emblema.
   Los iconos NO se precachean: los descarga el sistema al instalar el acceso
   directo y no hacen falta para buscar. Precacharlos costaba 680 KB extra
   antes de que la app estuviera lista, justo en el Real y con la red saturada.
   El manejador de fetch los cachea igualmente si el navegador los pide. */
const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      // addAll falla en bloque si un recurso no existe: se añaden de uno en uno.
      .then(cache => Promise.all(
        ASSETS.map(url => cache.add(url).catch(() => {}))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;

  // Solo se gestionan navegaciones y recursos propios en GET.
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // El propio service worker nunca se cachea: una copia rancia aquí podría
  // impedir que el equipo reciba una corrección de coordenadas.
  if (url.pathname.endsWith('/sw.js')) return;

  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put('./index.html', copy));
          return res;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  event.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(req, copy));
      return res;
    }))
  );
});
