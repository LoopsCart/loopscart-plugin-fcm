// public/firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/10.11.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.11.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyABXH6F1gbGdJCPW0KZBBBuJM9X4EgjFEs",
    projectId: "message-testing-8db7c",
    messagingSenderId: "400864901695",
    appId: "1:400864901695:web:c1f51e81bf798e2998d68a",
});

// public/firebase-messaging-sw.js
console.log('[SW] Firebase Messaging Service Worker Loaded');


const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
    console.log('[firebase-messaging-sw.js] Received background message:', payload);
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: '/firebase-logo.png'
    });
});
