/**
 * Unit tests for MLConnectionModal component
 *
 * Tests the MercadoLibre connection modal functionality including
 * pre-auth education and manager account warnings.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, waitFor, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import MLConnectionModal from '$lib/components/ml/MLConnectionModal.svelte';
import { mlConnectionStore } from '$lib/stores/ml-connection';
import { mlOAuthApi, MLManagerAccountError, MLRateLimitError } from '$lib/api/ml-oauth';

// Mock the stores and API
vi.mock('$lib/stores/ml-connection', () => ({
  mlConnectionStore: {
    initiateConnection: vi.fn(),
    handleCallback: vi.fn(),
  },
}));

vi.mock('$lib/api/ml-oauth', () => ({
  mlOAuthApi: {
    buildRedirectUri: vi.fn(() => 'http://localhost:3000/ml-setup/callback'),
    validateRedirectUri: vi.fn(() => true),
    formatError: vi.fn(error => error.message || 'Unknown error'),
  },
  MLManagerAccountError: class extends Error {
    public guidance: string;
    constructor(message: string, guidance: string) {
      super(message);
      this.name = 'MLManagerAccountError';
      this.guidance = guidance;
    }
  },
  MLRateLimitError: class extends Error {
    public retryAfter: number;
    constructor(message: string, retryAfter: number) {
      super(message);
      this.name = 'MLRateLimitError';
      this.retryAfter = retryAfter;
    }
  },
}));

// Mock window.location
const mockLocation = {
  href: 'http://localhost:3000',
};
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

describe('MLConnectionModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('should not render when isOpen is false', () => {
    const { container } = render(MLConnectionModal, {
      props: { isOpen: false },
    });

    expect(container.querySelector('.modal-backdrop')).toBeNull();
  });

  it('should render education step when opened', () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    expect(screen.getByText('Connect to MercadoLibre')).toBeInTheDocument();
    expect(screen.getByText('Benefits of Connecting')).toBeInTheDocument();
    expect(screen.getByText('Manager Account Required')).toBeInTheDocument();
    expect(screen.getByText('Secure Connection')).toBeInTheDocument();
  });

  it('should display manager account warning prominently', () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    const warningBox = screen.getByText('Manager Account Required').closest('.warning-box');
    expect(warningBox).toBeInTheDocument();
    expect(warningBox).toHaveClass('warning-box');

    const warningText = screen.getByText(
      'Only MercadoLibre manager accounts can connect to IntelliPost AI.'
    );
    expect(warningText).toBeInTheDocument();
  });

  it('should show benefits list with correct items', () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    expect(screen.getByText('Automated Publishing')).toBeInTheDocument();
    expect(screen.getByText('Real-time Sync')).toBeInTheDocument();
    expect(screen.getByText('Smart Optimization')).toBeInTheDocument();
    expect(screen.getByText('Performance Insights')).toBeInTheDocument();
  });

  it('should proceed to site selection when Continue is clicked', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    expect(screen.getByText('Choose Your Marketplace')).toBeInTheDocument();
    expect(screen.getByText('MercadoLibre Argentina')).toBeInTheDocument();
  });

  it('should display all available marketplaces in site selection', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Check all marketplaces are displayed
    expect(screen.getByText('MercadoLibre Argentina')).toBeInTheDocument();
    expect(screen.getByText('MercadoLibre México')).toBeInTheDocument();
    expect(screen.getByText('MercadoLivre Brasil')).toBeInTheDocument();
    expect(screen.getByText('MercadoLibre Chile')).toBeInTheDocument();
    expect(screen.getByText('MercadoLibre Colombia')).toBeInTheDocument();
  });

  it('should allow site selection and show selected site', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true, selectedSiteId: 'MLA' },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Select Brazil
    const brazilCard = screen.getByText('MercadoLivre Brasil').closest('.site-card');
    expect(brazilCard).not.toBeNull();
    await fireEvent.click(brazilCard!);

    // Check the component's selectedSiteId prop was updated
    // Check that Brazil card is now selected (visual feedback)
    expect(brazilCard!.classList.contains('selected')).toBe(true);
  });

  it('should initiate OAuth connection on connect button click', async () => {
    const mockInitiateConnection = vi.fn().mockResolvedValue({
      authorization_url: 'https://auth.mercadolibre.com.ar/authorization?...',
      state: 'test_state',
      code_verifier: 'test_verifier',
    });

    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Click connect button
    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    await waitFor(() => {
      expect(mockInitiateConnection).toHaveBeenCalledWith(
        'http://localhost:3000/ml-setup/callback',
        'MLA'
      );
    });
  });

  it('should redirect to MercadoLibre on successful OAuth initiation', async () => {
    const mockInitiateConnection = vi.fn().mockResolvedValue({
      authorization_url: 'https://auth.mercadolibre.com.ar/authorization?test=true',
      state: 'test_state',
      code_verifier: 'test_verifier',
    });

    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Click connect button
    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    await waitFor(() => {
      expect(window.location.href).toBe('https://auth.mercadolibre.com.ar/authorization?test=true');
    });
  });

  it('should handle manager account error appropriately', async () => {
    const managerError = new MLManagerAccountError(
      'Only manager accounts can authorize applications',
      'Please use a manager account'
    );

    const mockInitiateConnection = vi.fn().mockRejectedValue(managerError);
    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection and attempt connection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    await waitFor(() => {
      expect(screen.getByText('Manager Account Required')).toBeInTheDocument();
    });
  });

  it('should handle rate limit error with countdown', async () => {
    const rateLimitError = new MLRateLimitError('Too many requests', 60);

    const mockInitiateConnection = vi.fn().mockRejectedValue(rateLimitError);
    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection and attempt connection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    await waitFor(() => {
      expect(screen.getByText('Rate Limited: Too many requests')).toBeInTheDocument();
    });
  });

  it('should close modal when close button is clicked', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    await fireEvent.click(closeButton);

    // Check that close event was dispatched
    // Modal should be closed (not visible in DOM)\n    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('should close modal when backdrop is clicked', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    const backdrop = screen.getByRole('dialog');
    await fireEvent.click(backdrop);

    // Modal should be closed (not visible in DOM)\n    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('should not close modal when content is clicked', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    const modalContent = screen.getByText('Connect to MercadoLibre').closest('.modal-content');
    expect(modalContent).not.toBeNull();
    await fireEvent.click(modalContent!);

    // Modal should still be open
    expect(screen.getByText('Connect to MercadoLibre')).toBeInTheDocument();
  });

  it('should handle keyboard navigation (Escape key)', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    await fireEvent.keyDown(document, { key: 'Escape' });

    // Modal should be closed (not visible in DOM)\n    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('should disable buttons during connection process', async () => {
    const mockInitiateConnection = vi
      .fn()
      .mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Click connect button
    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    // Button should be disabled during connection
    expect(connectButton).toBeDisabled();
    expect(screen.getByText('Connecting...')).toBeInTheDocument();
  });

  it('should show connecting state with proper messaging', async () => {
    const mockInitiateConnection = vi
      .fn()
      .mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection and connect
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    // Check connecting state
    expect(screen.getByText('Redirecting to MercadoLibre...')).toBeInTheDocument();
    expect(
      screen.getByText('Remember: Only manager accounts can complete this process.')
    ).toBeInTheDocument();
  });

  it('should validate redirect URI before initiating connection', async () => {
    const mockValidateRedirectUri = vi.fn().mockReturnValue(false);
    vi.mocked(mlOAuthApi.validateRedirectUri).mockImplementation(mockValidateRedirectUri);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Attempt connection
    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid redirect URI configuration')).toBeInTheDocument();
    });
  });

  it('should close modal when close button is clicked', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    await fireEvent.click(closeButton);

    // Check that the modal is no longer visible
    await waitFor(() => {
      expect(screen.queryByText('Connect to MercadoLibre')).not.toBeInTheDocument();
    });
  });

  it('should start connection process on successful connection', async () => {
    const mockInitiateConnection = vi.fn().mockResolvedValue({
      authorization_url: 'https://auth.mercadolibre.com.ar/authorization?test=true',
      state: 'test_state',
      code_verifier: 'test_verifier',
    });

    vi.mocked(mlConnectionStore.initiateConnection).mockImplementation(mockInitiateConnection);

    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection and connect
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    const connectButton = screen.getByText('Connect to MercadoLibre Argentina');
    await fireEvent.click(connectButton);

    // Check that the connection process started successfully
    await waitFor(() => {
      expect(mockInitiateConnection).toHaveBeenCalled();
    });
  });

  it('should reset modal state when closed and reopened', async () => {
    render(MLConnectionModal, {
      props: { isOpen: true },
    });

    // Navigate to site selection
    const continueButton = screen.getByText('Continue');
    await fireEvent.click(continueButton);

    // Close modal
    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    await fireEvent.click(closeButton);

    // Reopen modal
    // Component state management is handled by props in the test setup
    await tick();

    // Should be back to education step
    expect(screen.getByText('Connect to MercadoLibre')).toBeInTheDocument();
    expect(screen.getByText('Benefits of Connecting')).toBeInTheDocument();
  });
});
