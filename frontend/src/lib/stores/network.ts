import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Network status store
function createNetworkStore() {
  const { subscribe, set } = writable(true); // Default to online

  return {
    subscribe,
    setOnline: () => set(true),
    setOffline: () => set(false),
    checkConnection: async () => {
      if (!browser) return true;

      try {
        // Use a lightweight request to check connectivity
        const response = await fetch('http://localhost:8001/health', {
          method: 'GET',
          cache: 'no-cache',
        });
        const isOnline = response.ok;
        set(isOnline);
        return isOnline;
      } catch {
        set(false);
        return false;
      }
    },
  };
}

export const networkStatus = createNetworkStore();

// Derived stores for UI
export const isOnline = derived(networkStatus, $network => $network);
export const isOffline = derived(networkStatus, $network => !$network);

// Initialize network listeners if in browser
if (browser) {
  // Listen for online/offline events

  window.addEventListener('online', () => {
    networkStatus.setOnline();
  });

  window.addEventListener('offline', () => {
    networkStatus.setOffline();
  });

  // Initial check
  networkStatus.checkConnection();

  // Periodic connectivity check (every 30 seconds when offline)

  setInterval(() => {
    networkStatus.checkConnection();
  }, 30000);
}
