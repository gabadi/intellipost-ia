# IntelliPost AI - Frontend Architecture

## Document Information
- **Project:** IntelliPost AI MVP
- **Architect:** Winston (Fred)
- **Date:** June 22, 2025
- **Framework:** SvelteKit + TypeScript
- **Focus:** Mobile-Complete Architecture

---

## Frontend Architecture Overview

### Mobile-First Design Philosophy
```yaml
Core Principle: Mobile-Complete MVP
  - Primary: Mobile 320px-767px (one-hand use)
  - Secondary: Tablet 768px-1023px (larger touch targets)
  - Future: Desktop 1024px+ (Post-MVP)

Performance Targets:
  - App Load: <3 seconds on 3G
  - UI Response: <100ms for all interactions
  - Photo Upload: <5 seconds for multiple photos
  - End-to-End Flow: <60 seconds photo → published
```

### SvelteKit Application Structure
```
src/
├── app.html                    # App shell with PWA meta
├── routes/
│   ├── +layout.svelte         # Global layout with navigation
│   ├── +layout.ts             # Global layout data loading
│   ├── +page.svelte           # Dashboard (product list)
│   ├── products/
│   │   ├── new/
│   │   │   └── +page.svelte   # Photo + Prompt input (mobile-first)
│   │   ├── [id]/
│   │   │   ├── +page.svelte   # Product detail view
│   │   │   ├── +page.ts       # Product data loading
│   │   │   ├── review/
│   │   │   │   └── +page.svelte  # Balanced Review flow
│   │   │   └── edit/
│   │   │       └── +page.svelte  # Edit interface
│   │   └── +layout.svelte     # Product-specific layout
│   ├── ml-setup/
│   │   └── +page.svelte       # MercadoLibre OAuth setup
│   └── api/                   # API routes (if needed)
├── lib/
│   ├── components/            # Reusable UI components
│   │   ├── core/             # Core mobile components
│   │   ├── product/          # Product-specific components
│   │   ├── ui/               # Generic UI components
│   │   └── forms/            # Form components
│   ├── stores/               # Svelte stores for state
│   │   ├── auth.ts           # Authentication state
│   │   ├── products.ts       # Product management
│   │   ├── realtime.ts       # WebSocket management
│   │   └── ui.ts             # UI state (loading, errors)
│   ├── api/                  # API client functions
│   │   ├── products.ts       # Product API calls
│   │   ├── ml.ts             # MercadoLibre API calls
│   │   └── client.ts         # Base API client
│   ├── utils/                # Helper functions
│   │   ├── image.ts          # Image compression/processing
│   │   ├── validation.ts     # Form validation
│   │   └── formatting.ts     # Data formatting
│   └── types/                # TypeScript definitions
│       ├── api.ts            # API response types
│       ├── product.ts        # Product entity types
│       └── ui.ts             # UI component types
├── static/                   # Static assets
└── service-worker.js         # PWA service worker (future)
```

---

## Core Mobile Components

### 1. Photo Collection Component
**Purpose:** Multi-photo capture optimized for mobile

