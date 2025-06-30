import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { config } from '$lib/config';

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
        // Use centralized configuration for health check
        const response = await fetch(config.getApiUrl(config.api.HEALTH_ENDPOINT), {
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

// Initialize network listeners if in browser and feature is enabled
if (browser && config.features.NETWORK_MONITORING) {
  // Listen for online/offline events
  window.addEventListener('online', () => {
    networkStatus.setOnline();
  });

  window.addEventListener('offline', () => {
    networkStatus.setOffline();
  });

  // Initial check
  networkStatus.checkConnection();

  // Periodic connectivity check using configured interval (but less frequent)
  setInterval(() => {
    networkStatus.checkConnection();
  }, config.network.HEALTH_CHECK_INTERVAL);
}
