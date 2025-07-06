/**
 * MercadoLibre OAuth API Client
 * 
 * HTTP client for ML OAuth integration with error handling and validation.
 */

import { env } from '$env/dynamic/public';
import type {
	MLOAuthInitiateRequest,
	MLOAuthInitiateResponse,
	MLOAuthCallbackRequest,
	MLOAuthCallbackResponse,
	MLConnectionStatusResponse,
	MLDisconnectRequest,
	MLDisconnectResponse,
	MLTokenRefreshResponse,
	MLErrorResponse,
	MLRateLimitResponse
} from '$lib/types/ml-connection';

// API configuration
const API_BASE_URL = env.PUBLIC_API_BASE_URL || 'http://localhost:8080';
const ML_OAUTH_BASE = `${API_BASE_URL}/auth/ml`;

// Error classes
export class MLOAuthError extends Error {
	constructor(
		message: string,
		public errorCode: string,
		public statusCode: number,
		public details?: any
	) {
		super(message);
		this.name = 'MLOAuthError';
	}
}

export class MLManagerAccountError extends MLOAuthError {
	constructor(message: string, public guidance: string) {
		super(message, 'manager_account_required', 403);
		this.name = 'MLManagerAccountError';
	}
}

export class MLRateLimitError extends MLOAuthError {
	constructor(message: string, public retryAfter: number) {
		super(message, 'rate_limited', 429);
		this.name = 'MLRateLimitError';
	}
}

// Helper function to get auth token
function getAuthToken(): string | null {
	if (typeof localStorage === 'undefined') return null;
	return localStorage.getItem('auth_token');
}

// Helper function to make authenticated requests
async function makeAuthenticatedRequest(
	endpoint: string,
	options: RequestInit = {}
): Promise<Response> {
	const token = getAuthToken();
	if (!token) {
		throw new MLOAuthError('Authentication required', 'auth_required', 401);
	}

	const headers = {
		'Content-Type': 'application/json',
		'Authorization': `Bearer ${token}`,
		...options.headers
	};

	const response = await fetch(endpoint, {
		...options,
		headers
	});

	// Handle rate limiting
	if (response.status === 429) {
		const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
		const errorData = await response.json().catch(() => ({}));
		throw new MLRateLimitError(
			errorData.error_description || 'Too many requests. Please try again later.',
			retryAfter
		);
	}

	// Handle manager account errors
	if (response.status === 403) {
		const errorData = await response.json().catch(() => ({}));
		if (errorData.error === 'manager_account_required') {
			throw new MLManagerAccountError(
				errorData.error_description || 'Manager account required',
				errorData.guidance || 'Please use a MercadoLibre manager account'
			);
		}
	}

	// Handle other errors
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		throw new MLOAuthError(
			errorData.error_description || `HTTP ${response.status}`,
			errorData.error || 'api_error',
			response.status,
			errorData
		);
	}

	return response;
}

// ML OAuth API client
export const mlOAuthApi = {
	/**
	 * Initiate OAuth flow
	 */
	async initiateOAuth(
		redirectUri: string,
		siteId: string = 'MLA'
	): Promise<MLOAuthInitiateResponse> {
		const request: MLOAuthInitiateRequest = {
			redirect_uri: redirectUri,
			site_id: siteId
		};

		const response = await makeAuthenticatedRequest(`${ML_OAUTH_BASE}/initiate`, {
			method: 'POST',
			body: JSON.stringify(request)
		});

		return response.json();
	},

	/**
	 * Handle OAuth callback
	 */
	async handleCallback(
		code: string,
		state: string,
		codeVerifier: string
	): Promise<MLOAuthCallbackResponse> {
		const request: MLOAuthCallbackRequest = {
			code,
			state,
			code_verifier: codeVerifier
		};

		const response = await makeAuthenticatedRequest(`${ML_OAUTH_BASE}/callback`, {
			method: 'POST',
			body: JSON.stringify(request)
		});

		return response.json();
	},

	/**
	 * Get connection status
	 */
	async getConnectionStatus(): Promise<MLConnectionStatusResponse> {
		const response = await makeAuthenticatedRequest(`${ML_OAUTH_BASE}/status`);
		return response.json();
	},

	/**
	 * Disconnect ML account
	 */
	async disconnect(): Promise<MLDisconnectResponse> {
		const request: MLDisconnectRequest = {
			confirm: true
		};

		const response = await makeAuthenticatedRequest(`${ML_OAUTH_BASE}/disconnect`, {
			method: 'POST',
			body: JSON.stringify(request)
		});

		return response.json();
	},

	/**
	 * Refresh tokens manually
	 */
	async refreshTokens(): Promise<MLTokenRefreshResponse> {
		const response = await makeAuthenticatedRequest(`${ML_OAUTH_BASE}/refresh`, {
			method: 'POST'
		});

		return response.json();
	},

	/**
	 * Build redirect URI for current environment
	 */
	buildRedirectUri(path: string = '/ml-setup/callback'): string {
		if (typeof window === 'undefined') {
			// Server-side fallback
			return `${API_BASE_URL}${path}`;
		}
		
		const { protocol, hostname, port } = window.location;
		const portSuffix = port && port !== '80' && port !== '443' ? `:${port}` : '';
		
		return `${protocol}//${hostname}${portSuffix}${path}`;
	},

	/**
	 * Validate redirect URI format
	 */
	validateRedirectUri(uri: string): boolean {
		try {
			const url = new URL(uri);
			return ['http:', 'https:'].includes(url.protocol);
		} catch {
			return false;
		}
	},

	/**
	 * Handle errors with user-friendly messages
	 */
	formatError(error: unknown): string {
		if (error instanceof MLManagerAccountError) {
			return `${error.message}\n\n${error.guidance}`;
		}
		
		if (error instanceof MLRateLimitError) {
			return `${error.message} Please wait ${error.retryAfter} seconds before trying again.`;
		}
		
		if (error instanceof MLOAuthError) {
			switch (error.errorCode) {
				case 'invalid_grant':
					return 'The authorization code has expired. Please try connecting again.';
				case 'invalid_client':
					return 'Invalid application credentials. Please contact support.';
				case 'validation_error':
					return error.message;
				case 'auth_required':
					return 'Please log in to connect your MercadoLibre account.';
				default:
					return error.message;
			}
		}
		
		if (error instanceof Error) {
			return error.message;
		}
		
		return 'An unexpected error occurred. Please try again.';
	},

	/**
	 * Check if error requires user action
	 */
	requiresUserAction(error: unknown): boolean {
		if (error instanceof MLManagerAccountError) return true;
		if (error instanceof MLOAuthError) {
			return ['invalid_grant', 'auth_required'].includes(error.errorCode);
		}
		return false;
	},

	/**
	 * Get retry delay for rate limit errors
	 */
	getRetryDelay(error: unknown): number | null {
		if (error instanceof MLRateLimitError) {
			return error.retryAfter * 1000; // Convert to milliseconds
		}
		return null;
	}
};