```svelte
<!-- PhotoCollectionComponent.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { imageCompression } from '$lib/utils/image';

  export let images: ImageData[] = [];
  export let maxImages: number = 10;

  const dispatch = createEventDispatcher<{
    imagesChange: ImageData[];
    uploadStart: void;
    uploadComplete: void;
  }>();

  let fileInput: HTMLInputElement;
  let isUploading = false;

  // Mobile camera access
  async function capturePhoto() {
    fileInput.click();
  }

  // Handle file selection with compression
  async function handleFileSelect(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (!files) return;

    isUploading = true;
    dispatch('uploadStart');

    try {
      const compressedImages = await Promise.all(
        Array.from(files).map(async (file) => {
          const compressed = await imageCompression(file, {
            maxSizeMB: 2,
            maxWidthOrHeight: 1920,
            useWebWorker: true
          });
          return {
            id: crypto.randomUUID(),
            file: compressed,
            url: URL.createObjectURL(compressed),
            isPrimary: images.length === 0
          };
        })
      );

      images = [...images, ...compressedImages];
      dispatch('imagesChange', images);
    } finally {
      isUploading = false;
      dispatch('uploadComplete');
    }
  }

  function removeImage(imageId: string) {
    images = images.filter(img => img.id !== imageId);
    dispatch('imagesChange', images);
  }

  function setPrimary(imageId: string) {
    images = images.map(img => ({
      ...img,
      isPrimary: img.id === imageId
    }));
    dispatch('imagesChange', images);
  }
</script>

<!-- Mobile-optimized UI -->
<div class="photo-collection">
  <!-- Hidden file input for camera access -->
  <input
    bind:this={fileInput}
    type="file"
    accept="image/*"
    multiple
    capture="environment"
    on:change={handleFileSelect}
    style="display: none;"
  />

  <!-- Camera button - prominent mobile placement -->
  <button
    class="camera-btn"
    on:click={capturePhoto}
    disabled={isUploading || images.length >= maxImages}
  >
    {#if isUploading}
      <LoadingSpinner size="24" />
      Procesando...
    {:else}
      📷 Tomar Fotos
    {/if}
  </button>

  <!-- Image grid - mobile touch-optimized -->
  {#if images.length > 0}
    <div class="image-grid">
      {#each images as image (image.id)}
        <div class="image-card" class:primary={image.isPrimary}>
          <img src={image.url} alt="Product" />

          <!-- Mobile touch controls -->
          <div class="image-controls">
            <button
              class="btn-small"
              on:click={() => setPrimary(image.id)}
              disabled={image.isPrimary}
            >
              {image.isPrimary ? '⭐' : '☆'}
            </button>
            <button
              class="btn-small btn-danger"
              on:click={() => removeImage(image.id)}
            >
              🗑️
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Photo count indicator -->
  <div class="photo-count">
    {images.length} foto{images.length !== 1 ? 's' : ''}
    {#if maxImages > 0} / {maxImages}{/if}
  </div>
</div>

<style>
  .photo-collection {
    width: 100%;
    padding: 1rem;
  }

  .camera-btn {
    width: 100%;
    padding: 1rem;
    font-size: 1.2rem;
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    min-height: 56px; /* 44px minimum touch target + padding */
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .image-card {
    position: relative;
    aspect-ratio: 1;
    border-radius: 8px;
    overflow: hidden;
    border: 2px solid transparent;
  }

  .image-card.primary {
    border-color: #059669;
  }

  .image-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .image-controls {
    position: absolute;
    top: 0.25rem;
    right: 0.25rem;
    display: flex;
    gap: 0.25rem;
  }

  .btn-small {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .photo-count {
    text-align: center;
    margin-top: 0.5rem;
    color: #6B7280;
    font-size: 0.9rem;
  }
</style>
```

### 2. Prompt Input Component
**Purpose:** Required user description with mobile optimization

```svelte
<!-- PromptInputComponent.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let value = '';
  export let placeholder = 'Describe your item (brand, size, condition...)';
  export let minLength = 10;
  export let maxLength = 500;
  export let required = true;
  export let disabled = false;

  const dispatch = createEventDispatcher<{
    change: string;
    regenerate: string;
  }>();

  let textArea: HTMLTextAreaElement;
  let isValid = false;

  $: isValid = value.trim().length >= minLength;
  $: remainingChars = maxLength - value.length;

  function handleInput() {
    dispatch('change', value);
    autoResize();
  }

  function autoResize() {
    if (textArea) {
      textArea.style.height = 'auto';
      textArea.style.height = textArea.scrollHeight + 'px';
    }
  }

  function handleRegenerate() {
    if (isValid) {
      dispatch('regenerate', value);
    }
  }
</script>

<div class="prompt-input">
  <label for="prompt" class="prompt-label">
    Describe tu producto
    {#if required}<span class="required">*</span>{/if}
  </label>

  <textarea
    bind:this={textArea}
    bind:value
    id="prompt"
    {placeholder}
    {disabled}
    maxlength={maxLength}
    class="prompt-textarea"
    class:valid={isValid}
    class:invalid={required && value.length > 0 && !isValid}
    on:input={handleInput}
    rows="3"
  ></textarea>

  <!-- Mobile-friendly validation feedback -->
  <div class="prompt-meta">
    <div class="validation-info">
      {#if required && value.length > 0 && !isValid}
        <span class="error">Mínimo {minLength} caracteres</span>
      {:else if isValid}
        <span class="success">✓ Importante para precisión</span>
      {:else}
        <span class="hint">Importante para precisión del AI</span>
      {/if}
    </div>

    <div class="char-count" class:warning={remainingChars < 50}>
      {remainingChars}
    </div>
  </div>

  <!-- Regenerate button for edit mode -->
  <slot name="regenerate-button">
    <!-- Will be provided in edit mode -->
  </slot>
</div>

<style>
  .prompt-input {
    width: 100%;
    margin-bottom: 1rem;
  }

  .prompt-label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #374151;
  }

  .required {
    color: #DC2626;
  }

  .prompt-textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #D1D5DB;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: none;
    min-height: 80px;
    line-height: 1.5;
  }

  .prompt-textarea:focus {
    outline: none;
    border-color: #2563EB;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  .prompt-textarea.valid {
    border-color: #059669;
  }

  .prompt-textarea.invalid {
    border-color: #DC2626;
  }

  .prompt-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }

  .error { color: #DC2626; }
  .success { color: #059669; }
  .hint { color: #6B7280; }
  .warning { color: #D97706; }

  .char-count {
    color: #6B7280;
    font-variant-numeric: tabular-nums;
  }

  .char-count.warning {
    color: #D97706;
    font-weight: 600;
  }
</style>
```

