/**
 * Authentication guards for route protection.
 *
 * Provides utilities for protecting routes and handling authentication redirects
 * in SvelteKit applications.
 */

import { goto } from '$app/navigation';
import { get } from 'svelte/store';
import { authStore, isAuthenticated } from '../stores/auth';

/**
 * Redirect unauthenticated users to login page
 */
export function requireAuth(redirectTo?: string): Promise<boolean> {
  return new Promise(resolve => {
    const unsubscribe = isAuthenticated.subscribe(authenticated => {
      if (!authenticated) {
        // Build login URL with redirect parameter
        const loginUrl = new URL('/auth/login', window.location.origin);
        if (redirectTo) {
          loginUrl.searchParams.set('redirect', redirectTo);
        } else if (typeof window !== 'undefined') {
          loginUrl.searchParams.set('redirect', window.location.pathname + window.location.search);
        }

        goto(loginUrl.toString());
        resolve(false);
      } else {
        resolve(true);
      }
      unsubscribe();
    });
  });
}

/**
 * Redirect authenticated users away from auth pages
 */
export function requireGuest(redirectTo: string = '/'): Promise<boolean> {
  return new Promise(resolve => {
    const unsubscribe = isAuthenticated.subscribe(authenticated => {
      if (authenticated) {
        goto(redirectTo);
        resolve(false);
      } else {
        resolve(true);
      }
      unsubscribe();
    });
  });
}

/**
 * Check if user is authenticated (synchronous)
 */
export function isUserAuthenticated(): boolean {
  return get(isAuthenticated);
}

/**
 * Get current user (synchronous)
 */
export function getCurrentUser() {
  const authState = get(authStore);
  return authState.user;
}

/**
 * Check if user has specific permissions (placeholder for future role-based access)
 */
export function hasPermission(_permission: string): boolean {
  const user = getCurrentUser();

  // For MVP, all authenticated users have all permissions
  if (!user) return false;

  // Future: implement role-based permissions
  // return user.permissions?.includes(permission) || user.role === 'admin';

  return true;
}

/**
 * Route guard middleware function for SvelteKit load functions
 */
export async function authGuard(options?: {
  requireAuth?: boolean;
  requireGuest?: boolean;
  redirectTo?: string;
  permission?: string;
}) {
  const {
    requireAuth: needsAuth,
    requireGuest: needsGuest,
    redirectTo,
    permission,
  } = options || {};

  const authenticated = isUserAuthenticated();

  // Check authentication requirement
  if (needsAuth && !authenticated) {
    const loginUrl = new URL('/auth/login', window.location.origin);
    if (redirectTo || typeof window !== 'undefined') {
      const redirect = redirectTo || window.location.pathname + window.location.search;
      loginUrl.searchParams.set('redirect', redirect);
    }

    throw new Response(null, {
      status: 302,
      headers: {
        location: loginUrl.toString(),
      },
    });
  }

  // Check guest requirement
  if (needsGuest && authenticated) {
    throw new Response(null, {
      status: 302,
      headers: {
        location: redirectTo || '/',
      },
    });
  }

  // Check permission requirement
  if (permission && !hasPermission(permission)) {
    throw new Response(null, {
      status: 403,
      headers: {
        location: '/unauthorized',
      },
    });
  }

  return { authenticated, user: getCurrentUser() };
}

/**
 * Helper for protected page components
 */
export function useAuthGuard(options?: { redirectTo?: string; permission?: string }) {
  const { redirectTo, permission } = options || {};

  // Check authentication
  const authenticated = isUserAuthenticated();
  if (!authenticated) {
    requireAuth(redirectTo);
    return { loading: true, authenticated: false, user: null };
  }

  // Check permission
  if (permission && !hasPermission(permission)) {
    goto('/unauthorized');
    return { loading: true, authenticated: false, user: null };
  }

  return {
    loading: false,
    authenticated: true,
    user: getCurrentUser(),
  };
}

/**
 * Logout helper with redirect
 */
export async function logoutAndRedirect(redirectTo: string = '/') {
  try {
    await authStore.logout();
    goto(redirectTo);
  } catch (error) {
    console.error('Logout failed:', error);
    // Force local logout even if API call fails
    authStore.clearAuth();
    goto(redirectTo);
  }
}
