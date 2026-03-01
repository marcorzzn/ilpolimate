---
    layout: null
---
const CACHE_NAME = 'polimate-cache-v2';
const urlsToCache = [
    '{{ site.baseurl }}/',
    '{{ site.baseurl }}/index.html',
    '{{ site.baseurl }}/map.html',
    '{{ site.baseurl }}/ultima-ora.html',
    '{{ site.baseurl }}/archivio/',
    '{{ site.baseurl }}/assets/data/headlines.json',
    '{{ site.baseurl }}/assets/data/tensions.json',
    '{{ site.baseurl }}/assets/data/latest_news.json',
    'https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Inter:wght@400;500;600&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).then(response => {
            // If the fetch is successful, cache it and return
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
                if (event.request.method === 'GET' && event.request.url.startsWith(self.location.origin)) {
                    cache.put(event.request, responseClone);
                }
            });
            return response;
        }).catch(() => {
            // If network fails, try to return from cache
            return caches.match(event.request);
        })
    );
});

self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
