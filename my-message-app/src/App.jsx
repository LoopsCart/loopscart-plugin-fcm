// src/App.jsx
import { useEffect, useState } from "react";
import { messaging, getToken, onMessage } from "./firebase";

const VAPID_KEY = "BHlUnSON3KRDvtQ4I9MLv-ohDWj05qdB_KP-bXhf5sbRMcAsuib9jcleflmG5mgUt_-5tCu8CalIHeMBWcuqiiA"

function App() {
  const [notification, setNotification] = useState(null);

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker
      .register('/firebase-messaging-sw.js')
      .then((registration) => {
        console.log('Service Worker registered:', registration);
      })
      .catch((err) => console.error('Service Worker registration failed:', err));
  }


  useEffect(() => {
    // Request permission and get token
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        getToken(messaging, { vapidKey: VAPID_KEY })
          .then((currentToken) => {
            if (currentToken) {
              console.log("FCM Token:", currentToken);
              // Send token to backend if needed
            }
          })
          .catch(console.error);
      }
    });

    // Handle messages while app is in foreground
    onMessage(messaging, (payload) => {
      console.log("Message received. ", payload);
      setNotification(payload.notification);
    });
  }, []);

  return (
    <div>
      <h1>Firebase Cloud Messaging</h1>
      {notification && (
        <div>
          <h2>{notification.title}</h2>
          <p>{notification.body}</p>
        </div>
      )}
    </div>
  );
}

export default App;
