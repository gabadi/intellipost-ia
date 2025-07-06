<script lang="ts">
	/**
	 * MercadoLibre Connection Modal
	 * 
	 * Modal component for initiating ML OAuth connection with pre-auth education
	 * and manager account warning as specified in the story requirements.
	 */
	
	import { createEventDispatcher, onMount } from 'svelte';
	import { mlConnectionStore } from '$lib/stores/ml-connection';
	import { mlOAuthApi, MLManagerAccountError, MLRateLimitError } from '$lib/api/ml-oauth';
	import type { MLSiteConfig } from '$lib/types/ml-connection';
	import { ML_SITES } from '$lib/types/ml-connection';

	// Component props
	export let isOpen = false;
	export let selectedSiteId = 'MLA';

	// Component state
	let isConnecting = false;
	let error: string | null = null;
	let currentStep: 'education' | 'site-selection' | 'connecting' = 'education';
	let retryDelay = 0;
	let retryTimer: NodeJS.Timeout | null = null;

	// Event dispatcher
	const dispatch = createEventDispatcher<{
		close: void;
		connected: { siteId: string; nickname?: string };
	}>();

	// Reactive values
	$: selectedSite = ML_SITES[selectedSiteId];
	$: canProceed = !isConnecting && !retryDelay;

	// Cleanup on unmount
	onMount(() => {
		return () => {
			if (retryTimer) {
				clearInterval(retryTimer);
			}
		};
	});

	/**
	 * Handle modal close
	 */
	function handleClose() {
		if (!isConnecting) {
			resetModal();
			dispatch('close');
		}
	}

	/**
	 * Reset modal to initial state
	 */
	function resetModal() {
		currentStep = 'education';
		error = null;
		isConnecting = false;
		retryDelay = 0;
		if (retryTimer) {
			clearInterval(retryTimer);
			retryTimer = null;
		}
	}

	/**
	 * Proceed to site selection
	 */
	function proceedToSiteSelection() {
		currentStep = 'site-selection';
		error = null;
	}

	/**
	 * Start retry countdown
	 */
	function startRetryCountdown(seconds: number) {
		retryDelay = seconds;
		retryTimer = setInterval(() => {
			retryDelay--;
			if (retryDelay <= 0) {
				clearInterval(retryTimer!);
				retryTimer = null;
			}
		}, 1000);
	}

	/**
	 * Initiate OAuth connection
	 */
	async function initiateConnection() {
		if (!canProceed) return;

		currentStep = 'connecting';
		isConnecting = true;
		error = null;

		try {
			// Build redirect URI
			const redirectUri = mlOAuthApi.buildRedirectUri('/ml-setup/callback');
			
			// Validate redirect URI
			if (!mlOAuthApi.validateRedirectUri(redirectUri)) {
				throw new Error('Invalid redirect URI configuration');
			}

			// Initiate OAuth flow
			const response = await mlConnectionStore.initiateConnection(redirectUri, selectedSiteId);
			
			// Redirect to MercadoLibre for authorization
			window.location.href = response.authorization_url;
			
		} catch (err) {
			isConnecting = false;
			currentStep = 'site-selection';
			
			if (err instanceof MLManagerAccountError) {
				error = `Manager Account Required: ${err.message}\n\n${err.guidance}`;
			} else if (err instanceof MLRateLimitError) {
				error = `Rate Limited: ${err.message}`;
				startRetryCountdown(err.retryAfter);
			} else {
				error = mlOAuthApi.formatError(err);
			}
		}
	}

	/**
	 * Handle site selection
	 */
	function selectSite(siteId: string) {
		selectedSiteId = siteId;
	}

	/**
	 * Handle keyboard navigation
	 */
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && !isConnecting) {
			handleClose();
		}
	}
</script>

