import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import * as serviceWorker from "./serviceWorker";  // 引入 serviceWorker 文件

const container = document.getElementById("root");

if (!container) {
  throw new Error("Root container missing in index.html");
}

const root = ReactDOM.createRoot(container);

root.render(
    <App />
);

// 注册 Service Worker
serviceWorker.register({
  onUpdate: (registration) => {
    if (window.confirm('A new version is available. Would you like to refresh the page to update?')) {
      const waitingWorker = registration.waiting;
      if (waitingWorker) {
        waitingWorker.postMessage({ action: 'skipWaiting' });
        waitingWorker.addEventListener('statechange', (event:any) => {
          if (event.target.state === 'activated') {
            window.location.reload();
          }
        });
      }
    }
  },
});
