// SET KAMPÜSE HOŞ GELDİN FEST — SERVICE WORKER (BACKGROUND PUSH NOTIFICATIONS)
const CACHE_NAME = 'set-fest-v2';

self.addEventListener('install', function(event) {
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  event.waitUntil(self.clients.claim());
});

// PUSH EVENT — FIRES EVEN WHEN APPLICATION / TAB IS COMPLETELY CLOSED
self.addEventListener('push', function(event) {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: '📋 SET Festivali Görev Bildirimi', body: event.data.text() };
    }
  }

  const title = data.title || '📋 Sana Yeni Görev Atandı!';
  const options = {
    body: data.body || 'SET Kampüse Hoş Geldin Fest için yeni bir görev atandı.',
    icon: './SET WS LOGO.png',
    badge: './SET WS LOGO.png',
    vibrate: [350, 150, 350, 150, 450],
    tag: data.tag || ('set-task-' + (data.task_id || Date.now())),
    renotify: true,
    requireInteraction: true,
    silent: false,
    timestamp: Date.now(),
    data: {
      url: data.url || '/',
      taskId: data.task_id || ''
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// NOTIFICATION CLICK — OPENS OR FOCUSES THE TAB & HIGHLIGHTS TASK
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const notifData = event.notification.data || {};
  const targetUrl = notifData.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
      for (let i = 0; i < clientList.length; i++) {
        let client = clientList[i];
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          if (notifData.taskId) {
            client.postMessage({ type: 'FOCUS_TASK', taskId: notifData.taskId });
          }
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
