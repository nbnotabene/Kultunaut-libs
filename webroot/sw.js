const CACHE_NAME = 'svanekebio-cache-v1';
// no cache   '/','/index.html',

const urlsToCache = [
  '/css/basic.css',
	'/css/page.css',
	'/css/overlay.css',
	'/css/arr.css',
	'/css/films.css',
	'/img/icons/web-app-manifest-192x192.png',
	'/img/icons/web-app-manifest-512x512.png',
	'/img/icons/apple-touch-icon.png',
	'/img/icons/favicon.ico'
];

self.addEventListener('install', function(event) {
  // Perform install steps
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
