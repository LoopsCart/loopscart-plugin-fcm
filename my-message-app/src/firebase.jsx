import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from 'firebase/messaging';
// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyABXH6F1gbGdJCPW0KZBBBuJM9X4EgjFEs",
    authDomain: "message-testing-8db7c.firebaseapp.com",
    projectId: "message-testing-8db7c",
    storageBucket: "message-testing-8db7c.firebasestorage.app",
    messagingSenderId: "400864901695",
    appId: "1:400864901695:web:c1f51e81bf798e2998d68a",
    measurementId: "G-DW2YY4Q6F1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

const messaging = getMessaging(app);

export { messaging, onMessage, getToken }