### 3. Processing Spinner Component
**Purpose:** Real-time AI processing feedback

```svelte
<!-- ProcessingSpinner.svelte -->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { realtimeStore } from '$lib/stores/realtime';

  export let productId: string;
  export let estimatedSeconds = 15;

  let progress = 0;
  let message = 'Analyzing your photos...';
  let elapsedSeconds = 0;
  let interval: number;

  // Subscribe to real-time updates
  const unsubscribe = realtimeStore.subscribe(productId, (update) => {
    if (update.type === 'status_change') {
      progress = update.data.progress || 0;
      message = update.data.message || message;
    }
  });

  onMount(() => {
    // Progress simulation if no real-time updates
    interval = setInterval(() => {
      elapsedSeconds += 1;

      // Simulate progress curve (fast start, slow finish)
      const progressPercent = Math.min(
        (elapsedSeconds / estimatedSeconds) * 80 +
        Math.random() * 10,
        95
      );

      if (progress === 0) {
        progress = progressPercent;
      }
    }, 1000);
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
    unsubscribe();
  });

  $: remainingSeconds = Math.max(0, estimatedSeconds - elapsedSeconds);
</script>

<!-- Full-screen overlay for mobile focus -->
<div class="processing-overlay">
  <div class="processing-content">
    <!-- Large visual spinner -->
    <div class="spinner-container">
      <div class="spinner"></div>
      <div class="spinner-progress" style="--progress: {progress}%"></div>
    </div>

    <!-- AI processing message -->
    <h2 class="processing-title">
      🤖 {message}
    </h2>

    <!-- Progress indicator -->
    <div class="progress-info">
      <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%"></div>
      </div>
      <div class="progress-text">
        {Math.round(progress)}% complete
      </div>
    </div>

    <!-- Time estimate -->
    {#if remainingSeconds > 0}
      <div class="time-estimate">
        Estimated time: {remainingSeconds}s remaining
      </div>
    {/if}

    <!-- Helpful tips while waiting -->
    <div class="processing-tips">
      <p>💡 <strong>Tip:</strong> Better photos = better results</p>
      <p>📱 Keep the app open for real-time updates</p>
    </div>
  </div>
</div>

<style>
  .processing-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
  }

  .processing-content {
    text-align: center;
    max-width: 400px;
    width: 100%;
  }

  .spinner-container {
    position: relative;
    width: 120px;
    height: 120px;
    margin: 0 auto 2rem;
  }

  .spinner {
    width: 100%;
    height: 100%;
    border: 8px solid #E5E7EB;
    border-radius: 50%;
    animation: spin 2s linear infinite;
  }

  .spinner-progress {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 8px solid transparent;
    border-top-color: #2563EB;
    border-radius: 50%;
    transform: rotate(calc(var(--progress) * 3.6deg - 90deg));
    transition: transform 0.5s ease;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .processing-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1.5rem;
    line-height: 1.4;
  }

  .progress-info {
    margin-bottom: 1rem;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #E5E7EB;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2563EB, #7C3AED);
    border-radius: 4px;
    transition: width 0.5s ease;
  }

  .progress-text {
    font-weight: 600;
    color: #2563EB;
  }

  .time-estimate {
    color: #6B7280;
    margin-bottom: 1.5rem;
    font-variant-numeric: tabular-nums;
  }

  .processing-tips {
    background: #F3F4F6;
    border-radius: 8px;
    padding: 1rem;
    text-align: left;
  }

  .processing-tips p {
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #6B7280;
  }
</style>
```

