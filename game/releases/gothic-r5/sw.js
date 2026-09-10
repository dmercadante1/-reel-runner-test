'use strict';
const CACHE='gothic-r5-6d5bf642fbdc-offline2';
const BASE=new URL('./',self.location).href;
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 await cache.addAll([BASE,BASE+'manifest.webmanifest',BASE+'icon-180.png',BASE+'icon-192.png',BASE+'icon-512.png']);
 await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
 const request=event.request;
 if(request.method!=='GET'||!request.url.startsWith(BASE))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  const saved=await cache.match(request,{ignoreSearch:true});
  if(saved)return saved;
  if(request.mode==='navigate'){
   const app=await cache.match(BASE);
   if(app)return app;
  }
  return fetch(request);
 })());
});
