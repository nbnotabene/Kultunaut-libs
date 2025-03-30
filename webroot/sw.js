
const CACHE_NAME = 'svanekebio-cache-v1';
// no cache   '/','/index.html',

window.addEventListener('load', function() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(registration => {
      registration.unregister().then(function(boolean) {
        if (boolean) {
          console.log("Service worker unregistered");
          // Clear the cache
          if ('caches' in window) {
            caches.keys().then(function(cacheNames) {
              cacheNames.forEach(function(cacheName) {
                caches.delete(cacheName).then(function() {
                  console.log(`Cache "${cacheName}" deleted.`);
                });
              });
            });
          }
        } else {
          console.log("Service worker unregistration failed");
        }
      });
    });
  }
});



// if ('serviceWorker' in navigator) {
//   navigator.serviceWorker.ready.then(registration => {
//     registration.unregister();
//   });
// }
// 
// 
// const urlsToCache = [
//   '/css/basic.css',
// 	'/css/page.css',
// 	'/css/overlay.css',
// 	'/css/arr.css',
// 	'/css/films.css',
// 	'/img/icons/web-app-manifest-192x192.png',
// 	'/img/icons/web-app-manifest-512x512.png',
// 	'/img/icons/apple-touch-icon.png',
// 	'/img/icons/favicon.ico'
// ];
// 
// self.addEventListener('install', function(event) {
//   // Perform install steps
//   event.waitUntil(
//     caches.open(CACHE_NAME)
//       .then(function(cache) {
//         console.log('Opened cache');
//         return cache.addAll(urlsToCache);
//       })
//   );
// });

// self.addEventListener('fetch', function(event) {
//   event.respondWith(
//     caches.match(event.request)
//       .then(function(response) {
//         if (response) {
//           return response;
//         }
//         return fetch(event.request);
//       })
//   );
// });
// 
// self.addEventListener('fetch', function(event) {
//   event.respondWith(
//     caches.match(event.request)
//       .then(function(response) {
//         // Cache hit - return response
//         if (response) {
//           return response;
//         }
// 
//         // IMPORTANT: Exclude index.html from cache match, and always fetch from network.
//         if (event.request.url.endsWith('index.html')) {
//           return fetch(event.request);
//         }
// 
//         return fetch(event.request).then(
//           function(response) {
//             // Check if we received a valid response
//             if(!response || response.status !== 200 || response.type !== 'basic') {
//               return response;
//             }
// 
//             // IMPORTANT: Clone the response.
//             // A response is a stream and because we want the browser to consume the response
//             // as well as the cache consuming the response, we need to clone it.
//             //var responseToCache = response.clone();
// //
//             //caches.open(CACHE_NAME)
//             //  .then(function(cache) {
//             //    cache.put(event.request, responseToCache);
//             //  });
// //
//             //return response;
//           }
//         );
//       })
//     );
// });