### 4. Generated Listing Preview Component
**Purpose:** Display AI-generated content with confidence-based UX

```svelte
<!-- GeneratedListingPreview.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import ConfidenceIndicator from './ConfidenceIndicator.svelte';
  import ActionButton from './ActionButton.svelte';

  export let product: Product;
  export let isPublishing = false;

  const dispatch = createEventDispatcher<{
    publish: void;
    edit: void;
    regenerate: void;
  }>();

  $: content = product.generated_content;
  $: confidence = content?.confidence_overall || 0;
  $: primaryImage = product.images?.find(img => img.is_primary);

  // Determine flow based on confidence
  $: flowType = confidence > 0.85 ? 'quick_approval' : 'balanced_review';
  $: showPublishButton = confidence > 0.70;

  function handlePublish() {
    dispatch('publish');
  }

  function handleEdit() {
    dispatch('edit');
  }

  function handleRegenerate() {
    dispatch('regenerate');
  }
</script>

<div class="listing-preview">
  <!-- Primary product image -->
  {#if primaryImage}
    <div class="image-container">
      <img
        src={primaryImage.processed_url || primaryImage.original_url}
        alt={content?.title || 'Product'}
        class="product-image"
      />
      <ConfidenceIndicator
        confidence={confidence}
        position="top-right"
      />
    </div>
  {/if}

  <!-- Generated content display -->
  <div class="content-section">
    <!-- AI-generated title -->
    <h1 class="product-title">
      🤖 {content?.title || 'Generating title...'}
    </h1>

    <!-- Key details -->
    <div class="product-details">
      <div class="detail-item">
        <span class="label">Precio:</span>
        <span class="value price">
          ${content?.ml_price?.toLocaleString('es-AR') || 'Calculando...'}
        </span>
      </div>

      <div class="detail-item">
        <span class="label">Categoría:</span>
        <span class="value">
          {content?.ml_category_name || 'Detecting category...'}
        </span>
      </div>

      <div class="detail-item">
        <span class="label">Condición:</span>
        <span class="value">
          {content?.ml_condition || 'New'}
        </span>
      </div>
    </div>

    <!-- AI-generated description -->
    <div class="description-section">
      <h3 class="section-title">🤖 Description</h3>
      <p class="description">
        {content?.description || 'Generating description...'}
      </p>
    </div>

    <!-- Confidence and flow guidance -->
    <div class="confidence-section">
      <ConfidenceIndicator
        confidence={confidence}
        showDetails={true}
      />

      {#if flowType === 'quick_approval'}
        <div class="flow-message success">
          ✅ High confidence - Ready to publish!
        </div>
      {:else}
        <div class="flow-message warning">
          ⚠️ Review recommended - Check details before publishing
        </div>
      {/if}
    </div>
  </div>

  <!-- Action buttons - mobile optimized -->
  <div class="action-section">
    {#if showPublishButton}
      <ActionButton
        variant={flowType === 'quick_approval' ? 'primary' : 'secondary'}
        size="large"
        disabled={isPublishing}
        on:click={handlePublish}
      >
        {#if isPublishing}
          Publishing...
        {:else if flowType === 'quick_approval'}
          🚀 PUBLISH NOW
        {:else}
          📝 Publish Anyway
        {/if}
      </ActionButton>
    {/if}

    <ActionButton
      variant="outline"
      size="medium"
      on:click={handleEdit}
    >
      ✏️ Edit Details
    </ActionButton>

    <ActionButton
      variant="ghost"
      size="small"
      on:click={handleRegenerate}
    >
      🔄 Regenerate
    </ActionButton>
  </div>
</div>

<style>
  .listing-preview {
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .image-container {
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
    overflow: hidden;
  }

  .product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .content-section {
    padding: 1.5rem;
  }

  .product-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    line-height: 1.4;
  }

  .product-details {
    display: grid;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #F3F4F6;
  }

  .label {
    font-weight: 500;
    color: #6B7280;
  }

  .value {
    font-weight: 600;
    color: #374151;
  }

  .price {
    color: #059669;
    font-size: 1.1rem;
  }

  .description-section {
    margin-bottom: 1.5rem;
  }

  .section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
  }

  .description {
    color: #6B7280;
    line-height: 1.6;
  }

  .confidence-section {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #F9FAFB;
    border-radius: 8px;
  }

  .flow-message {
    margin-top: 0.5rem;
    padding: 0.5rem;
    border-radius: 6px;
    font-weight: 500;
    text-align: center;
  }

  .flow-message.success {
    background: #D1FAE5;
    color: #065F46;
    border: 1px solid #A7F3D0;
  }

  .flow-message.warning {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
  }

  .action-section {
    padding: 1.5rem;
    background: #F9FAFB;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  /* Mobile-specific optimizations */
  @media (max-width: 480px) {
    .listing-preview {
      border-radius: 0;
      box-shadow: none;
    }

    .content-section,
    .action-section {
      padding: 1rem;
    }

    .product-title {
      font-size: 1.125rem;
    }
  }
</style>
```

