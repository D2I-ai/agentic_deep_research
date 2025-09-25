const CACHE_VERSION = 1;  // 每次发布更新时更改这个版本号
const CURRENT_CACHE = `my-app-cache-v${CACHE_VERSION}`;

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CURRENT_CACHE).then(cache => {
      return cache.addAll([
        '/',
        '/index.html',
        '/static/css/main.css',
        '/static/js/main.js'
        // Add other static assets that need to be cached
      ]);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CURRENT_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

self.addEventListener('message', event => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});
