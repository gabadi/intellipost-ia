<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';

  let isChecking = true;

  onMount(() => {
    // Initialize auth store
    authStore.init();

    // Check if user is already authenticated
    const unsubscribe = authStore.subscribe((state) => {
      if (state.isAuthenticated) {
        // Redirect to dashboard if already logged in
        goto('/dashboard');
      } else {
        isChecking = false;
      }
    });

    return unsubscribe;
  });
</script>

<svelte:head>
  <title>IntelliPost AI - Intelligent Social Media Posting</title>
</svelte:head>

{#if isChecking}
  <div class="loading-container">
    <div class="loading-spinner"></div>
    <p>Checking authentication...</p>
  </div>
{:else}
  <div class="container">
    <div class="landing-container">
      <header class="landing-header">
        <h1 class="landing-title">IntelliPost AI</h1>
        <p class="landing-subtitle">Intelligent Social Media Posting Platform</p>
        <p class="landing-description">
          Create compelling product listings with AI-powered content generation and seamless MercadoLibre integration.
        </p>
      </header>

      <div class="landing-actions">
        <a href="/auth/login" class="btn btn--primary btn--lg">
          Get Started
        </a>
        <a href="/auth/register" class="btn btn--secondary btn--lg">
          Create Account
        </a>
      </div>

      <div class="landing-features">
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3 class="feature-title">AI-Powered Content</h3>
          <p class="feature-description">
            Generate compelling product descriptions and social media posts automatically
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">📦</div>
          <h3 class="feature-title">Product Management</h3>
          <p class="feature-description">
            Organize and manage your product listings with intuitive tools
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🚀</div>
          <h3 class="feature-title">MercadoLibre Integration</h3>
          <p class="feature-description">
            Seamlessly publish to MercadoLibre with automated listing optimization
          </p>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 1rem;
  }

  .loading-container p {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .landing-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: var(--space-8) var(--space-4);
    text-align: center;
  }

  .landing-header {
    max-width: 600px;
    margin-bottom: var(--space-12);
  }

  .landing-title {
    font-size: var(--text-4xl);
    font-weight: 800;
    color: var(--color-text-primary);
    margin-bottom: var(--space-4);
  }

  .landing-subtitle {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-text-secondary);
    margin-bottom: var(--space-6);
  }

  .landing-description {
    font-size: var(--text-lg);
    color: var(--color-text-muted);
    line-height: 1.6;
  }

  .landing-actions {
    display: flex;
    gap: var(--space-4);
    margin-bottom: var(--space-16);
    flex-wrap: wrap;
    justify-content: center;
  }

  .landing-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--space-8);
    max-width: 1000px;
  }

  .feature-card {
    padding: var(--space-6);
    border: 1px solid var(--color-border-muted);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
  }

  .feature-icon {
    font-size: 3rem;
    margin-bottom: var(--space-4);
  }

  .feature-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--space-2);
  }

  .feature-description {
    color: var(--color-text-muted);
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    .landing-title {
      font-size: var(--text-3xl);
    }

    .landing-subtitle {
      font-size: var(--text-lg);
    }

    .landing-description {
      font-size: var(--text-base);
    }

    .landing-actions {
      flex-direction: column;
      width: 100%;
      max-width: 300px;
    }

    .landing-features {
      grid-template-columns: 1fr;
    }
  }
</style>