---

## State Management Architecture

### Svelte Stores Structure
```typescript
// stores/products.ts
import { writable, derived } from 'svelte/store';
import type { Product, ProductStatus } from '$lib/types/product';

interface ProductsState {
  items: Record<string, Product>;
  currentProductId: string | null;
  loading: boolean;
  error: string | null;
}

function createProductsStore() {
  const { subscribe, set, update } = writable<ProductsState>({
    items: {},
    currentProductId: null,
    loading: false,
    error: null
  });

  return {
    subscribe,

    // Load products list
    async loadProducts() {
      update(state => ({ ...state, loading: true, error: null }));

      try {
        const response = await fetch('/api/v1/products');
        const data = await response.json();

        const items = data.products.reduce((acc, product) => {
          acc[product.id] = product;
          return acc;
        }, {});

        update(state => ({
          ...state,
          items,
          loading: false
        }));
      } catch (error) {
        update(state => ({
          ...state,
          error: error.message,
          loading: false
        }));
      }
    },

    // Create new product
    async createProduct(promptText: string, images: File[]) {
      const formData = new FormData();
      formData.append('prompt_text', promptText);
      images.forEach(image => formData.append('images[]', image));

      const response = await fetch('/api/v1/products', {
        method: 'POST',
        body: formData
      });

      const product = await response.json();

      update(state => ({
        ...state,
        items: { ...state.items, [product.id]: product },
        currentProductId: product.id
      }));

      return product;
    },

    // Update product status (from WebSocket)
    updateProductStatus(productId: string, status: ProductStatus) {
      update(state => ({
        ...state,
        items: {
          ...state.items,
          [productId]: {
            ...state.items[productId],
            status
          }
        }
      }));
    },

    // Set current product
    setCurrentProduct(productId: string | null) {
      update(state => ({ ...state, currentProductId: productId }));
    }
  };
}

export const productsStore = createProductsStore();

// Derived stores
export const currentProduct = derived(
  productsStore,
  ($products) => $products.currentProductId
    ? $products.items[$products.currentProductId]
    : null
);

export const productsList = derived(
  productsStore,
  ($products) => Object.values($products.items)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
);
```

### Real-time WebSocket Store
```typescript
// stores/realtime.ts
import { writable } from 'svelte/store';

interface RealtimeState {
  connected: boolean;
  reconnectAttempts: number;
  subscriptions: Record<string, WebSocket>;
}

function createRealtimeStore() {
  const { subscribe, update } = writable<RealtimeState>({
    connected: false,
    reconnectAttempts: 0,
    subscriptions: {}
  });

  function connectToProduct(productId: string, onMessage: (data: any) => void) {
    const wsUrl = `ws://localhost:8000/ws/products/${productId}/status`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      update(state => ({
        ...state,
        connected: true,
        reconnectAttempts: 0,
        subscriptions: { ...state.subscriptions, [productId]: ws }
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onclose = () => {
      update(state => {
        const { [productId]: removed, ...subscriptions } = state.subscriptions;
        return {
          ...state,
          subscriptions,
          connected: Object.keys(subscriptions).length > 0
        };
      });

      // Auto-reconnect logic
      setTimeout(() => {
        update(state => ({ ...state, reconnectAttempts: state.reconnectAttempts + 1 }));
        if (state.reconnectAttempts < 3) {
          connectToProduct(productId, onMessage);
        }
      }, 1000 * Math.pow(2, state.reconnectAttempts));
    };

    return () => ws.close();
  }

  return {
    subscribe,
    connectToProduct,

    disconnect(productId: string) {
      update(state => {
        const ws = state.subscriptions[productId];
        if (ws) {
          ws.close();
          const { [productId]: removed, ...subscriptions } = state.subscriptions;
          return { ...state, subscriptions };
        }
        return state;
      });
    }
  };
}

