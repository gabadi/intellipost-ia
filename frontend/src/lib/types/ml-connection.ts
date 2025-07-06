/**
 * MercadoLibre Connection Types
 *
 * TypeScript interfaces for ML OAuth integration and connection management.
 */

export interface MLConnectionState {
  isConnected: boolean;
  connectionHealth: 'healthy' | 'expired' | 'invalid' | 'disconnected';
  mlNickname: string | null;
  mlEmail: string | null;
  mlSiteId: string | null;
  expiresAt: Date | null;
  lastValidatedAt: Date | null;
  isLoading: boolean;
  error: string | null;
  shouldRefresh: boolean;
  timeUntilRefresh: number | null;
}

export interface MLOAuthInitiateRequest {
  redirect_uri: string;
  site_id?: string;
}

export interface MLOAuthInitiateResponse {
  authorization_url: string;
  state: string;
  code_verifier: string;
  expires_in?: number;
}

export interface MLOAuthCallbackRequest {
  code: string;
  state: string;
  code_verifier: string;
}

export interface MLOAuthCallbackResponse {
  success: boolean;
  message: string;
  ml_nickname?: string;
  ml_email?: string;
  ml_site_id: string;
  connection_health: string;
}

export interface MLConnectionStatusResponse {
  is_connected: boolean;
  connection_health: 'healthy' | 'expired' | 'invalid' | 'disconnected';
  ml_nickname?: string;
  ml_email?: string;
  ml_site_id?: string;
  expires_at?: string;
  last_validated_at?: string;
  error_message?: string;
  should_refresh: boolean;
  time_until_refresh?: number;
}

export interface MLDisconnectRequest {
  confirm?: boolean;
}

export interface MLDisconnectResponse {
  success: boolean;
  message: string;
}

export interface MLTokenRefreshResponse {
  success: boolean;
  message: string;
  expires_at?: string;
  connection_health: string;
}

export interface MLErrorResponse {
  error: string;
  error_description: string;
  error_uri?: string;
  status_code: number;
  request_id?: string;
}

export interface MLManagerAccountError {
  error: string;
  error_description: string;
  guidance: string;
  status_code: number;
}

export interface MLRateLimitResponse {
  error: string;
  error_description: string;
  retry_after: number;
  status_code: number;
}

// ML Site configuration
export interface MLSiteConfig {
  id: string;
  name: string;
  country: string;
  domain: string;
  currency: string;
  flag: string;
}

export const ML_SITES: Record<string, MLSiteConfig> = {
  MLA: {
    id: 'MLA',
    name: 'MercadoLibre Argentina',
    country: 'Argentina',
    domain: 'mercadolibre.com.ar',
    currency: 'ARS',
    flag: '🇦🇷',
  },
  MLM: {
    id: 'MLM',
    name: 'MercadoLibre México',
    country: 'México',
    domain: 'mercadolibre.com.mx',
    currency: 'MXN',
    flag: '🇲🇽',
  },
  MBL: {
    id: 'MBL',
    name: 'MercadoLivre Brasil',
    country: 'Brasil',
    domain: 'mercadolibre.com.br',
    currency: 'BRL',
    flag: '🇧🇷',
  },
  MLC: {
    id: 'MLC',
    name: 'MercadoLibre Chile',
    country: 'Chile',
    domain: 'mercadolibre.cl',
    currency: 'CLP',
    flag: '🇨🇱',
  },
  MCO: {
    id: 'MCO',
    name: 'MercadoLibre Colombia',
    country: 'Colombia',
    domain: 'mercadolibre.com.co',
    currency: 'COP',
    flag: '🇨🇴',
  },
};

// Connection health helpers
export const CONNECTION_HEALTH_LABELS: Record<string, string> = {
  healthy: 'Connected',
  expired: 'Expired',
  invalid: 'Invalid',
  disconnected: 'Not Connected',
};

export const CONNECTION_HEALTH_COLORS: Record<string, string> = {
  healthy: 'success',
  expired: 'warning',
  invalid: 'error',
  disconnected: 'neutral',
};

// OAuth flow states
export type OAuthFlowState =
  | 'idle'
  | 'initiating'
  | 'authorizing'
  | 'completing'
  | 'completed'
  | 'error';

export interface OAuthFlowContext {
  state: OAuthFlowState;
  error?: string;
  redirectUri?: string;
  siteId?: string;
}
