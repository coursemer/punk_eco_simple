// Configuration du Service Worker
const CACHE_NAME = 'punk-eco-v1';
const OFFLINE_URL = '/offline.html';

// Fichiers à mettre en cache immédiatement
const PRECACHE_ASSETS = [
  '/',
  '/static/css/base.css',
  '/static/css/header.css',
  '/static/css/footer.css',
  '/static/css/custom.css',
  '/static/js/main.js',
  '/static/img/logo.png',
  '/static/img/favicon.ico',
  'https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  
  // Mise en cache des ressources critiques
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Mise en cache des ressources critiques');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker activé');
  
  // Nettoyage des anciens caches
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Suppression de l\'ancien cache :', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Stratégie de mise en cache : Cache First, Network Fallback
self.addEventListener('fetch', (event) => {
  // Ignorer les requêtes non-GET et les requêtes vers des API
  if (event.request.method !== 'GET' || 
      event.request.url.includes('/api/') || 
      event.request.url.includes('sockjs') ||
      event.request.url.includes('hot-update')) {
    return;
  }

  // Gestion des requêtes de navigation (pages)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Mise à jour du cache avec la nouvelle réponse
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          return response;
        })
        .catch(() => {
          // En cas d'erreur, essayer de servir depuis le cache
          return caches.match(event.request)
            .then((response) => {
              // Si la page n'est pas en cache, afficher la page hors ligne
              return response || caches.match(OFFLINE_URL);
            });
        })
    );
  } else {
    // Pour les autres requêtes (CSS, JS, images, etc.)
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          // Retourner la ressource en cache si elle existe
          if (response) {
            return response;
          }
          
          // Sinon, faire la requête réseau
          return fetch(event.request)
            .then((response) => {
              // Vérifier si la réponse est valide
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              
              // Mettre en cache la réponse pour les requêtes ultérieures
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, responseToCache);
                });
              
              return response;
            });
        })
    );
  }
});

// Gestion des messages pour les mises à jour
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Gestion de l'état en ligne/hors ligne
self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        try {
          const networkResponse = await fetch(event.request);
          return networkResponse;
        } catch (error) {
          const cache = await caches.open(CACHE_NAME);
          const cachedResponse = await cache.match(OFFLINE_URL);
          return cachedResponse || Response.error();
        }
      })()
    );
  }
});