export const realtimeStore = createRealtimeStore();
```

---

## Mobile-First Routing Strategy

### SvelteKit Page Structure
```typescript
// routes/+layout.svelte - Global mobile layout
<script lang="ts">
  import { page } from '$app/stores';
  import MobileNavigation from '$lib/components/core/MobileNavigation.svelte';
  import LoadingIndicator from '$lib/components/ui/LoadingIndicator.svelte';
  import { productsStore } from '$lib/stores/products';

  // Global loading state
  $: isLoading = $productsStore.loading;
</script>

<!-- Mobile-optimized app shell -->
<div class="app-container">
  <header class="app-header">
    <h1>IntelliPost AI</h1>
    {#if isLoading}
      <LoadingIndicator size="small" />
    {/if}
  </header>

  <main class="app-main">
    <slot />
  </main>

  <MobileNavigation currentRoute={$page.route.id} />
</div>

<style>
  .app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #F9FAFB;
  }

  .app-header {
    background: white;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .app-main {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 80px; /* Space for mobile navigation */
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .app-main {
      padding: 0;
    }
  }
</style>
```

### Key Route Implementations
```svelte
<!-- routes/products/new/+page.svelte - Photo capture flow -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import PhotoCollectionComponent from '$lib/components/product/PhotoCollectionComponent.svelte';
  import PromptInputComponent from '$lib/components/product/PromptInputComponent.svelte';
  import { productsStore } from '$lib/stores/products';

  let images: ImageData[] = [];
  let promptText = '';
  let isCreating = false;

  $: canSubmit = images.length > 0 && promptText.trim().length >= 10;

  async function handleSubmit() {
    if (!canSubmit) return;

    isCreating = true;

    try {
      const imageFiles = images.map(img => img.file);
      const product = await productsStore.createProduct(promptText, imageFiles);

      // Navigate to processing view
      await goto(`/products/${product.id}`);
    } catch (error) {
      console.error('Failed to create product:', error);
      // Handle error state
    } finally {
      isCreating = false;
    }
  }
</script>

<div class="new-product-page">
  <div class="step-indicator">
    <span class="step active">1. Photos</span>
    <span class="step active">2. Description</span>
    <span class="step">3. Review</span>
  </div>

  <PhotoCollectionComponent
    bind:images
    on:imagesChange={() => images = images}
  />

  <PromptInputComponent
    bind:value={promptText}
    required={true}
    minLength={10}
  />

  <div class="submit-section">
    <button
      class="submit-btn"
      class:disabled={!canSubmit}
      disabled={!canSubmit || isCreating}
      on:click={handleSubmit}
    >
      {#if isCreating}
        Creating...
      {:else}
        🚀 Generate Listing
      {/if}
    </button>
  </div>
</div>

<style>
  .new-product-page {
    padding: 1rem;
    max-width: 600px;
    margin: 0 auto;
  }

  .step-indicator {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2rem;
    padding: 0 1rem;
  }

  .step {
    font-size: 0.875rem;
    color: #9CA3AF;
  }

  .step.active {
    color: #2563EB;
    font-weight: 600;
  }

  .submit-section {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #E5E7EB;
  }

  .submit-btn {
    width: 100%;
    padding: 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    min-height: 56px;
  }

  .submit-btn.disabled {
    background: #9CA3AF;
    cursor: not-allowed;
  }
</style>
```

---

**Esta arquitectura frontend cubre los componentes críticos MVP con optimización mobile-first. ¿Continuamos con External Integrations o quieres revisar algún componente específico?**