<!-- Modal backdrop -->
{#if isOpen}
	<div 
		class="modal-backdrop"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="dialog"
		aria-modal="true"
		aria-labelledby="modal-title"
		tabindex="-1"
	>
		<!-- Modal content -->
		<div 
			class="modal-content" 
			on:click|stopPropagation
			role="document"
		>
			<!-- Header -->
			<div class="modal-header">
				<h2 id="modal-title" class="modal-title">
					{#if currentStep === 'education'}
						Connect to MercadoLibre
					{:else if currentStep === 'site-selection'}
						Choose Your Marketplace
					{:else}
						Connecting...
					{/if}
				</h2>
				
				{#if !isConnecting}
					<button 
						class="close-button"
						on:click={handleClose}
						aria-label="Close modal"
					>
						×
					</button>
				{/if}
			</div>

			<!-- Content -->
			<div class="modal-body">
				{#if currentStep === 'education'}
					<!-- Pre-auth education step -->
					<div class="education-content">
						<div class="benefits-section">
							<h3>Benefits of Connecting</h3>
							<ul class="benefits-list">
								<li>
									<span class="benefit-icon">🚀</span>
									<div>
										<strong>Automated Publishing</strong>
										<p>Publish generated listings directly to MercadoLibre</p>
									</div>
								</li>
								<li>
									<span class="benefit-icon">⚡</span>
									<div>
										<strong>Real-time Sync</strong>
										<p>Keep your listings synchronized across platforms</p>
									</div>
								</li>
								<li>
									<span class="benefit-icon">🎯</span>
									<div>
										<strong>Smart Optimization</strong>
										<p>AI-optimized titles and descriptions for better visibility</p>
									</div>
								</li>
								<li>
									<span class="benefit-icon">📊</span>
									<div>
										<strong>Performance Insights</strong>
										<p>Track listing performance and optimization suggestions</p>
									</div>
								</li>
							</ul>
						</div>

						<!-- CRITICAL: Manager account warning -->
						<div class="warning-section">
							<div class="warning-box">
								<span class="warning-icon">⚠️</span>
								<div class="warning-content">
									<h4>Manager Account Required</h4>
									<p>
										<strong>Only MercadoLibre manager accounts can connect to IntelliPost AI.</strong>
										Collaborator accounts cannot authorize applications.
									</p>
									<p class="warning-detail">
										If you're using a collaborator account, please contact your account manager 
										to complete this connection.
									</p>
								</div>
							</div>
						</div>

						<!-- Security information -->
						<div class="security-section">
							<h4>Secure Connection</h4>
							<p class="security-text">
								This connection uses OAuth 2.0 with PKCE security. Your MercadoLibre 
								credentials are never stored by IntelliPost AI. You can revoke access 
								at any time from your MercadoLibre account settings.
							</p>
						</div>

						<!-- Action buttons -->
						<div class="action-buttons">
							<button 
								class="button button-secondary"
								on:click={handleClose}
								disabled={isConnecting}
							>
								Cancel
							</button>
							<button 
								class="button button-primary"
								on:click={proceedToSiteSelection}
								disabled={isConnecting}
							>
								Continue
							</button>
						</div>
					</div>

				{:else if currentStep === 'site-selection'}
					<!-- Site selection step -->
					<div class="site-selection-content">
						<p class="selection-description">
							Choose your MercadoLibre marketplace to connect with IntelliPost AI:
						</p>

						<div class="sites-grid">
							{#each Object.values(ML_SITES) as site}
								<button
									class="site-card {site.id === selectedSiteId ? 'selected' : ''}"
									on:click={() => selectSite(site.id)}
									disabled={isConnecting}
								>
									<span class="site-flag">{site.flag}</span>
									<div class="site-info">
										<h4 class="site-name">{site.name}</h4>
										<p class="site-country">{site.country}</p>
										<p class="site-domain">{site.domain}</p>
									</div>
									{#if site.id === selectedSiteId}
										<span class="check-icon">✓</span>
									{/if}
								</button>
							{/each}
						</div>
						
						<!-- Error display -->
						{#if error}
							<div class="error-section">
								<div class="error-box">
									<span class="error-icon">❌</span>
									<div class="error-content">
										<p class="error-message">{error}</p>
										{#if retryDelay > 0}
											<p class="retry-message">
												You can try again in {retryDelay} seconds.
											</p>
										{/if}
									</div>
								</div>
							</div>
						{/if}

						<!-- Selected site info -->
						{#if selectedSite}
							<div class="selected-site-info">
								<h4>Selected Marketplace:</h4>
								<div class="site-details">
									<span class="site-flag-large">{selectedSite.flag}</span>
									<div>
										<p class="site-name-large">{selectedSite.name}</p>
										<p class="site-domain-small">{selectedSite.domain}</p>
									</div>
								</div>
							</div>
						{/if}

						<!-- Action buttons -->
						<div class="action-buttons">
							<button 
								class="button button-secondary"
								on:click={() => currentStep = 'education'}
								disabled={isConnecting}
							>
								Back
							</button>
							<button 
								class="button button-primary"
								on:click={initiateConnection}
								disabled={!canProceed}
							>
								{#if isConnecting}
									Connecting...
								{:else if retryDelay > 0}
									Wait {retryDelay}s
								{:else}
									Connect to {selectedSite?.name}
								{/if}
							</button>
						</div>
					</div>

				{:else if currentStep === 'connecting'}
					<!-- Connecting step -->
					<div class="connecting-content">
						<div class="loading-spinner"></div>
						<h3>Redirecting to MercadoLibre...</h3>
						<p>
							You will be redirected to MercadoLibre to authorize the connection.
							Please complete the authorization process there.
						</p>
						<p class="connecting-note">
							<strong>Remember:</strong> Only manager accounts can complete this process.
						</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
	}

	.modal-content {
		background: white;
		border-radius: 12px;
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		animation: modalAppear 0.3s ease-out;
	}

	@keyframes modalAppear {
		from {
			opacity: 0;
			transform: scale(0.9) translateY(-20px);
		}
		to {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
	}

	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 24px 24px 0 24px;
		border-bottom: 1px solid #e5e7eb;
		margin-bottom: 24px;
	}

	.modal-title {
		font-size: 1.5rem;
		font-weight: 600;
		margin: 0;
		color: #111827;
	}

	.close-button {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		padding: 4px;
		color: #6b7280;
		border-radius: 4px;
		transition: all 0.2s;
	}

	.close-button:hover {
		color: #374151;
		background-color: #f3f4f6;
	}

	.modal-body {
		padding: 0 24px 24px 24px;
	}

	/* Education content styles */
	.education-content > * + * {
		margin-top: 24px;
	}

	.benefits-section h3 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 16px;
		color: #111827;
	}

	.benefits-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.benefits-list li {
		display: flex;
		align-items: flex-start;
		gap: 12px;
		padding: 16px;
		background-color: #f9fafb;
		border-radius: 8px;
		border-left: 4px solid #3b82f6;
		margin-bottom: 16px;
	}

	.benefit-icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}

	.benefits-list li strong {
		color: #111827;
		font-weight: 600;
	}

	.benefits-list li p {
		margin: 4px 0 0 0;
		color: #6b7280;
		font-size: 0.875rem;
	}

	/* Warning section styles */
	.warning-section {
		margin: 24px 0;
	}

	.warning-box {
		display: flex;
		gap: 12px;
		padding: 16px;
		background-color: #fef3c7;
		border: 1px solid #f59e0b;
		border-radius: 8px;
	}

	.warning-icon {
		font-size: 1.25rem;
		flex-shrink: 0;
	}

	.warning-content h4 {
		margin: 0 0 8px 0;
		font-weight: 600;
		color: #92400e;
	}

	.warning-content p {
		margin: 0 0 8px 0;
		color: #92400e;
		font-size: 0.875rem;
	}

	.warning-detail {
		font-style: italic;
	}

	/* Security section styles */
	.security-section {
		margin: 24px 0;
	}

	.security-section h4 {
		margin: 0 0 8px 0;
		font-weight: 600;
		color: #111827;
	}

	.security-text {
		color: #6b7280;
		font-size: 0.875rem;
		line-height: 1.5;
		margin: 0;
	}

	/* Site selection styles */
	.selection-description {
		margin-bottom: 24px;
		color: #6b7280;
	}

	.sites-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 16px;
		margin-bottom: 24px;
	}

	.site-card {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 16px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		background: white;
		cursor: pointer;
		transition: all 0.2s;
		text-align: left;
	}

	.site-card:hover {
		border-color: #3b82f6;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.site-card.selected {
		border-color: #3b82f6;
		background-color: #eff6ff;
	}

	.site-flag {
		font-size: 2rem;
	}

	.site-info h4 {
		margin: 0 0 4px 0;
		font-weight: 600;
		color: #111827;
	}

	.site-info p {
		margin: 0;
		font-size: 0.875rem;
		color: #6b7280;
	}

	.check-icon {
		margin-left: auto;
		color: #3b82f6;
		font-weight: bold;
	}

	/* Selected site info */
	.selected-site-info {
		margin: 24px 0;
		padding: 16px;
		background-color: #eff6ff;
		border-radius: 8px;
	}

	.selected-site-info h4 {
		margin: 0 0 12px 0;
		font-weight: 600;
		color: #111827;
	}

	.site-details {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.site-flag-large {
		font-size: 2rem;
	}

	.site-name-large {
		margin: 0;
		font-weight: 600;
		color: #111827;
	}

	.site-domain-small {
		margin: 4px 0 0 0;
		font-size: 0.875rem;
		color: #6b7280;
	}

	/* Error styles */
	.error-section {
		margin: 16px 0;
	}

	.error-box {
		display: flex;
		gap: 12px;
		padding: 16px;
		background-color: #fef2f2;
		border: 1px solid #ef4444;
		border-radius: 8px;
	}

	.error-icon {
		flex-shrink: 0;
	}

	.error-message {
		margin: 0;
		color: #dc2626;
		font-size: 0.875rem;
		white-space: pre-line;
	}

	.retry-message {
		margin: 8px 0 0 0;
		color: #dc2626;
		font-size: 0.875rem;
		font-style: italic;
	}

	/* Connecting styles */
	.connecting-content {
		text-align: center;
		padding: 32px 0;
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #e5e7eb;
		border-left: 4px solid #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 24px auto;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.connecting-content h3 {
		margin: 0 0 16px 0;
		color: #111827;
	}

	.connecting-content p {
		margin: 0 0 16px 0;
		color: #6b7280;
	}

	.connecting-note {
		font-weight: 600;
		color: #92400e;
	}

	/* Action buttons */
	.action-buttons {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
		margin-top: 24px;
	}

	.button {
		padding: 12px 24px;
		border: none;
		border-radius: 6px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 100px;
	}

	.button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.button-primary {
		background-color: #3b82f6;
		color: white;
	}

	.button-primary:hover:not(:disabled) {
		background-color: #2563eb;
	}

	.button-secondary {
		background-color: #f3f4f6;
		color: #374151;
		border: 1px solid #d1d5db;
	}

	.button-secondary:hover:not(:disabled) {
		background-color: #e5e7eb;
	}

	/* Responsive design */
	@media (max-width: 640px) {
		.modal-content {
			width: 95%;
			margin: 20px;
		}
		
		.sites-grid {
			grid-template-columns: 1fr;
		}
		
		.action-buttons {
			flex-direction: column;
		}
		
		.button {
			width: 100%;
		}
	}
</style>